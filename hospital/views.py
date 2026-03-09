from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .forms import DoctorForm, PatientForm, AppointmentForm
# Create your views here.


def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="login",
    )(view_func)


def About(request):
    return render(request, 'about.html')


def Contact(request):
    return render(request, 'contact.html')


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
    return redirect('login')


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




    
