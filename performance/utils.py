from .models import Group, Vara, StepConfiguration, Comments, Steps
from .serializers import GroupSerializer, VaraSerializer, VaraDetailsSerializer, VaraListSerializer,\
    StepConfigurationSerializer, CommentsSerializer, StepsSerializer
from django.db.models import Avg, StdDev


def create_graph_dict(vara_id, is_time=1):
    graph = {'identificador_vara':vara_id,
             'root':'Distribuição',
             'arestas':[]}
    
    steps = Steps.objects.filter(vara_id=vara_id)

    for s in steps:
        stepConfig = s.step_id
        
        if is_time == 1:
            weight = s.med_time
        else:
            weight = s.frequency

        edge = {'origem':stepConfig.origin,
                'destino':stepConfig.destination,
                'weight':weight
                }
        graph['arestas'].append(edge)
    
    return graph


def best_varas_on_step_aux(step_id, vara_id, amount_of_varas):
    my_vara = Vara.objects.get(vara_id=vara_id)
    my_vara_group = my_vara.group_id
    varas_in_group = Vara.objects.filter(group_id=my_vara_group)

    # print('varas_list: ', str(varas_list))

    all_step_objects = Steps.objects.\
        filter(step_id=step_id, vara_id__in=varas_in_group).\
            order_by('med_time')

    # print('all_step_objects: ', str(all_step_objects))

    first_objs = all_step_objects[:max(amount_of_varas - 5, 1)]
    focused_vara_index = list(all_step_objects.all()).\
        index(Steps.objects.get(step_id=step_id,vara_id=vara_id))
    min_index_to_get = max(0, focused_vara_index-2)
    max_index_to_get = focused_vara_index + 3
    last_objs = all_step_objects[min_index_to_get:max_index_to_get]
    objs = first_objs.union(last_objs).distinct()
    if amount_of_varas > len(objs):
        objs = objs.union(all_step_objects[:amount_of_varas]).distinct()

    objs = objs.order_by('med_time')

    res_steps = []
    for step in objs.all():
        step_dict = StepsSerializer(step).data
        res_dict = {
            'vara_id': step_dict['vara_id'],
            'med_time': step_dict['med_time']
        }
        # Get vara info
        vara_obj = Vara.objects.get(vara_id=res_dict['vara_id'])
        vara = VaraSerializer(vara_obj).data
        res_dict['vara_name'] = vara['name']
        # Get comment info
        comment_obj = Comments.objects.get(comment_id=step_dict['comment_id'])
        comment = CommentsSerializer(comment_obj).data
        res_dict['comment'] = comment['comment']
        # res_dict['comment'] = "Meu comentário fixo"
        res_steps.append(res_dict)
    
    return res_steps


def find_ranking(res, vara_id):
    count = 1
    
    for el in res:
        # print(el)
        # print('el[vara]: ', str(el['vara_id']))
        # print('vara_id: ', str(vara_id))
        if int(el['vara_id']) == int(vara_id):
            # print('###### encontrou')
            return count
        count += 1
    
    return None


def find_outliers_group(group_id):
    outliers = []
    varas_in_group = Vara.objects.filter(group_id=group_id)

    mean = varas_in_group.\
        aggregate(Avg('days_finish_process'))['days_finish_process__avg']
    
    std_dev = varas_in_group.\
        aggregate(StdDev('days_finish_process'))['days_finish_process__stddev']

    upper_bound = mean + 1.5 * std_dev

    varas_em_alerta = varas_in_group.\
        filter(days_finish_process__gte = upper_bound)

    # for vara in varas_em_alerta:
    #     outliers.append({"identificador": vara.vara_id,
    #                      "nome": vara.name,
    #                      "tempo": vara.days_finish_process})

    outliers = [vara.vara_id for vara in varas_em_alerta]

    return outliers


def __get_best_steps__(vara_id: int, amount_of_steps: int = 10):
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


def __get_worst_steps__(vara_id: int, amount_of_steps: int = 10):
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


def __get_best_ujs__(group_id: int, amount_of_varas: int) -> list:
    all_uj_obj_list = Vara.objects.filter(group_id=group_id).order_by('days_finish_process')
    if amount_of_varas > 0:
        all_uj_obj_list = all_uj_obj_list[:amount_of_varas]
    all_uj_obj_list = all_uj_obj_list.order_by('days_finish_process')

    res_list = []
    for uj_obj in all_uj_obj_list.all():
        uj = VaraSerializer(uj_obj).data
        uj['tribunal'] = uj['name'][-4:]
        # uj['best_steps'] = __get_best_steps__(uj['vara_id'], 1)
        # uj['worst_steps'] = __get_worst_steps__(uj['vara_id'], 1)
        res_list.append(uj)
    return res_list


def __get_worst_ujs__(group_id: int, amount_of_varas: int) -> list:
    all_uj_obj_list = Vara.objects.filter(group_id=group_id).order_by('days_finish_process')
    if amount_of_varas > 0:
        all_uj_obj_list = all_uj_obj_list[-amount_of_varas:]
    all_uj_obj_list = all_uj_obj_list.order_by('days_finish_process')

    res_list = []
    for uj_obj in all_uj_obj_list.all():
        uj = VaraSerializer(uj_obj).data
        uj['tribunal'] = uj['name'][-4:]
        # uj['best_steps'] = __get_best_steps__(uj['vara_id'], 1)
        # uj['worst_steps'] = __get_worst_steps__(uj['vara_id'], 1)
        res_list.append(uj)
    return res_list


def __get_amount_alerted_ujs__(group_id: int) -> int:
    return len(find_outliers_group(group_id))


def __get_group_med_time__(group_id: int) -> int:
    uj_objs = Vara.objects.filter(group_id=group_id).all()
    avg_time = uj_objs.aggregate(tempo_medio=Avg('days_finish_process'))
    return avg_time['tempo_medio']

