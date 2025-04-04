# activity/admin.py

from django.contrib import admin
from .models import Activity, ActivityUpdate

admin.site.register(Activity)
admin.site.register(ActivityUpdate)
