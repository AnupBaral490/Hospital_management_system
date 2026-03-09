from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hospital", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doctor",
            name="mobile",
            field=models.CharField(max_length=20),
        ),
        migrations.AddField(
            model_name="doctor",
            name="department",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="doctor",
            name="qualification",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="doctor",
            name="experience_years",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="doctor",
            name="availability_schedule",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="patient",
            name="mobile",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="patient",
            name="dob",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="patient",
            name="blood_group",
            field=models.CharField(
                blank=True,
                choices=[
                    ("A+", "A+"),
                    ("A-", "A-"),
                    ("B+", "B+"),
                    ("B-", "B-"),
                    ("AB+", "AB+"),
                    ("AB-", "AB-"),
                    ("O+", "O+"),
                    ("O-", "O-"),
                ],
                max_length=5,
            ),
        ),
        migrations.AddField(
            model_name="patient",
            name="emergency_contact",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="patient",
            name="allergies",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="patient",
            name="medical_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[
                    ("scheduled", "Scheduled"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                    ("no_show", "No Show"),
                ],
                default="scheduled",
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="appointment",
            constraint=models.UniqueConstraint(
                fields=("doctor", "date1", "time1"),
                name="unique_doctor_time_slot",
            ),
        ),
    ]
