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

    for vara in varas_em_alerta:
        outliers.append({"identificador": vara.vara_id,
                         "nome": vara.name,
                         "tempo": vara.days_finish_process})

    return outliers

