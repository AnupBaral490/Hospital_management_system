from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    NO_SHOW = "no_show", "No Show"


class BloodGroup(models.TextChoices):
    A_POS = "A+", "A+"
    A_NEG = "A-", "A-"
    B_POS = "B+", "B+"
    B_NEG = "B-", "B-"
    AB_POS = "AB+", "AB+"
    AB_NEG = "AB-", "AB-"
    O_POS = "O+", "O+"
    O_NEG = "O-", "O-"

class Doctor(models.Model):
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20)
    special = models.CharField(max_length=50)
    department = models.CharField(max_length=80, blank=True)
    qualification = models.CharField(max_length=120, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    availability_schedule = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    mobile = models.CharField(max_length=20, blank=True)  # optional
    address = models.CharField(max_length=150)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BloodGroup.choices, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    booked_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="booked_appointments",
    )
    date1 = models.DateField()
    time1 = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "date1", "time1"], name="unique_doctor_time_slot"
            )
        ]


    def __str__(self):
        return self.doctor.name+"--"+self.patient.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=120)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=80, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=150, blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BloodGroup.choices, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class HealthDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_documents")
    title = models.CharField(max_length=120)
    file = models.FileField(upload_to="health_documents/%Y/%m")
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AppointmentFeedback(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointment_feedbacks")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback {self.rating}/5 for appointment {self.appointment_id}"






