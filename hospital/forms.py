from django import forms

from .models import Appointment, Doctor, Patient


class BootstrapFormMixin:
    def _apply_bootstrap_classes(self):
        for field_name, field in self.fields.items():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
            if field.required:
                field.widget.attrs.setdefault("required", "required")


class DoctorForm(BootstrapFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()

    class Meta:
        model = Doctor
        fields = [
            "name",
            "mobile",
            "special",
            "department",
            "qualification",
            "experience_years",
            "availability_schedule",
        ]
        widgets = {
            "availability_schedule": forms.Textarea(attrs={"rows": 3}),
        }


class PatientForm(BootstrapFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()

    class Meta:
        model = Patient
        fields = [
            "name",
            "gender",
            "mobile",
            "address",
            "dob",
            "blood_group",
            "emergency_contact",
            "allergies",
            "medical_notes",
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "medical_notes": forms.Textarea(attrs={"rows": 3}),
        }


class AppointmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "patient", "date1", "time1", "status"]
        widgets = {
            "date1": forms.DateInput(attrs={"type": "date"}),
            "time1": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.order_by("name")
        self.fields["patient"].queryset = Patient.objects.order_by("name")
        self._apply_bootstrap_classes()

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        date1 = cleaned_data.get("date1")
        time1 = cleaned_data.get("time1")

        if doctor and date1 and time1:
            clashes = Appointment.objects.filter(doctor=doctor, date1=date1, time1=time1)
            if self.instance.pk:
                clashes = clashes.exclude(pk=self.instance.pk)
            if clashes.exists():
                raise forms.ValidationError(
                    "This doctor is already booked for the selected date and time."
                )

        return cleaned_data
