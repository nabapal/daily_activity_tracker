# activity/admin.py

from .models import Activity, ActivityUpdate
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

admin.site.register(Activity)
admin.site.register(ActivityUpdate)
