from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
import datetime

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
    DENTIST = 'dentist'
    EYE_DOCTOR = 'eye_doctor'
    DERMATOLOGY = 'dermatology'

    SPECIALITY_TYPES = [
        (CARDIOLOGY, 'cardiology'),
        (DENTIST, 'dentist'),
        (EYE_DOCTOR, 'eye_doctor'),
        (DERMATOLOGY, 'dermatology'),
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

WEEK_DAYS = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    week_day = models.IntegerField(choices=WEEK_DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.get_week_day_display()} {self.start_time}-{self.end_time}"

    def generate_slots(self):
        slots = []
        current = datetime.datetime.combine(datetime.date.today(), self.start_time)
        end_dt = datetime.datetime.combine(datetime.date.today(), self.end_time)
        delta = datetime.timedelta(minutes=self.slot_duration)
        while current + delta <= end_dt:
            slots.append((current.time(), (current + delta).time()))
            current += delta
        return slots
        

class TimeSlot(models.Model):
    availability = models.ForeignKey(Availability, related_name='slots', on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('availability', 'start_time', 'end_time')

    def __str__(self):
        status = "✓" if self.is_booked else "—"
        return f"{self.availability.get_week_day_display()} {self.start_time}-{self.end_time} {status}"

class Booking(models.Model):
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.slot} by {self.patient}"
