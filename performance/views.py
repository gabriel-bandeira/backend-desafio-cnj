from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Group, Vara, StepConfiguration, Comments, Steps
from .serializers import GroupSerializer, GroupListSerializer, VaraSerializer, VaraDetailsSerializer, \
    VaraListSerializer, CommentsSerializer, GroupDetailsSerializer
from .utils import create_graph_dict, best_varas_on_step_aux, __get_best_steps__, __get_worst_steps__,\
    __get_best_ujs__, __get_amount_alerted_ujs__, __get_group_med_time__, find_outliers_group,\
    __get_group_ujs_over_med_time__

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
        vara_res['tribunal'] = vara_res['name'][-4:]
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
@api_view(["POST"])
@permission_classes((AllowAny,))
def create_comment(request):
    try:
        vara_id = request.data.get("vara_id")
        step_id = request.data.get("step_id")
        comment = request.data.get("comment")

        step = Steps.objects.get(step_id=step_id, vara_id=vara_id)
        new_comment = Comments(comment=comment)
        new_comment.save()
        step.comment_id = new_comment
        step.save()

        return Response('success', HTTP_200_OK)

    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def get_my_comment(request):
    try:
        step_id = request.GET.get('step_id', None)
        vara_id = request.GET.get('vara_id', None)
        step = Steps.objects.get(step_id=step_id, vara_id=vara_id)
        my_comment = step.comment_id
        res = CommentsSerializer(my_comment).data

        return Response(res, HTTP_200_OK)

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
        # optional filters
        justica = request.GET.get('justica', None)
        grau = request.GET.get('grau', None)
        classe_processual = request.GET.get('classe_processual', None)

        # get list of groups and insert selected filters
        all_groups_obj_list = Group.objects
        if justica is not None:
            all_groups_obj_list = all_groups_obj_list.filter(justica=justica)
        if grau is not None:
            all_groups_obj_list = all_groups_obj_list.filter(grau=grau)
        if classe_processual is not None:
            all_groups_obj_list = all_groups_obj_list.filter(classe_processual=classe_processual)
        all_groups_obj_list = all_groups_obj_list.order_by('group_id')

        res_list = []
        for group_obj in all_groups_obj_list.all():
            # get group info
            group = GroupListSerializer(group_obj).data

            # add calculated info
            group.update({'varas': __get_best_ujs__(group_id=group['group_id'], amount_of_varas=-1)})
            group.update({'varas_em_alerta': __get_amount_alerted_ujs__(group['group_id'])})

            # rename columns
            group['identificador'] = group.pop("group_id")
            group['total_varas'] = group.pop("amount_of_varas")
            group['assuntos_frequentes'] = group.pop("frequent_subjects")
            group['classes_frequentes'] = group.pop("frequent_classes")

            # append response object
            res_list.append(group)
        return Response(res_list, HTTP_200_OK)
    except Group.DoesNotExist as e:
        return Response('Error getting grupo. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


# Grupos
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def grupo_details(request, group_id):
    try:
        # get list of groups and insert selected filters
        group_obj = Group.objects.get(group_id=group_id)

        # get group info
        group = GroupDetailsSerializer(group_obj).data

        # add calculated info
        group.update({'tempo_medio': __get_group_med_time__(group['group_id'])})
        # group.update({'tempoOutrasVaras': __get_group_ujs_over_med_time__(group['group_id'])})
        group.update({'varas': __get_best_ujs__(group_id=group['group_id'], amount_of_varas=-1)})
        group.update({'varasEmAlerta': find_outliers_group(group['group_id'])})

        # rename columns
        group['identificador'] = group.pop("group_id")
        group['numero_varas'] = group.pop("amount_of_varas")
        # group['assuntos_frequentes'] = group.pop("frequent_subjects")
        # group['classes_frequentes'] = group.pop("frequent_classes")

        return Response(group, HTTP_200_OK)
    except Group.DoesNotExist as e:
        return Response('Error getting group. ' + str(e), HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), HTTP_400_BAD_REQUEST)


