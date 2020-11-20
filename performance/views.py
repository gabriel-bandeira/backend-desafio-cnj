from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Group, Vara, StepConfiguration, Comments, Steps
from .serializers import GroupSerializer, VaraSerializer, VaraDetailsSerializer, VaraListSerializer,\
    StepConfigurationSerializer, CommentsSerializer, StepsSerializer
from .utils import create_graph_dict, best_varas_on_step_aux, \
    find_ranking

from rest_framework.response import Response
from rest_framework.decorators import api_view, \
                                      permission_classes
from rest_framework.status import HTTP_400_BAD_REQUEST, \
                                  HTTP_404_NOT_FOUND, \
                                  HTTP_200_OK
from rest_framework.permissions import AllowAny



# Home
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def home(request):
    return Response('Backend is running fine', HTTP_200_OK)


# Support functions
def __get_best_steps__(vara_id:int, amount_of_steps:int =10):
    step_objects = Steps.objects.filter(vara_id=vara_id).order_by('med_time')[:amount_of_steps]
    res_steps = []
    for step in step_objects.all():
        step_dict = StepsSerializer(step).data

        my_res_steps = best_varas_on_step_aux(step_dict['step_id'], 
                                           vara_id, 
                                           amount_of_varas=60)

                            
        ranking = find_ranking(my_res_steps, vara_id)

        # print('### res_steps: ', str(res_steps))
        # print('ranking: ', str(ranking))
        # print('vara_id: ', str(vara_id))

        res_dict = {
            'step_id': step_dict['step_id'],
            'med_time': step_dict['med_time'],
            'frequency': step_dict['frequency'],
            'ranking': ranking
        }
        # Get step info
        step_config_obj = StepConfiguration.objects.get(step_id=res_dict['step_id'])
        step_config = StepConfigurationSerializer(step_config_obj).data
        res_dict['origin'] = step_config['origin']
        res_dict['destination'] = step_config['destination']
        res_steps.append(res_dict)
    return res_steps


def __get_worst_steps__(vara_id:int, amount_of_steps:int = 10):
    step_objects = Steps.objects.filter(vara_id=vara_id).order_by('-med_time')[:amount_of_steps]
    res_steps = []
    for step in step_objects.all():
        step_dict = StepsSerializer(step).data

        my_res_steps = best_varas_on_step_aux(step_dict['step_id'], 
                                              vara_id, 
                                              amount_of_varas=60)

        ranking = find_ranking(my_res_steps, vara_id)

        res_dict = {
            'step_id': step_dict['step_id'],
            'med_time': step_dict['med_time'],
            'frequency': step_dict['frequency'],
            'ranking': ranking
        }
        # Get step info
        step_config_obj = StepConfiguration.objects.get(step_id=res_dict['step_id'])
        step_config = StepConfigurationSerializer(step_config_obj).data
        res_dict['origin'] = step_config['origin']
        res_dict['destination'] = step_config['destination']
        res_steps.append(res_dict)
    return res_steps



# Varas
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def varas_list(request):
    try:
        vara_list = Vara.objects.all()
        res = [VaraListSerializer(vr).data for vr in vara_list]
        return Response(res, HTTP_200_OK)
    except Vara.DoesNotExist as e:
        return Response(str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def vara_details(request, vara_id):
    try:
        vara = Vara.objects.get(vara_id=vara_id)
        vara_res = VaraDetailsSerializer(vara).data
        group_id = vara_res['group_id']
        group = Group.objects.get(group_id=group_id)
        group_res = GroupSerializer(group).data
        vara_res['group'] = group_res
        vara_res.pop('group_id')
        vara_res['best_steps'] = __get_best_steps__(vara_id, 10)
        vara_res['worst_steps'] = __get_worst_steps__(vara_id, 10)
        return Response(vara_res, HTTP_200_OK)
    except Vara.DoesNotExist as e:
        return Response(str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def best_varas_on_step(request):
    try:
        step_id = request.GET.get('step_id', None)
        vara_id = request.GET.get('vara_id', None)

        # print('step_id: ', str(step_id))
        # print('vara_id: ', str(vara_id))


        amount_of_varas = int(request.GET.get('amount_of_varas', 10))

        res_steps = best_varas_on_step_aux(step_id, vara_id, amount_of_varas)
        
        return Response(res_steps, HTTP_200_OK)
    except Steps.DoesNotExist as e:
        return Response('Error getting steps. ' + str(e), HTTP_404_NOT_FOUND)
    except Vara.DoesNotExist as e:
        return Response('Error getting vara. ' + str(e), HTTP_404_NOT_FOUND)
    except Comments.DoesNotExist as e:
        return Response('Error getting comment. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


# Etapas
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def best_steps(request):
    try:
        vara_id = request.GET.get('vara_id', None)
        amount_of_steps = int(request.GET.get('amount_of_steps', 10))
        res_steps = __get_best_steps__(vara_id, amount_of_steps)
        return Response(res_steps, HTTP_200_OK)
    except Steps.DoesNotExist as e:
        return Response('Error getting steps. ' + str(e), HTTP_404_NOT_FOUND)
    except StepConfiguration.DoesNotExist as e:
        return Response('Error getting step configuration. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def worst_steps(request):
    try:
        vara_id = request.GET.get('vara_id', None)
        amount_of_steps = int(request.GET.get('amount_of_steps', 10))
        res_steps = __get_worst_steps__(vara_id, amount_of_steps)
        return Response(res_steps, HTTP_200_OK)
    except Steps.DoesNotExist as e:
        return Response('Error getting steps. ' + str(e), HTTP_404_NOT_FOUND)
    except StepConfiguration.DoesNotExist as e:
        return Response('Error getting step configuration. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


# Processos
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def best_varas(request):
    try:
        vara_id = request.GET.get('vara_id', None)
        amount_of_varas = int(request.GET.get('amount_of_varas', 10))

        my_vara = Vara.objects.get(vara_id=vara_id)
        my_vara_group = my_vara.group_id

        all_vara_obj_list = Vara.objects.filter(group_id=my_vara_group).\
            order_by('days_finish_process')
        first_objs = all_vara_obj_list[:max(amount_of_varas - 5, 1)]
        focused_vara_index = list(all_vara_obj_list.all()).index(Vara.objects.get(vara_id=vara_id))
        min_index_to_get = max(0, focused_vara_index-2)
        max_index_to_get = focused_vara_index + 3
        last_objs = all_vara_obj_list[min_index_to_get:max_index_to_get]
        objs = first_objs.union(last_objs).distinct()
        if amount_of_varas > len(objs):
            objs = objs.union(all_vara_obj_list[:amount_of_varas]).distinct()

        objs = objs.order_by('days_finish_process')

        res_list = []
        for vara_obj in objs.all():
            vara = VaraSerializer(vara_obj).data
            res_list.append(vara)
        return Response(res_list, HTTP_200_OK)
    except Vara.DoesNotExist as e:
        return Response('Error getting vara. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


# Comentarios
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def comments_list(request):
    try:
        comm_list = Comments.objects.all()
        res = [CommentsSerializer(cl).data for cl in comm_list]
        return Response(res, HTTP_200_OK)
    except Comments.DoesNotExist as e:
        return Response(str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def comment(request, comment_id):
    try:
        comm = Comments.objects.get(comment_id=comment_id)
        res = CommentsSerializer(comm).data
        return Response(res, HTTP_200_OK)
    except Comments.DoesNotExist as e:
        return Response(str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def graphs(request, vara_id, other_vara_id, is_time):
    try:
        vara_graph = create_graph_dict(vara_id=vara_id,
                                       is_time=is_time)
        other_vara_graph = create_graph_dict(vara_id=other_vara_id,
                                             is_time=is_time)
        return Response([vara_graph, other_vara_graph], HTTP_200_OK)
    except Vara.DoesNotExist as e:
       return Response(str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


# Grupos
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def grupos_list(request):
    try:
        # filtros opicionais
        justica = request.GET.get('justica', None)
        grau = request.GET.get('grau', None)
        classe_processual = request.GET.get('classe_processual', None)
        fake_data = \
            [
                {
                    "identificador": 20,
                    "total_varas": 51,
                    "varas_em_alerta": 2,
                    "assuntos_frequentes": [
                        {
                            "assunto": "Direito Civil",
                            "frequencia": 22.3
                        },
                        {
                            "assunto": "Direito da Saúde",
                            "frequencia": 31.3
                        },
                        {
                            "assunto": "Direito Penal",
                            "frequencia": 17.1
                        },

                    ],
                    "classes_frequentes": [
                        {
                            "classe": "Processo Cível e do Trabalho",
                            "frequencia": 35.9
                        },
                        {
                            "classe": "Processo Criminal",
                            "frequencia": 15.5
                        },
                        {
                            "classe": "Processo Eleitoral",
                            "frequencia": 10.7
                        },
                    ],
                    "varas": [
                        {
                            "nome": "Vara Única de Anajás",
                            "tempo": 1207,
                            "latitude": -8.12094,
                            "longitude": -34.73094
                        },
                        {
                            "nome": "1ª Vara TJBA",
                            "tempo": 956,
                            "latitude": -8.12094,
                            "longitude": -34.93094
                        },
                        {
                            "nome": "1ª Vara TJAC",
                            "tempo": 843,
                            "latitude": -9.12094,
                            "longitude": -35.23094
                        },
                    ]
                },
                {
                    "identificador": 21,
                    "total_varas": 15,
                    "varas_em_alerta": 0,
                    "assuntos_frequentes": [
                        {
                            "assunto": "Direito Assistencial",
                            "frequencia": 12.3
                        },
                        {
                            "assunto": "Direito Eleitoral",
                            "frequencia": 41.3
                        },

                    ],
                    "classes_frequentes": [
                        {
                            "classe": "Processo Eleitoral",
                            "frequencia": 65.9
                        }
                    ],
                    "varas": [
                        {
                            "nome": "Vara Única de Anajás",
                            "tempo": 654,
                            "latitude": -8.12094,
                            "longitude": -34.73094
                        },
                        {
                            "nome": "1ª Vara TJPA",
                            "tempo": 2300,
                            "latitude": -8.12094,
                            "longitude": -34.93094
                        },
                        {
                            "nome": "1ª Vara TJRN",
                            "tempo": 1980,
                            "latitude": -9.12094,
                            "longitude": -35.23094
                        },
                    ]
                }
            ]
        return Response(fake_data, HTTP_200_OK)
    except Group.DoesNotExist as e:
        return Response('Error getting grupo. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


# Grupos
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def grupo_details(request, grupo_id):
    try:
        fake_data = \
            {
                "identificador": 20,
                "numero_varas": 56,
                "tempo_medio": 1100,
                "tempoOutrasVaras": {
                    "nome": "Outras Unidades Judiciárias",
                    "tempo": 890
                },
                "varasEmAlerta": [
                    {
                    "identificador": 60,
                    "nome": "2ª de TJAC",
                    "tempo": 1544,
                    },
                    {
                    "identificador": 60,
                    "nome": "3ª de TJAC",
                    "tempo": 1607,
                    },
                    {
                    "identificador": 60,
                    "nome": "4ª de TJBA",
                    "tempo": 1699,
                    },
                ],
                "melhoresVaras": [
                    {
                        "identificador": 57,
                        "ranking": 1,
                        "nome": "Única de Roraima",
                        "tempo": 690,
                        "movimentos": 32,
                        "processos": 67,
                        "melhorEtapa": "Distribuição",
                        "piorEtapa": "Julgamento",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": 3.5,
                                "time_conclusao": 0.09,
                                "time_despacho": 49.35,
                                "time_decisao": 36.28,
                                "time_julgamento": 9.9,
                                "time_transito_em_julgado": 0,
                                "time_baixa_ou_arquivamento": 22.47,
                                "time_citacao": 0,
                                "time_audiencia": 0,
                                "time_outros": 0
                            }
                        ]
                    },
                    {
                        "identificador": 44,
                        "ranking": 2,
                        "nome": "1ª Vara de TJAL",
                        "tempo": 740,
                        "movimentos": 36,
                        "processos": 67,
                        "melhorEtapa": "Baixa/Arquivamento",
                        "piorEtapa": "Trânsito em julgado",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": -1,
                                "time_conclusao": 5.13,
                                "time_despacho": 54.61,
                                "time_decisao": -1,
                                "time_julgamento": 17.4,
                                "time_transito_em_julgado": -1,
                                "time_baixa_ou_arquivamento": 22.47,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": 0.39,
                            }
                        ]
                    },
                    {
                        "identificador": 33,
                        "ranking": 3,
                        "nome": "2ª Vara TJPB",
                        "tempo": 790,
                        "movimentos": 32,
                        "processos": 67,
                        "melhorEtapa": "Distribuição",
                        "piorEtapa": "Julgamento",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": -1,
                                "time_conclusao": 5.59,
                                "time_despacho": -1,
                                "time_decisao": 35.72,
                                "time_julgamento": 12.48,
                                "time_transito_em_julgado": 28.87,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": 17.34,
                            }
                        ]
                    },
                    {
                        "identificador": 34,
                        "ranking": 4,
                        "nome": "3ª Vara TJPB",
                        "tempo": 804,
                        "movimentos": 22,
                        "processos": 37,
                        "melhorEtapa": "Distribuição",
                        "piorEtapa": "Julgamento",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": 0.04,
                                "time_conclusao": 0.21,
                                "time_despacho": 30.33,
                                "time_decisao": 60.3,
                                "time_julgamento": 9.11,
                                "time_transito_em_julgado": -1,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": -1,
                            }
                        ]
                    },
                    {
                        "identificador": 22,
                        "ranking": 5,
                        "nome": "4ª Vara TJPB",
                        "tempo": 890,
                        "movimentos": 32,
                        "processos": 67,
                        "melhorEtapa": "Distribuição",
                        "piorEtapa": "Julgamento",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": 28.47,
                                "time_conclusao": 38.43,
                                "time_despacho": 18.26,
                                "time_decisao": -1,
                                "time_julgamento": 14.85,
                                "time_transito_em_julgado": -1,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": -1,
                            }
                        ]
                    },
                ],
                "pioresVaras": [
                    {
                        "identificador": 53,
                        "ranking": 52,
                        "nome": "1ª de TJRO",
                        "tempo": 1207,
                        "movimentos": 43,
                        "processos": 47,
                        "melhorEtapa": "Despacho",
                        "piorEtapa": "Audiência",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": -1,
                                "time_conclusao": 12.35,
                                "time_despacho": 23.99,
                                "time_decisao": -1,
                                "time_julgamento": 32.78,
                                "time_transito_em_julgado": 30.88,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": -1,
                            }
                        ]
                    },
                    {
                        "identificador": 54,
                        "ranking": 53,
                        "nome": "1ª de TJAC",
                        "tempo": 1307,
                        "movimentos": 43,
                        "processos": 47,
                        "melhorEtapa": "Conclusão",
                        "piorEtapa": "Audiência",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": -1,
                                "time_conclusao": 0.71,
                                "time_despacho": -1,
                                "time_decisao": 28.83,
                                "time_julgamento": 29.36,
                                "time_transito_em_julgado": 20.82,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": 20.28,
                            }
                        ]
                    },
                    {
                        "identificador": 53,
                        "ranking": 54,
                        "nome": "2ª de TJAC",
                        "tempo": 1544,
                        "movimentos": 43,
                        "processos": 47,
                        "melhorEtapa": "Conclusão",
                        "piorEtapa": "Despacho",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": 3.5,
                                "time_conclusao": 0.09,
                                "time_despacho": 49.35,
                                "time_decisao": 36.28,
                                "time_julgamento": 9.9,
                                "time_transito_em_julgado": 0,
                                "time_baixa_ou_arquivamento": 22.47,
                                "time_citacao": 0,
                                "time_audiencia": 0,
                                "time_outros": 0
                            }
                        ]
                    },
                    {
                        "identificador": 50,
                        "ranking": 55,
                        "nome": "3ª de TJAC",
                        "tempo": 1607,
                        "movimentos": 43,
                        "processos": 47,
                        "melhorEtapa": "Despacho",
                        "piorEtapa": "Audiência",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": 27.75,
                                "time_conclusao": 44.7,
                                "time_despacho": 14.19,
                                "time_decisao": -1,
                                "time_julgamento": 13.36,
                                "time_transito_em_julgado": -1,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": -1,
                            }
                        ]
                    },
                    {
                        "identificador": 49,
                        "ranking": 56,
                        "nome": "4ª de TJBA",
                        "tempo": 1699,
                        "movimentos": 43,
                        "processos": 47,
                        "melhorEtapa": "Conclusão",
                        "piorEtapa": "Audiência",
                        "porcentagemMacroetapas": [
                            {
                                "time_distribuicao": -1,
                                "time_conclusao": 25.43,
                                "time_despacho": -1,
                                "time_decisao": -1,
                                "time_julgamento": 41.36,
                                "time_transito_em_julgado": -1,
                                "time_baixa_ou_arquivamento": -1,
                                "time_audiencia": -1,
                                "time_citacao": -1,
                                "time_outros": 33.21,
                            }
                        ]
                    },
                ]
            }
        return Response(fake_data, HTTP_200_OK)
    except Group.DoesNotExist as e:
        return Response('Error getting grupo. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)

