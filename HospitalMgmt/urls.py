"""
URL configuration for HospitalMgmt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital.views import*

urlpatterns = [
    path('admin/dashboard/', Index, name='admin_home'),
    path('admin/', admin.site.urls),

    path('', User_Root, name='home'),
    path('user/login/', User_Login, name='user_login'),
    path('user/register/', User_Register, name='user_register'),
    path('user/dashboard/', User_Home, name='user_home'),
    path('find-doctor/', User_Find_Doctor, name='find_doctor'),
    path('book-appointment/<int:doctor_id>/', User_Book_Appointment, name='book_appointment_user'),
    path('my-appointment-status/', User_Appointment_Status, name='my_appointment_status'),

    path('about/', About,name='about'),
    path('contact/', Contact,name='contact'),
    path('dashboard/', Index, name='admin_dashboard_legacy'),
    path('admin_login/', Login,name='login'),
    path('logout/', Logout_admin,name='logout'),

    path('view_doctor/', View_Doctor,name='view_doctor'),
    path('add_doctor/', Add_Doctor,name='add_doctor'),
    path('doctor/<int:pid>/edit/', Edit_Doctor,name='edit_doctor'),
    path('doctor/<int:pid>/delete/', Delete_Doctor,name='delete_doctor'),

    path('view_patient/', View_Patient,name='view_patient'),
    path('add_patient/', Add_Patient,name='add_patient'),
    path('patient/<int:pid>/edit/', Edit_Patient,name='edit_patient'),
    path('patient/<int:pid>/delete/', Delete_Patient,name='delete_patient'),

    path('view_appointment/', View_Appointment,name='view_appointment'),
    path('add_appointment/', Add_Appointment,name='add_appointment'),
    path('appointment/<int:pid>/edit/', Edit_Appointment,name='edit_appointment'),
    path('appointment/<int:pid>/delete/', Delete_Appointment,name='delete_appointment'),

]
