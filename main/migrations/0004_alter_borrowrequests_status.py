# Generated by Django 5.0.6 on 2024-07-14 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_borrowrequests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowrequests',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending', max_length=20),
        ),
    ]
