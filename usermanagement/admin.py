from django.contrib import admin
from .models import Doctor, Availability, Booking, TimeSlot
# Register your models here.

admin.site.register(Doctor)
admin.site.register(Availability)
admin.site.register(Booking)
admin.site.register(TimeSlot)
