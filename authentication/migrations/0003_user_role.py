# Generated by Django 4.1.4 on 2023-01-07 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_user_sex'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('hr', 'hr'), ('employee', 'employee'), ('unknown', 'unknown')], default='unknown', max_length=8),
        ),
    ]
