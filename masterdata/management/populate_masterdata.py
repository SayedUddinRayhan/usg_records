from django.core.management.base import BaseCommand
from masterdata.models import ExamName, Referrer, Sonologist, ExamType

class Command(BaseCommand):
    help = "Populate masterdata tables with initial values."

    def handle(self, *args, **options):
        exam_names = [
            'Whole Abdomen',
            'Whole Abdomen with Pregnancy',
            'Lower Abdomen',
            'HBS',
            'Pregnancy Profile',
            'Pregnancy Profile twin',
            'Anomaly Scan',
            'Fetal Doppler Study',
            'Thyroid/Neck',
            'Testes/ISR',
            'Swelling',
            'Breast',
            'TVS',
        ]

        referrers = [
            'Prof. Dr. Mahbubul Islam Majumder',
            'Prof. Dr. Samsun Nahar',
            'Prof. Dr. Haroon-Or-Rashid',
            'Dr. Belal Hossain',
            'Prof. Dr. Md. Safiqur Rahman Patwary',
            'Prof. Dr. Nasir Uddin Mahmud',
            'Dr. Mahfuzur Rahman (EMON)',
            'Dr. Hasan Imam (Sany)',
            'Dr. Joynal Abedin',
            'Dr. Md. Mainul Hasan Sohel',
            'Dr. Kawsar Hamid',
            'Dr. Mostaque Ahmad',
            'Dr. Shamsul Islam (Bokol)',
            'Dr. Nazim Uddin',
            'Dr. Md. Shahid Ullah',
            'Dr. Jasrin Akter Milli',
            'Dr. Shahnaz Parvin Zeba',
            'Dr. Salma Akter Ripa',
            'Dr. Risana Akter',
            'Dr. Nabila Binte Ali',
            'Prof. Dr. Zahirul Alam',
            'Dr. Habibur Rahman',
            'Dr. Arifur Rahman',
            'Dr. Sayeda Nafiz Jobaida',
            'Dr. Emdadul Hoque',
            'Dr. Ashraful Hoque',
            'Dr. Rifat Chow. Anik',
            'Dr. Saiful Hoque',
            'Dr. Abul Khair',
            'Dr. Shahadat Billa',
            'Dr. Masud EMO',
            'Dr. Nasid Hasan Mollah EMO',
            'Dr. Saikot EMO',
            'Dr. Anirban Roy EMO',
            'Upazilla Health Complex',
            'Self'
        ]

        sonologists = [
            'Dr. Nur Mohammad',
            'Dr. Nabila Binte Ali',
            'Dr. Saikot'
        ]

        exam_types = ['Normal', 'Special']

        created = 0
        for name in exam_names:
            obj, _ = ExamName.objects.get_or_create(name=name)
            created += 1
        for name in exam_types:
            obj, _ = ExamType.objects.get_or_create(name=name)
            created += 1
        for name in referrers:
            obj, _ = Referrer.objects.get_or_create(name=name)
            created += 1
        for name in sonologists:
            obj, _ = Sonologist.objects.get_or_create(name=name)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Populated masterdata with {created} items.'))
