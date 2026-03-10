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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "phone", "subject", "created_at")
	search_fields = ("name", "email", "phone", "subject", "message")
	list_filter = ("created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "full_name", "phone", "blood_group", "updated_at")
	search_fields = ("user__username", "full_name", "phone")


@admin.register(HealthDocument)
class HealthDocumentAdmin(admin.ModelAdmin):
	list_display = ("user", "title", "uploaded_at")
	search_fields = ("user__username", "title", "notes")
	list_filter = ("uploaded_at",)


@admin.register(AppointmentFeedback)
class AppointmentFeedbackAdmin(admin.ModelAdmin):
	list_display = ("appointment", "user", "rating", "created_at")
	search_fields = ("appointment__doctor__name", "appointment__patient__name", "comment")
	list_filter = ("rating", "created_at")