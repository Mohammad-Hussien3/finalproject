from django.urls import path
from . import views

urlpatterns = [
    path("api/auth/registration/account-confirm-email/<str:key>/", views.ConfirmEmailAPI.as_view(), name="account_confirm_email"),
    path('accounts/google/login/', views.direct_google_login, name='google_login_direct'),
    path('accounts/google/login/callback/', views.google_callback, name='google_callback'),

    # Patient
    path('availabilities/<int:doctor_id>/', views.AvailabilityList.as_view(), name='availability-list'),
    path('my-upcoming-bookings/<int:id>/', views.MyUpcomingBookingsView.as_view(), name='my-upcoming-bookings'),
    path('getdoctors/', views.GetDoctors.as_view(), name='getdoctors'),
    path('getpopulardoctors/', views.GetPopularDoctors.as_view(), name='getpopulardoctors'),
    path('getallpopulardoctors/', views.GetAllPopularDoctors.as_view(), name='getallpopulardoctors'),
    path('getsepcialitydoctors/<str:sepciality>/', views.GetSepcialityDoctors.as_view(), name='getsepcialitydoctors'),
    path('getallsepcialitydoctors/<str:sepciality>/', views.GetAllSepcialityDoctors.as_view(), name='getallsepcialitydoctors'),
    path('getdoctor/<int:id>/', views.GetDoctor.as_view(), name='getdoctor'),
    path('changefavorite/', views.ChangeFavorite.as_view(), name='changefavorite'),
    path('booking/<int:doctor_id>/<int:slot_id>/<int:patient_id>/', views.Book.as_view(), name='booking'),
    path('getpatient/<int:id>/', views.GetPatient.as_view(), name='getPateint'),


    # Doctor
    path('doctorupdate/<int:id>/', views.UpdateDoctorInformation.as_view(), name='doctorUpdate')
]
