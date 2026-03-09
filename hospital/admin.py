from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
	list_display = ("name", "special", "department", "mobile", "experience_years")
	search_fields = ("name", "special", "department", "mobile")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ("name", "gender", "mobile", "blood_group", "dob")
	search_fields = ("name", "mobile", "emergency_contact")
	list_filter = ("gender", "blood_group")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ("doctor", "patient", "date1", "time1", "status")
	search_fields = ("doctor__name", "patient__name")
	list_filter = ("status", "date1")