from django.contrib import admin
from . import models

class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "availability", "phone")
    list_filter = ("specialty", "availability")
    search_fields = ("user__email", "user__first_name")

class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "state")
    search_fields = ("user__email", "user__first_name")

admin.site.register(models.ClientProfile, ClientProfileAdmin)
admin.site.register(models.LawyerProfile, LawyerProfileAdmin)