from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Doctor, Availability, TimeSlot

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