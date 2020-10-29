from django.conf.urls import url
from .views import ResetPasswordSend, ResetPassChange


urlpatterns = [
	url(r'^forgot-password/send-mail/$', ResetPasswordSend.as_view(), name='send-password-reset'),
	url(r'^forgot-password/reset_password/$', ResetPassChange.as_view(), name='password-reset'),
]