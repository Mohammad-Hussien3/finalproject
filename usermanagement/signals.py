from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Availability, TimeSlot, Patient, MedicalReport, FamilyMember, MedicalSpecialty, MedicalDetail
from django.contrib.auth import get_user_model

@receiver(post_save, sender=Availability)
def create_time_slots(sender, instance, **kwargs):
    instance.slots.all().delete()
    for start, end in instance.generate_slots():
        TimeSlot.objects.create(
            availability=instance,
            start_time=start,
            end_time=end
        )

@receiver(pre_delete, sender=Availability)
def delete_time_slots(sender, instance, **kwargs):
    instance.slots.all().delete()


@receiver(post_save, sender=Patient)
def create_report_for_patient(sender, instance, created, **kwargs):
    if created:
        MedicalReport.objects.create(owner=instance, reportImage=instance.photo)

    

User = get_user_model()

@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    if created:
        Patient.objects.get_or_create(user=instance)



@receiver(post_save, sender=Patient)
def update_report_image_on_patient_change(sender, instance, **kwargs):
    reports = MedicalReport.objects.filter(owner=instance, family_member__isnull=True)
    for report in reports:
        if instance.photo:
            report.reportImage = instance.photo
            report.save(update_fields=['reportImage'])


@receiver(post_save, sender=FamilyMember)
def update_report_image_on_family_change(sender, instance, **kwargs):
    reports = MedicalReport.objects.filter(family_member=instance)
    for report in reports:
        if instance.patient.photo:
            report.reportImage = instance.patient.photo
            report.save(update_fields=['reportImage'])



DEFAULT_SPECIALTIES = ['cardiology', 'dentist', 'ophthalmology', 'neurology', 'pulmonology']

@receiver(post_save, sender=Patient)
def create_report_for_new_patient(sender, instance, created, **kwargs):
    if created:
        report, _ = MedicalReport.objects.get_or_create(owner=instance)

        for specialty_name in DEFAULT_SPECIALTIES:
            specialty, _ = MedicalSpecialty.objects.get_or_create(report=report, name=specialty_name)
            MedicalDetail.objects.get_or_create(specialty=specialty)


@receiver(post_save, sender=FamilyMember)
def create_report_for_new_family_member(sender, instance, created, **kwargs):
    if created:
        patient = instance.patient
        report, _ = MedicalReport.objects.get_or_create(owner=patient, family_member=instance)

        if instance.photo:
            report.reportImage = instance.photo
        else:
            report.reportImage = patient.photo
        report.save(update_fields=['reportImage'])

        for specialty_name in DEFAULT_SPECIALTIES:
            specialty, _ = MedicalSpecialty.objects.get_or_create(report=report, name=specialty_name)
            MedicalDetail.objects.get_or_create(specialty=specialty)