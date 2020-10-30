from django.contrib import admin
from .models import UserPassToken, User

# Register your models here.
admin.site.register(UserPassToken)
admin.site.register(User)
