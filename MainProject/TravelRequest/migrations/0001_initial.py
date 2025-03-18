# Generated by Django 4.2 on 2025-03-06 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Employees',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Managers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TravelRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateField(blank=True, null=True)),
                ('to_date', models.DateField(blank=True, null=True)),
                ('location', models.CharField(max_length=100)),
                ('destination', models.CharField(max_length=100)),
                ('travel_mode', models.CharField(max_length=50)),
                ('lodging_required', models.BooleanField(default=False)),
                ('purpose_of_travel', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('FI_required', 'Further Information Required'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('closed', 'Closed')], default='pending', max_length=20)),
                ('manager_note', models.TextField(blank=True, null=True)),
                ('admin_note', models.TextField(blank=True, null=True)),
                ('further_information', models.TextField(blank=True, null=True)),
                ('resubmission_count', models.IntegerField(default=0)),
                ('is_closed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TravelRequest.employees')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TravelRequest.managers')),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests_processed', to='TravelRequest.admins')),
            ],
        ),
        migrations.AddField(
            model_name='employees',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees_managed', to='TravelRequest.managers'),
        ),
    ]
