from django.db import models


class Group(models.Model):
    group_id = models.BigIntegerField(primary_key=True)

    competences = models.IntegerField(default=None)
    justice = models.TextField(max_length=255, blank=False, default=None)
    grade = models.TextField(max_length=255, blank=False, default=None)
    court = models.TextField(max_length=255, null=True, default=None)
    court_class = models.TextField(max_length=255, null=True, default=None)
    subject = models.TextField(max_length=255, blank=False, default=None)
    judging_body = models.TextField(max_length=255, null=True, default=None)
    method = models.TextField(max_length=255, null=True, default=None)

    amount_of_varas = models.IntegerField(default=None)

    frequent_subjects = models.JSONField(null=True)
    frequent_classes = models.JSONField(null=True)


# adicionar tribunal
class Vara(models.Model):
    vara_id = models.BigIntegerField(primary_key=True)
    name = models.TextField(max_length=255, blank=False, default=None)

    ranking = models.IntegerField(default=None, null=True)
    finished_processes = models.IntegerField(default=None)
    movements = models.IntegerField(default=None)

    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)

    time_distribuicao = models.FloatField(default=None, null=True)
    time_conclusao = models.FloatField(default=None, null=True)
    time_despacho = models.FloatField(default=None, null=True)
    time_decisao = models.FloatField(default=None, null=True)
    time_julgamento = models.FloatField(default=None, null=True)
    time_transito_em_julgado = models.FloatField(default=None, null=True)
    time_baixa_ou_arquivamento = models.FloatField(default=None, null=True)
    time_audiencia = models.FloatField(default=None, null=True)
    time_citacao = models.FloatField(default=None, null=True)
    time_outros = models.FloatField(default=None, null=True)

    days_finish_process = models.IntegerField(default=None)

    latitude = models.FloatField(default=None, null=True)
    longitude = models.FloatField(default=None, null=True)


class VaraList(models.Model):
    vara_id = models.ForeignKey(Vara, on_delete=models.CASCADE)
    name = models.TextField(max_length=255, blank=False, default=None)


class StepConfiguration(models.Model):
  step_id = models.BigIntegerField(primary_key=True)
  origin = models.TextField(max_length=255, blank=False, default=None)
  destination = models.TextField(max_length=255, blank=False, default=None)


class Comments(models.Model):
  comment_id = models.BigIntegerField(primary_key=True)
  comment = models.TextField(max_length=500, blank=False, default=None)


class Steps(models.Model):
  step_id = models.ForeignKey(StepConfiguration, on_delete=models.CASCADE)
  vara_id = models.ForeignKey(Vara, on_delete=models.CASCADE)
  min_time = models.IntegerField(default=None, null=True)
  med_time = models.IntegerField(default=None)
  max_time = models.IntegerField(default=None, null=True)
  frequency = models.IntegerField(default=None)
  comment_id = models.ForeignKey(Comments, on_delete=models.CASCADE, null=True)

