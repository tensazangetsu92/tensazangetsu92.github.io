# Generated by Django 5.1.1 on 2024-10-04 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='task_manager_db',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_text', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deadline_at', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
