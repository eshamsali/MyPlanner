import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('system', 'System')], default='light', max_length=10)),
                ('accent_color', models.CharField(choices=[('purple', 'Purple'), ('pink', 'Pink'), ('blue', 'Blue'), ('green', 'Green'), ('orange', 'Orange')], default='purple', max_length=10)),
                ('language', models.CharField(choices=[('en', 'English'), ('ar', 'العربية')], default='en', max_length=5)),
                ('font_size', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium', max_length=10)),
                ('week_start', models.CharField(choices=[('mon', 'Monday'), ('sat', 'Saturday'), ('sun', 'Sunday')], default='mon', max_length=3)),
                ('time_format_24h', models.BooleanField(default=False)),
                ('task_reminders', models.BooleanField(default=True)),
                ('habit_reminders', models.BooleanField(default=True)),
                ('goal_reminders', models.BooleanField(default=True)),
                ('daily_planning_reminder', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
