from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
from datetime import timedelta
from datetime import datetime as dt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dateutil.relativedelta import relativedelta
from .models import User, UserPassToken
import secrets
import os
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.contrib.auth.hashers import make_password # You have to import make_password

today = datetime.date.today()

# Fuction to generate our token
def gen_password(length=64, charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@$%-_"):
    return "".join([secrets.choice(charset) for _ in range(0, length)])

class ResetPasswordSend(APIView):
	def post(self, request):
		email = request.data.get('email')
		# Check if email exists
		check_user = User.objects.filter(email=email).exists()
		if check_user == False:
			return Response({'error': 'User with the email not found'}, status=status.HTTP_400_BAD_REQUEST)
		else:
			user = User.objects.get(email=email)
			# Let's call the generate function to generate our token
			token = gen_password()
			first_name = user.first_name
			last_name = user.last_name
			password_link = 'http://localhost/forgot-password/reset_password/?signature='+token

			# Let's setup variable's to add to our template
			subject_file = os.path.join(settings.BASE_DIR, "mail/reset_password/subject.txt")
			subject = render_to_string(subject_file, {'name': first_name})
			from_email = settings.DEFAULT_MAIL_SENDER
			to_email = [email]

			password_message_file = os.path.join(settings.BASE_DIR, "mail/reset_password/body.txt")
			password_message = render_to_string(password_message_file, {
	                                                    'first_name': first_name, 'last_name': last_name,
	                                                    'password_link': password_link,
	                                                })

			message = EmailMultiAlternatives(subject=subject, body=password_message, from_email=from_email, to=to_email)

			html_template = os.path.join(settings.BASE_DIR, "mail/reset_password/body.html")
			template = render_to_string(html_template, {
														'first_name': first_name, 'last_name': last_name,
	                                                    'password_link': password_link,
	                                                    })

			message.attach_alternative(template, "text/html")

			message.send()
			UserPassToken.objects.create(user=user, token=token, sent=True)


		return Response({'success': 'Password Reset Link has been sent to'+ ' ' + email}, status=status.HTTP_200_OK)

class ResetPassChange(APIView):
	def post(self, request):
		signature = request.data.get('signature')
		password = request.data.get('new_password')
		new_password = make_password(password)

		# Check if token exists
		check_token = UserPassToken.objects.filter(token=signature).exists()
		# Check if token has expired
		if check_token == False:
			return Response({'not_found': 'Code is invalid. Try again'}, status=status.HTTP_404_NOT_FOUND)
		else:
			get_token = UserPassToken.objects.get(token=signature)
		if get_token.expired:
			return Response({'error': 'Sorry, Code has already been expired.'}, status=status.HTTP_400_BAD_REQUEST)

		# get user from UserPassToken
		token = UserPassToken.objects.get(token=signature)
		user = User.objects.get(id=token.user.id)
		user.password = new_password
		user.save()
		UserPassToken.objects.filter(token=signature).update(expired=True)
		return Response({'success': "Password Changed Successfully."}, status=status.HTTP_200_OK)
