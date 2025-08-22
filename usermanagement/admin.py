from django.contrib import admin
from .models import Doctor, Availability, Booking, TimeSlot, Patient, FamilyMember, MedicalReport, LabTestImage, MedicalDetail, MedicalSpecialty
# Register your models here.

admin.site.register(Doctor)
admin.site.register(Availability)
admin.site.register(Booking)
admin.site.register(TimeSlot)
admin.site.register(Patient)
admin.site.register(FamilyMember)
admin.site.register(MedicalDetail)
admin.site.register(MedicalReport)
admin.site.register(MedicalSpecialty)
admin.site.register(LabTestImage)