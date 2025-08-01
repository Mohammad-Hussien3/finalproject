from rest_framework import serializers
from .models import Doctor, Availability, TimeSlot, Booking
from django.utils import timezone
import datetime
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Doctor
        fields = '__all__'


class TimeSlotSerializer(serializers.ModelSerializer):
    date = serializers.DateField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = ['id', 'date', 'start_time', 'end_time']


class AvailabilitySerializer(serializers.ModelSerializer):
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ['week_day', 'available_slots']

    def get_available_slots(self, obj):
        now = timezone.now()
        today = timezone.localdate()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=7)

        slots_data = []
        free_slots = obj.slots.filter(is_booked=False)

        for slot in free_slots:
            slot_date = start_of_week + datetime.timedelta(days=obj.week_day)
            slot_dt = timezone.make_aware(
                datetime.datetime.combine(slot_date, slot.start_time),
                timezone.get_current_timezone()
            )
            if now <= slot_dt < timezone.make_aware(
                    datetime.datetime.combine(end_of_week, datetime.time.min),
                    timezone.get_current_timezone()):
                slots_data.append({
                    'id': slot.id,
                    'date': slot_date,
                    'start_time': slot.start_time,
                    'end_time': slot.end_time,
                })

        slots_data.sort(key=lambda x: (x['date'], x['start_time']))
        return slots_data
    

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'slot', 'patient', 'booked_at']
        read_only_fields = ['booked_at', 'patient']

    def create(self, validated_data):
        slot = validated_data['slot']
        if slot.is_booked:
            raise serializers.ValidationError("هذا الفاصل محجوز بالفعل.")
        slot.is_booked = True
        slot.save()
        return Booking.objects.create(**validated_data)

