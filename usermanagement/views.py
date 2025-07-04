from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.models import EmailConfirmationHMAC
from django.shortcuts import redirect
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Availability, Booking, Doctor
from .serializers import AvailabilitySerializer, BookingSerializer, DoctorSerializer


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


from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.conf import settings
import requests

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


class AvailabilityList(ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Availability.objects.filter(doctor__id=doctor_id)


class AvailabilityDetail(RetrieveAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Availability.objects.filter(doctor__id=doctor_id)



class BookingListCreate(ListCreateAPIView):
    queryset = Booking.objects.select_related('slot')
    serializer_class = BookingSerializer

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Booking.objects.select_related('slot', 'slot__availability').filter(slot__availability__doctor__id=doctor_id)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class BookingDetail(RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.select_related('slot')
    serializer_class = BookingSerializer

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Booking.objects.select_related('slot', 'slot__availability').filter(slot__availability__doctor__id=doctor_id)


class GetPopularDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return Doctor.objects.all().order_by('-rating')[:5]


class GetSepcialityDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        sepciality = self.kwargs['sepciality']
        return Doctor.objects.filter(sepciality=sepciality)[:5]
    

class GetDoctors(ListAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class GetDoctor(RetrieveAPIView):
    
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'id'