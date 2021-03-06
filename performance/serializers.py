from rest_framework import serializers
from .models import Group, Vara, VaraList, StepConfiguration, Comments, Steps


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group_id',
                  'group_name',
                  'competences',
                  'justice',
                  'grade',
                  'court',
                  'court_class',
                  'subject',
                  'judging_body',
                  'amount_of_varas']

class VaraListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaraList
        fields = ['vara_id', 'name']

class VaraDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vara
        fields = ['vara_id',
                  'name',
                  'ranking',
                  'finished_processes',
                  'movements',
                  'days_finish_process',
                  'group_id']

class VaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vara
        fields = ['vara_id',
                  'name',
                  'finished_processes',
                  'movements',
                  'time_distribuicao',
                  'time_conclusao',
                  'time_despacho',
                  'time_decisao',
                  'time_julgamento',
                  'time_transito_em_julgado',
                  'time_baixa_ou_arquivamento',
                  'time_audiencia',
                  'time_citacao',
                  'time_outros',
                  'days_finish_process',
                  'latitude',
                  'longitude']

class StepConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
      model = StepConfiguration
      fields = ['step_id', 'origin', 'destination']

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
      model = Comments
      fields = ['comment_id', 'comment']

class StepsSerializer(serializers.ModelSerializer):
    class Meta:
      model = Steps
      fields = ['step_id',
                'vara_id',
                'min_time',
                'med_time',
                'max_time',
                'frequency',
                'comment_id']

class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group_id',
                  'group_name',
                  'amount_of_varas',
                  'frequent_subjects',
                  'frequent_classes']

class GroupDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group_id',
                  'group_name',
                  'amount_of_varas']
