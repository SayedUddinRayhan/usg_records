from django.db import models

class Report(models.Model):
    id_number = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()

    exam_name = models.ForeignKey(
        'masterdata.ExamName',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )

    EXAM_TYPE_CHOICES = [
        ('Normal', 'Normal'),
        ('Special', 'Special'),
    ]
   
    exam_type = models.CharField(max_length=50, choices=EXAM_TYPE_CHOICES, default='Normal')

    def get_self_referrer():
        from masterdata.models import Referrer
        return Referrer.objects.get_or_create(name='Self')[0].pk 
    
    referred_by = models.ForeignKey(
        'masterdata.Referrer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        default=get_self_referrer
    )

    sonologist = models.ForeignKey(
        'masterdata.Sonologist',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )

    TOTAL_ULTRA_CHOICES = [
        (1, '1'),
        (2, '2'),
    ]
    total_ultra = models.PositiveSmallIntegerField(choices=TOTAL_ULTRA_CHOICES, default=1)

    patient_name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']
        indexes = [models.Index(fields=['date'])]

    def __str__(self):
        exam = self.exam_name.name if self.exam_name else "—"
        referred = self.referred_by.name if self.referred_by else "—"
        return f"{self.id_number or self.pk} - {self.date} - {referred} - {exam}"