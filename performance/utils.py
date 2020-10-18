from .models import Steps, StepConfiguration


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

