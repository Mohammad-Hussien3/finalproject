from django.urls import path
from . import views

urlpatterns = [
    path("api/auth/registration/account-confirm-email/<str:key>/", views.ConfirmEmailAPI.as_view(), name="account_confirm_email"),
    path('accounts/google/login/', views.direct_google_login, name='google_login_direct'),
    path('accounts/google/login/callback/', views.google_callback, name='google_callback'),
]
