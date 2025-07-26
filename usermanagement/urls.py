from django.urls import path
from . import views

urlpatterns = [
    path("api/auth/registration/account-confirm-email/<str:key>/", views.ConfirmEmailAPI.as_view(), name="account_confirm_email"),
    path('accounts/google/login/', views.direct_google_login, name='google_login_direct'),
    path('accounts/google/login/callback/', views.google_callback, name='google_callback'),
    path('availabilities/<int:doctor_id>/', views.AvailabilityList.as_view(), name='availability-list'),
    path('availabilities/<int:pk>/<int:doctor_id>/', views.AvailabilityDetail.as_view(), name='availability-detail'),
    path('bookings/<int:doctor_id>/', views.BookingListCreate.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/<int:doctor_id>/', views.BookingDetail.as_view(), name='booking-detail'),
    path('getpopulardoctors/', views.GetPopularDoctors.as_view(), name='getpopulardoctors'),
    path('getallpopulardoctors/', views.GetAllPopularDoctors.as_view(), name='getallpopulardoctors'),
    path('getsepcialitydoctors/<str:sepciality>/', views.GetSepcialityDoctors.as_view(), name='getsepcialitydoctors'),
    path('getallsepcialitydoctors/<str:sepciality>/', views.GetAllSepcialityDoctors.as_view(), name='getallsepcialitydoctors'),
    path('getdoctors/', views.GetDoctors.as_view(), name='getdoctors'),
    path('getdoctor/<int:id>/', views.GetDoctor.as_view(), name='getdoctor'),
    path('changefavorite/', views.ChangeFavorite.as_view(), name='changefavorite')
]
