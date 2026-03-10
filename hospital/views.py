from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from .forms import (
    DoctorForm,
    PatientForm,
    AppointmentForm,
    ContactMessageForm,
    UserProfileForm,
    HealthDocumentForm,
    AppointmentFeedbackForm,
    RescheduleForm,
)
from datetime import datetime
# Create your views here.


DISEASE_SPECIALIZATION_MAP = {
    "fever": ["general", "internal", "infectious"],
    "cold": ["ent", "general"],
    "cough": ["pulmonology", "ent", "general"],
    "skin": ["dermatology"],
    "heart": ["cardiology"],
    "chest pain": ["cardiology", "pulmonology"],
    "stomach": ["gastro", "gastroenterology"],
    "diabetes": ["endocrinology", "internal"],
    "pregnancy": ["gynecology", "obstetrics"],
    "child": ["pediatric", "paediatric"],
    "bone": ["orthopedic", "orthopaedic"],
    "joint": ["orthopedic", "orthopaedic", "rheumatology"],
    "eye": ["ophthalmology"],
    "ear": ["ent"],
    "mental": ["psychiatry", "psychology"],
    "headache": ["neurology", "general"],
}

DISEASE_TAGS = [
    "Fever",
    "Cold",
    "Cough",
    "Skin",
    "Heart",
    "Stomach",
    "Diabetes",
    "Pregnancy",
    "Child",
    "Bone",
    "Joint",
    "Eye",
    "Ear",
    "Mental",
    "Headache",
]

AVAILABLE_TIME_SLOTS = [
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
    "17:00",
]


def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _get_available_slots(doctor, date_value, exclude_appointment_id=None):
    booked_times = (
        Appointment.objects.filter(doctor=doctor, date1=date_value)
        .exclude(status=AppointmentStatus.CANCELLED)
        .exclude(id=exclude_appointment_id)
        .values_list("time1", flat=True)
    )
    booked_str = {t.strftime("%H:%M") for t in booked_times}
    return [slot for slot in AVAILABLE_TIME_SLOTS if slot not in booked_str]


def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="login",
    )(view_func)


def user_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and not user.is_staff,
        login_url="user_login",
    )(view_func)


def About(request):
    return render(request, 'about.html')


def Contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting us. We will get back to you soon.")
            return redirect("contact")
    else:
        form = ContactMessageForm()

    return render(request, 'contact.html', {"form": form})


def User_Root(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_home")
    if request.user.is_authenticated:
        return redirect("user_home")
    return redirect("user_login")


def User_Register(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            error = "Please fill all required fields."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        elif User.objects.filter(email=email).exists():
            error = "Email already exists."
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            return redirect("user_login")

    return render(request, "user_register.html", {"error": error})


def User_Login(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)

        if user and not user.is_staff:
            login(request, user)
            return redirect("user_home")
        error = "Invalid user credentials."

    return render(request, "user_login.html", {"error": error})


@user_required
def User_Home(request):
    top_doctors = Doctor.objects.annotate(
        avg_rating=Avg("appointment__feedback__rating"),
        review_count=Count("appointment__feedback"),
    ).order_by("name")[:6]

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.username},
    )

    upcoming_count = Appointment.objects.filter(
        booked_by=request.user,
        status=AppointmentStatus.SCHEDULED,
    ).count()

    data = {
        "doctor_count": Doctor.objects.count(),
        "appointment_count": Appointment.objects.count(),
        "disease_tags": DISEASE_TAGS,
        "top_doctors": top_doctors,
        "upcoming_count": upcoming_count,
        "profile_complete": bool(profile.phone and profile.address),
    }
    return render(request, "user_home.html", data)


def User_Find_Doctor(request):
    disease = request.GET.get("disease", "").strip()
    query = request.GET.get("q", "").strip()

    doctors = Doctor.objects.annotate(
        avg_rating=Avg("appointment__feedback__rating"),
        review_count=Count("appointment__feedback"),
    ).order_by("name")
    matched_terms = []

    if disease:
        disease_normalized = disease.lower()
        matched_terms.append(disease)
        for keyword, spec_terms in DISEASE_SPECIALIZATION_MAP.items():
            if keyword in disease_normalized:
                matched_terms.extend(spec_terms)

        filter_q = Q()
        for term in matched_terms:
            filter_q |= Q(special__icontains=term) | Q(department__icontains=term)
        doctors = doctors.filter(filter_q).distinct()

    if query:
        doctors = doctors.filter(
            Q(name__icontains=query)
            | Q(special__icontains=query)
            | Q(department__icontains=query)
        )

    data = {
        "doctors": doctors,
        "disease": disease,
        "q": query,
        "disease_tags": DISEASE_TAGS,
    }
    return render(request, "user_doctor_list.html", data)


@user_required
def User_Book_Appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.username},
    )
    error = ""
    success = ""
    available_slots = []
    selected_date = request.GET.get("date1", "").strip()

    initial = {
        "name": profile.full_name or request.user.get_full_name() or request.user.username,
        "gender": profile.gender,
        "mobile": profile.phone,
        "address": profile.address,
        "dob": profile.dob.isoformat() if profile.dob else "",
        "blood_group": profile.blood_group,
        "emergency_contact": profile.emergency_contact,
        "allergies": profile.allergies,
        "medical_notes": "",
        "date1": selected_date,
        "time1": "",
    }

    if selected_date:
        parsed_date = _parse_date(selected_date)
        if parsed_date:
            available_slots = _get_available_slots(doctor, parsed_date)

    if request.method == "POST":
        initial = {
            "name": request.POST.get("name", "").strip(),
            "gender": request.POST.get("gender", "").strip(),
            "mobile": request.POST.get("mobile", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "dob": request.POST.get("dob", "").strip(),
            "blood_group": request.POST.get("blood_group", "").strip(),
            "emergency_contact": request.POST.get("emergency_contact", "").strip(),
            "allergies": request.POST.get("allergies", "").strip(),
            "medical_notes": request.POST.get("medical_notes", "").strip(),
            "date1": request.POST.get("date1", "").strip(),
            "time1": request.POST.get("time1", "").strip(),
        }

        name = initial["name"]
        gender = initial["gender"]
        mobile = initial["mobile"]
        address = initial["address"]
        dob = initial["dob"] or None
        blood_group = initial["blood_group"]
        emergency_contact = initial["emergency_contact"]
        allergies = initial["allergies"]
        medical_notes = initial["medical_notes"]
        date1 = initial["date1"]
        time1 = initial["time1"]

        parsed_date = _parse_date(date1)
        if parsed_date:
            available_slots = _get_available_slots(doctor, parsed_date)

        if not all([name, gender, address, date1, time1]):
            error = "Please fill all required fields."
        else:
            clash = Appointment.objects.filter(
                doctor=doctor,
                date1=date1,
                time1=time1,
            ).exclude(status=AppointmentStatus.CANCELLED)

            if clash.exists():
                error = "Selected slot is already booked for this doctor. Please choose another time."
            else:
                patient = Patient.objects.create(
                    name=name,
                    gender=gender,
                    mobile=mobile,
                    address=address,
                    dob=dob,
                    blood_group=blood_group,
                    emergency_contact=emergency_contact,
                    allergies=allergies,
                    medical_notes=medical_notes,
                )
                Appointment.objects.create(
                    doctor=doctor,
                    patient=patient,
                    booked_by=request.user,
                    date1=date1,
                    time1=time1,
                    status=AppointmentStatus.SCHEDULED,
                )
                profile.full_name = name
                profile.gender = gender
                profile.phone = mobile
                profile.address = address
                profile.dob = dob or None
                profile.blood_group = blood_group
                profile.emergency_contact = emergency_contact
                profile.allergies = allergies
                profile.save()
                success = "Your appointment request has been submitted successfully."
                initial["time1"] = ""

    data = {
        "doctor": doctor,
        "error": error,
        "success": success,
        "blood_groups": BloodGroup.choices,
        "genders": ["Male", "Female", "Other"],
        "initial": initial,
        "available_slots": available_slots,
    }
    return render(request, "user_book_appointment.html", data)


@user_required
def User_Profile(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.username},
    )

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("user_profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "user_profile.html", {"form": form})


@user_required
def User_My_Appointments(request):
    status = request.GET.get("status", "").strip()

    appointments = Appointment.objects.select_related("doctor", "patient").filter(
        booked_by=request.user
    )
    if status:
        appointments = appointments.filter(status=status)
    appointments = appointments.order_by("-date1", "-time1")

    data = {
        "appointments": appointments,
        "statuses": AppointmentStatus.choices,
        "selected_status": status,
    }
    return render(request, "user_my_appointments.html", data)


@user_required
def User_Reschedule_Appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctor", "patient"),
        id=appointment_id,
        booked_by=request.user,
    )

    if appointment.status != AppointmentStatus.SCHEDULED:
        messages.error(request, "Only scheduled appointments can be rescheduled.")
        return redirect("user_my_appointments")

    selected_date = request.GET.get("date1", appointment.date1.isoformat())
    parsed_date = _parse_date(selected_date)
    available_slots = _get_available_slots(
        appointment.doctor,
        parsed_date or appointment.date1,
        exclude_appointment_id=appointment.id,
    )

    if request.method == "POST":
        form = RescheduleForm(request.POST)
        if form.is_valid():
            new_date = form.cleaned_data["date1"]
            new_time = form.cleaned_data["time1"]

            clash = Appointment.objects.filter(
                doctor=appointment.doctor,
                date1=new_date,
                time1=new_time,
            ).exclude(id=appointment.id).exclude(status=AppointmentStatus.CANCELLED)

            if clash.exists():
                form.add_error("time1", "Selected slot is already booked. Please choose another time.")
            else:
                appointment.date1 = new_date
                appointment.time1 = new_time
                appointment.save()
                messages.success(request, "Appointment rescheduled successfully.")
                return redirect("user_my_appointments")
    else:
        form = RescheduleForm(
            initial={
                "date1": appointment.date1,
                "time1": appointment.time1,
            }
        )

    data = {
        "appointment": appointment,
        "form": form,
        "available_slots": available_slots,
    }
    return render(request, "user_reschedule_appointment.html", data)


@user_required
def User_Available_Slots(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    date_str = request.GET.get("date", "").strip()
    exclude_appointment = request.GET.get("exclude_appointment", "").strip()
    try:
        exclude_appointment_id = int(exclude_appointment) if exclude_appointment else None
    except ValueError:
        exclude_appointment_id = None

    date_obj = _parse_date(date_str)
    if not date_obj:
        return JsonResponse({"error": "Invalid date"}, status=400)

    slots = _get_available_slots(doctor, date_obj, exclude_appointment_id=exclude_appointment_id)
    return JsonResponse({"doctor": doctor.name, "date": date_str, "slots": slots})


@user_required
def User_Health_Documents(request):
    if request.method == "POST":
        form = HealthDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("user_documents")
    else:
        form = HealthDocumentForm()

    documents = HealthDocument.objects.filter(user=request.user)
    return render(
        request,
        "user_documents.html",
        {"form": form, "documents": documents},
    )


@user_required
def User_Add_Feedback(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctor", "patient"),
        id=appointment_id,
        booked_by=request.user,
    )

    if appointment.status != AppointmentStatus.COMPLETED:
        messages.error(request, "Feedback can be submitted only for completed appointments.")
        return redirect("user_my_appointments")

    if hasattr(appointment, "feedback"):
        messages.info(request, "Feedback already submitted for this appointment.")
        return redirect("user_my_appointments")

    if request.method == "POST":
        form = AppointmentFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.appointment = appointment
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you. Your feedback has been submitted.")
            return redirect("user_my_appointments")
    else:
        form = AppointmentFeedbackForm()

    return render(
        request,
        "user_feedback.html",
        {"appointment": appointment, "form": form},
    )


@user_required
def User_Appointment_Status(request):
    mobile = request.GET.get("mobile", "").strip()
    date1 = request.GET.get("date1", "").strip()
    appointments = Appointment.objects.none()
    searched = False
    message = ""

    if mobile or date1:
        searched = True

    if mobile and date1:
        appointments = (
            Appointment.objects.select_related("doctor", "patient")
            .filter(patient__mobile__iexact=mobile, date1=date1)
            .order_by("time1")
        )
        if not appointments.exists():
            message = "No appointments found for the provided mobile number and date."
    elif searched:
        message = "Please provide both mobile number and appointment date to track status."

    data = {
        "appointments": appointments,
        "mobile": mobile,
        "date1": date1,
        "searched": searched,
        "message": message,
    }
    return render(request, "user_appointment_status.html", data)


@staff_required
def Index(request):
    d1 = {
        'd': Doctor.objects.count(),
        'p': Patient.objects.count(),
        'a': Appointment.objects.count(),
    }
    return render(request, 'index.html', d1)

def Login(request):
    error=""
    if request.method=='POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u,password=p)
        try:
            if user.is_staff:
                login(request,user)
                error="yes"
            else:
                error = "not"
        except:
            error = "not"
    d = {'error':error}
    return render(request, 'login.html',d)

def Logout_admin(request):
    logout(request)
    return redirect('user_home')


@staff_required
def View_Doctor(request):
    query = request.GET.get("q", "").strip()
    specialization = request.GET.get("specialization", "").strip()

    doc = Doctor.objects.all().order_by("name")
    if query:
        doc = doc.filter(
            Q(name__icontains=query)
            | Q(mobile__icontains=query)
            | Q(department__icontains=query)
            | Q(qualification__icontains=query)
        )
    if specialization:
        doc = doc.filter(special__icontains=specialization)

    d = {
        'doc': doc,
        'q': query,
        'specialization': specialization,
    }
    return render(request, 'view_doctor.html', d)


@staff_required
def Add_Doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_doctor')
    else:
        form = DoctorForm()
    return render(request, 'add_doctor.html', {'form': form})


@staff_required
def Edit_Doctor(request, pid):
    doctor = get_object_or_404(Doctor, id=pid)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('view_doctor')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'edit_doctor.html', {'form': form, 'doctor': doctor})


@staff_required
def Delete_Doctor(request,pid):
    doctor = get_object_or_404(Doctor, id=pid)
    if request.method == 'POST':
        doctor.delete()
    return redirect('view_doctor')



@staff_required
def View_Patient(request):
    query = request.GET.get("q", "").strip()
    mobile = request.GET.get("mobile", "").strip()

    pat = Patient.objects.all().order_by("name")
    if query:
        pat = pat.filter(name__icontains=query)
    if mobile:
        pat = pat.filter(mobile__icontains=mobile)

    d = {
        'pat': pat,
        'q': query,
        'mobile': mobile,
    }
    return render(request, 'view_patient.html', d)


@staff_required
def Add_Patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_patient')
    else:
        form = PatientForm()

    return render(request, 'add_patient.html', {'form': form})


@staff_required
def Edit_Patient(request, pid):
    patient = get_object_or_404(Patient, id=pid)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('view_patient')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'edit_patient.html', {'form': form, 'patient': patient})


@staff_required
def Delete_Patient(request,pid):
    patient = get_object_or_404(Patient, id=pid)
    if request.method == 'POST':
        patient.delete()
    return redirect('view_patient')



@staff_required
def View_Appointment(request):
    date1 = request.GET.get("date", "").strip()
    doctor_id = request.GET.get("doctor", "").strip()
    status = request.GET.get("status", "").strip()

    appoint = Appointment.objects.select_related("doctor", "patient").order_by("-date1", "time1")
    if date1:
        appoint = appoint.filter(date1=date1)
    if doctor_id:
        appoint = appoint.filter(doctor_id=doctor_id)
    if status:
        appoint = appoint.filter(status=status)

    d = {
        'appoint': appoint,
        'doctors': Doctor.objects.all().order_by("name"),
        'statuses': AppointmentStatus.choices,
        'selected_date': date1,
        'selected_doctor': doctor_id,
        'selected_status': status,
    }
    return render(request, 'view_appointment.html', d)


@staff_required
def Add_Appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_appointment')
    else:
        form = AppointmentForm()

    return render(request, 'add_appointment.html', {'form': form})


@staff_required
def Edit_Appointment(request, pid):
    appointment = get_object_or_404(Appointment, id=pid)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('view_appointment')
    else:
        form = AppointmentForm(instance=appointment)
    return render(
        request,
        'edit_appointment.html',
        {'form': form, 'appointment': appointment},
    )





@staff_required
def Delete_Appointment(request,pid):
    appointment = get_object_or_404(Appointment, id=pid)
    if request.method == 'POST':
        appointment.delete()
    return redirect('view_appointment')




    
