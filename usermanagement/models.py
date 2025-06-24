from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.DecimalField(blank=True, max_digits=10, decimal_places=10, default=0.0)
    price = models.DecimalField(max_digits=10, decimal_places=10, default=0.0)
    isFavorite = models.BooleanField(default=False)
    yearsExperience = models.IntegerField(default=0)
    patientsNumber = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='photos', blank=True)
    consultation = models.IntegerField(default=0)
    phoneNumber = models.IntegerField(null=True, blank=True, default=0)
    address = models.CharField(max_length=100)

    CARDIOLOGY = 'cardiology'
    VASCULAR = 'vascular'
    PULMONOLOGY = 'pulmonology'
    DERMATOLOGY = 'dermatology'
    UROLOGY = 'urology'
    ORTHOPEDICS = 'orthopedics'

    SPECIALITY_TYPES = [
        (CARDIOLOGY, 'cardiology'),
        (VASCULAR, 'vascular'),
        (PULMONOLOGY, 'pulmonology'),
        (DERMATOLOGY, 'dermatology'),
        (UROLOGY, 'urology'),
        (ORTHOPEDICS, 'orthopedics')
    ]
    sepciality = models.CharField(max_length=15, choices=SPECIALITY_TYPES, null=False, blank=False)

    TEST1 = 'test1'
    TEST2 = 'test2'
    TEST3 = 'test3'
    TEST4 = 'test4'
    TEST5 = 'test5'

    SERVICE_TYPES = [
        (TEST1, 'test1'),
        (TEST2, 'test2'),
        (TEST3, 'test3'),
        (TEST4, 'test4'),
        (TEST5, 'test5'),
    ]

    services = MultiSelectField(choices=SERVICE_TYPES)
