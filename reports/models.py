from django.db import models


class Report(models.Model):
    # 1) Patient ID
    id_number = models.CharField(max_length=100, blank=True, null=True)

    # 2) Date
    date = models.DateField()

    # 3) Exam Name
    EXAM_NAME_CHOICES = [
        ('Whole Abdomen', 'Whole Abdomen'),
        ('Whole Abdomen with Pregnancy', 'Whole Abdomen with Pregnancy'),
        ('Lower Abdomen', 'Lower Abdomen'),
        ('HBS', 'HBS'),
        ('Pregnancy Profile', 'Pregnancy Profile'),
        ('Pregnancy Profile twin', 'Pregnancy Profile twin'),
        ('Anomaly Scan', 'Anomaly Scan'),
        ('Fetal Doppler Study', 'Fetal Doppler Study'),
        ('Thyroid/Neck', 'Thyroid/Neck'),
        ('Testes/ISR', 'Testes/ISR'),
        ('Swelling', 'Swelling'),
    ]

    exam_name = models.CharField(
        max_length=100,
        choices=EXAM_NAME_CHOICES,
        default='Abdomen'
    )

    # 4) Exam Type (Normal / Special)
    EXAM_TYPE_CHOICES = [
        ('Normal', 'Normal'),
        ('Special', 'Special'),
    ]
    exam_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPE_CHOICES,
        default='Normal'
    )

    # 5) Referred by (full doctor list)
    REFERRED_BY_CHOICES = [
        ('Prof. Dr. Mahbubul Islam Majumder', 'Prof. Dr. Mahbubul Islam Majumder'),
        ('Prof. Dr. Samsun Nahar', 'Prof. Dr. Samsun Nahar'),
        ('Prof. Dr. Haroon-Or-Rashid', 'Prof. Dr. Haroon-Or-Rashid'),
        ('Dr. Belal Hossain', 'Dr. Belal Hossain'),
        ('Prof. Dr. Md. Safiqur Rahman Patwary', 'Prof. Dr. Md. Safiqur Rahman Patwary'),
        ('Prof. Dr. Nasir Uddin Mahmud', 'Prof. Dr. Nasir Uddin Mahmud'),
        ('Dr. Mahfuzur Rahman (EMON)', 'Dr. Mahfuzur Rahman (EMON)'),
        ('Dr. Hasan Imam (Sany)', 'Dr. Hasan Imam (Sany)'),
        ('Dr. Joynal Abedin', 'Dr. Joynal Abedin'),
        ('Dr. Md. Mainul Hasan Sohel', 'Dr. Md. Mainul Hasan Sohel'),
        ('Dr. Kawsar Hamid', 'Dr. Kawsar Hamid'),
        ('Dr. Mostaque Ahmad', 'Dr. Mostaque Ahmad'),
        ('Dr. Shamsul Islam (Bokol)', 'Dr. Shamsul Islam (Bokol)'),
        ('Dr. Nazim Uddin', 'Dr. Nazim Uddin'),
        ('Dr. Md. Shahid Ullah', 'Dr. Md. Shahid Ullah'),
        ('Dr. Jasrin Akter Milli', 'Dr. Jasrin Akter Milli'),
        ('Dr. Shahnaz Parvin Zeba', 'Dr. Shahnaz Parvin Zeba'),
        ('Dr. Salma Akter Ripa', 'Dr. Salma Akter Ripa'),
        ('Dr. Risana Akter', 'Dr. Risana Akter'),
        ('Dr. Nabila Binte Ali', 'Dr. Nabila Binte Ali'),
        ('Prof. Dr. Zahirul Alam', 'Prof. Dr. Zahirul Alam'),
        ('Dr. Habibur Rahman', 'Dr. Habibur Rahman'),
        ('Dr. Arifur Rahman', 'Dr. Arifur Rahman'),
        ('Dr. Sayeda Nafiz Jobaida', 'Dr. Sayeda Nafiz Jobaida'),
        ('Dr. Emdadul Hoque', 'Dr. Emdadul Hoque'),
        ('Dr. Ashraful Hoque', 'Dr. Ashraful Hoque'),
        ('Dr. Rifat Chow. Anik', 'Dr. Rifat Chow. Anik'),
        ('Dr. Saiful Hoque', 'Dr. Saiful Hoque'),
        ('Dr. Abul Khair', 'Dr. Abul Khair'),
        ('Dr. Shahadat Billa', 'Dr. Shahadat Billa'),
        ('Dr. Masud EMO', 'Dr. Masud EMO'),
        ('Dr. Nasid Hasan Mollah EMO', 'Dr. Nasid Hasan Mollah EMO'),
        ('Dr. Saikot EMO', 'Dr. Saikot EMO'),
        ('Dr. Anirban Roy EMO', 'Dr. Anirban Roy EMO'),
        ('Upazilla Health Complex', 'Upazilla Health Complex'),
        ('Self', 'Self'),
    ]
    referred_by = models.CharField(
        max_length=200,
        choices=REFERRED_BY_CHOICES,
        default='Self'
    )

    # 6) Sonologist (short list)
    SONOLOGIST_CHOICES = [
        ('Dr. Nur Mohammad', 'Dr. Nur Mohammad'),
        ('Dr. Nabila Binte Ali', 'Dr. Nabila Binte Ali'),
        ('Dr. Saikot', 'Dr. Saikot'),
    ]
    sonologist = models.CharField(
        max_length=200,
        choices=SONOLOGIST_CHOICES,
        default='Dr. Nur Mohammad'
    )

    # 7) Total Ultrasound (per ID → 1 or 2)
    TOTAL_ULTRA_CHOICES = [
        (1, '1'),
        (2, '2'),
    ]
    total_ultra = models.PositiveSmallIntegerField(
        choices=TOTAL_ULTRA_CHOICES,
        default=1
    )

    # 8) Extra info
    patient_name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']
        indexes = [models.Index(fields=['date', 'referred_by', 'sonologist'])]

    def __str__(self):
        return f"{self.id_number or self.pk} - {self.date} - {self.referred_by}"
