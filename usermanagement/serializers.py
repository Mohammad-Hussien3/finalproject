from rest_framework import serializers
from .models import Doctor, Availability, TimeSlot, Booking, Patient
from django.utils import timezone
import datetime
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SimpleAvailabilitySerializer(serializers.ModelSerializer):    
    class Meta:
        model = Availability
        fields = ['start_time', 'end_time']


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    availability = serializers.SerializerMethodField() 

    class Meta:
        model = Doctor
        fields = '__all__'


    def get_availability(self, obj):
        today = timezone.localdate()
        days = [today + datetime.timedelta(days=i) for i in range(6)]

        availability_data = []
        for d in days:
            availability = Availability.objects.filter(doctor=obj, date=d).first()
            if availability:
                availability_data.append({
                    "date": d,
                    "week_day": d.strftime("%A"),
                    "start_time": availability.start_time,
                    "end_time": availability.end_time,
                })
            else:
                availability_data.append({
                    "date": d,
                    "week_day": d.strftime("%A"),
                    "start_time": None,
                    "end_time": None,
                })

        return availability_data


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
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
        fields = ['week_day', 'date', 'available_slots']


    def get_available_slots(self, obj):
        now = timezone.now()
        end = now + datetime.timedelta(days=7)
        tz = timezone.get_current_timezone()
        
        free_slots = obj.slots.filter(is_booked=False)
        slots_data = []

        for slot in free_slots:
            slot_dt = datetime.datetime.combine(obj.date, slot.start_time)

            if timezone.is_naive(slot_dt):
                slot_dt = timezone.make_aware(slot_dt, tz)

            if now <= slot_dt < end:
                slots_data.append({
                    'id': slot.id,
                    'start_time': slot.start_time.isoformat(),
                })

        return slots_data
    

class SimpleDoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'sepciality', 'address', 'photo', 'phoneNumber']


class BookingSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'slot', 'patient', 'booked_at', 'doctor']
        read_only_fields = ['booked_at', 'patient']

    def create(self, validated_data):
        slot = validated_data['slot']
        if slot.is_booked:
            raise serializers.ValidationError("هذا الفاصل محجوز بالفعل.")
        slot.is_booked = True
        slot.save()
        return Booking.objects.create(**validated_data)

    def get_doctor(self, obj):
        doctor = obj.slot.availability.doctor
        return SimpleDoctorSerializer(doctor).data
