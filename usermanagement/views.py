from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.models import EmailConfirmationHMAC
from django.shortcuts import redirect
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, CreateAPIView
from .models import Availability, Booking, Doctor, TimeSlot, Patient, MedicalReport, MedicalDetail, MedicalSpecialty
from .serializers import AvailabilitySerializer, BookingSerializer, DoctorSerializer, PatientSerializer, SimpleAvailabilitySerializer, FamilyMemberSerializer, PatientMedicalReportSerializer
from rest_framework import status
from django.utils import timezone
import datetime
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.conf import settings
import requests
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound

class CustomLoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if not user:
            try:
                candidate = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                candidate = None

            if candidate and candidate.check_password(password):
                user = candidate

        if not user:
            return Response({"detail": "Invalid email or password."},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "This account is inactive."},
                            status=status.HTTP_403_FORBIDDEN)

        doctor = Doctor.objects.filter(user=user).first()
        if doctor:
            return Response({"role": "doctor", "role_id": doctor.id}, status=status.HTTP_200_OK)

        patient = Patient.objects.filter(user=user).first()
        if patient:
            return Response({"role": "patient", "role_id": patient.id}, status=status.HTTP_200_OK)

        return Response({"detail": "User role not found (doctor/patient)."},
                        status=status.HTTP_404_NOT_FOUND)

class ConfirmEmailAPI(APIView):
    def get(self, request, key):
        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            confirmation.confirm(request)
            return Response({'detail': 'Email confirmed'})
        return Response({'detail': 'Invalid or expired confirmation key'}, status=400)



def direct_google_login(request):

    url = "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?client_id=414509258770-d8c07u9s9brrf8a5ilhj9lj55lgmet4v.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fmohammadhussien.pythonanywhere.com%2Faccounts%2Fgoogle%2Flogin%2Fcallback%2F&scope=profile%20email&response_type=code&state=h0dNTBhddghTx3Zf&access_type=online&service=lso&o2v=2&flowName=GeneralOAuthFlow"    
    return redirect(url)



def google_callback(request):
    
    url = "https://mohammadhussien.pythonanywhere.com/"  

    code = request.GET.get('code')
    if not code:
        return redirect('login_error')
    
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
        
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    token_data = response.json()
    access_token = token_data.get('access_token')
    
    user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info = requests.get(user_info_url, headers=headers).json()
    print(user_info)
    
    user, created = User.objects.get_or_create(
        email=user_info['name'],
        defaults={
            'username': user_info['email'],
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', ''),
        }
    )
    
    return redirect(url)



# Patient
class AvailabilityList(APIView):
     def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor not found"}, status=404)

        today = timezone.localdate()
        days = [today + datetime.timedelta(days=i) for i in range(7)]

        data = []
        for d in days:
            availability = Availability.objects.filter(doctor=doctor, date=d).first()
            if availability:
                serialized = AvailabilitySerializer(availability).data
            else:
                serialized = {
                    "week_day": d.strftime("%A"),
                    "date": d,
                    "available_slots": []
                }
            data.append(serialized)

        return Response(data)
    

WEEKDAY_NAME_TO_INT = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


class MyUpcomingBookingsView(ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        patient_id = self.kwargs['id']
        now = timezone.now()

        bookings = Booking.objects.filter(patient_id=patient_id).select_related('slot__availability')

        today = timezone.localdate()
        start_of_week = today - datetime.timedelta(days=today.weekday())

        upcoming_bookings = []
        for booking in bookings:
            slot = booking.slot
            availability = slot.availability
            slot_date = start_of_week + datetime.timedelta(days=WEEKDAY_NAME_TO_INT[availability.week_day])

            slot_datetime = datetime.datetime.combine(slot_date, slot.start_time)
            slot_datetime = timezone.make_aware(slot_datetime, timezone.get_current_timezone())

            if slot_datetime > now:
                upcoming_bookings.append(booking.pk)


        return Booking.objects.filter(patient_id=patient_id)
    

class GetDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class GetPopularDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return Doctor.objects.all().order_by('-rating')[:5]


class GetAllPopularDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return Doctor.objects.all().order_by('-rating')


class GetSepcialityDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        sepciality = self.kwargs['sepciality']
        print(type(Doctor.objects.all()[0].rating))
        return Doctor.objects.filter(sepciality=sepciality)[:5]
    

class GetAllSepcialityDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        sepciality = self.kwargs['sepciality']
        return Doctor.objects.filter(sepciality=sepciality)


class GetDoctor(RetrieveAPIView):
    
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'id'


class ChangeFavorite(APIView):

    def post(self, request):
        doctor_ids = request.data.get('ids')

        if not isinstance(doctor_ids, list):
            return Response({'error': 'error'}, status=status.HTTP_400_BAD_REQUEST)

        updated_doctors = []

        for doc_id in doctor_ids:
            doctor = Doctor.objects.get(pk=doc_id)
            doctor.isFavorite = not doctor.isFavorite
            doctor.save()
            updated_doctors.append(doctor)

        serializer = DoctorSerializer(updated_doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Book(APIView):

    def post(self, request, doctor_id, slot_id, patient_id):
        doctor = Doctor.objects.get(id=doctor_id)
        slot = TimeSlot.objects.get(id=slot_id, availability__doctor=doctor)
        patient = Patient.objects.get(id=patient_id)
        booking = Booking.objects.create(
            slot=slot,
            patient=patient
        )
        slot.is_booked = True
        slot.save()
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class GetPatient(RetrieveAPIView):
    
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'


class AvailabilityCreate(CreateAPIView):
    serializer_class = SimpleAvailabilitySerializer

    def perform_create(self, serializer):
        doctor_id = self.kwargs.get("doctor_id")
        doctor = Doctor.objects.get(id=doctor_id)
        serializer.save(doctor=doctor)


class UpdatePatientInformation(UpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'



class CreateFamilyMemberView(CreateAPIView):
    serializer_class = FamilyMemberSerializer

    def create(self, request, *args, **kwargs):
        patient_id = self.kwargs.get('id')
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['patient'] = patient.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        family_member = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class UpdatePatientMedicalReportView(APIView):

    def patch(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            raise NotFound("Patient not found")

        report= MedicalReport.objects.filter(owner=patient).first()

        details_data = request.data.get('medical_details', [])
        for detail_data in details_data:
            specialty_name = detail_data.get('specialty')
            if not specialty_name:
                continue

            specialty, _ = MedicalSpecialty.objects.get_or_create(report=report, name=specialty_name)

            medical_detail, _ = MedicalDetail.objects.get_or_create(specialty=specialty)

            for field in ['past_diseases', 'current_diseases', 'current_medications', 'past_doctors']:
                if field in detail_data:
                    setattr(medical_detail, field, detail_data[field])

            doctor_id = detail_data.get('current_doctor')
            if doctor_id:
                try:
                    doctor_instance = Doctor.objects.get(id=doctor_id)
                    medical_detail.current_doctor = doctor_instance
                except Doctor.DoesNotExist:
                    medical_detail.current_doctor = None
            else:
                medical_detail.current_doctor = None



            if 'images' in detail_data and detail_data['images']:
                medical_detail.images = detail_data['images']

            medical_detail.save()

        serializer = PatientMedicalReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)



# Doctor
class UpdateDoctorInformation(UpdateAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'id'