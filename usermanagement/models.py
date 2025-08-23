from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
import datetime



class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    blood_type = models.CharField(max_length=3, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    allergies_count = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='photos', blank=True)

    def __str__(self):
        return f"Patient Profile: {self.user.username} {self.id}"


class FamilyMember(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="family_records")
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.relation})"


class MedicalReport(models.Model):
    owner = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_reports")
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name="medical_reports", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    labTestImage = models.ImageField(upload_to='photos', blank=True, null=True)
    reportImage = models.ImageField(upload_to='photos', blank=True, null=True)

    def __str__(self):
        if self.family_member:
            return f"Report for {self.family_member.name}"
        return f"Report for {self.owner.user.username}"



class MedicalSpecialty(models.Model):
    report = models.ForeignKey(MedicalReport, on_delete=models.CASCADE, related_name="specialties")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.report}"



class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.FloatField(blank=True, default=0.0)
    price = models.FloatField(default=0.0)
    isFavorite = models.BooleanField(default=False)
    yearsExperience = models.IntegerField(default=0)
    patientsNumber = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='photos', blank=True)
    consultation = models.IntegerField(default=30)
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



class MedicalDetail(models.Model):
    specialty = models.ForeignKey(MedicalSpecialty, on_delete=models.CASCADE, related_name="details")
    
    past_diseases = models.TextField(blank=True, null=True)
    current_diseases = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    
    past_doctors = models.JSONField(blank=True, null=True)
    current_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, blank=True, null=True, related_name="patients_followed")

    images = models.ImageField(upload_to='photos', blank=True, null=True)

    def __str__(self):
        return f"Details for {self.specialty.name}"
    


WEEK_DAYS = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]

class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    week_day = models.CharField(choices=WEEK_DAYS, max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()


    def __str__(self):
        return f"{self.get_week_day_display()} {self.start_time}-{self.end_time}"

    def generate_slots(self):
        slots = []
        current = datetime.datetime.combine(datetime.date.today(), self.start_time)
        end_dt = datetime.datetime.combine(datetime.date.today(), self.end_time)
        slot_duration = self.doctor.consultation
        delta = datetime.timedelta(minutes=slot_duration)
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
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.slot} by {self.patient}"
