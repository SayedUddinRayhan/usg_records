from django.db import models


class Report(models.Model):
    id_number = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    type_of_usg = models.CharField(max_length=50, choices=[('Normal','Normal'),('Special','Special')], default='Normal')
    referred_by = models.CharField(max_length=200)
    sonologist = models.CharField(max_length=200)
    total_ultra = models.PositiveSmallIntegerField(default=1)

    patient_name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['-date']
        indexes = [models.Index(fields=['date','referred_by','sonologist'])]


    def __str__(self):
        return f"{self.id_number or self.pk} - {self.date} - {self.referred_by}"



