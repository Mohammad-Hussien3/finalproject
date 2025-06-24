from django.urls import path
from . import views

urlpatterns = [
    path("api/auth/registration/account-confirm-email/<str:key>/", views.ConfirmEmailAPI.as_view(), name="account_confirm_email"),
]
