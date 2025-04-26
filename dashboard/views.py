from django.core.mail import send_mass_mail
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from members.models import Member
from django.conf import settings

class SendEMAILTOALLVIEW(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        from_email=settings.EMAIL_HOST_USER

        if not subject or not message:
            return JsonResponse({'error': 'Subject and message are required.'}, status=400)

        members = Member.objects.values_list('email', flat=True)
        recipient_list = list(members)

        if not recipient_list:
            return JsonResponse({'error': 'No members found.'}, status=400)

        # Correct the from_email
        messages = [(subject, message ,from_email, [email]) for email in recipient_list]

        send_mass_mail(messages, fail_silently=False)

        return JsonResponse({'success': f'Emails sent to {len(recipient_list)} members.'})
