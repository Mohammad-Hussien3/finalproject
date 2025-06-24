from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.models import EmailConfirmationHMAC

class ConfirmEmailAPI(APIView):
    def get(self, request, key):
        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            confirmation.confirm(request)
            return Response({'detail': 'Email confirmed'})
        return Response({'detail': 'Invalid or expired confirmation key'}, status=400)
