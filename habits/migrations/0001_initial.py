import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('icon', models.CharField(default='droplet', help_text='Icon key used by the template', max_length=40)),
                ('color', models.CharField(default='accent', max_length=20)),
                ('frequency', models.CharField(choices=[('daily', 'Every day'), ('weekdays', 'Weekdays'), ('weekly', 'Specific days')], default='daily', max_length=10)),
                ('goal_per_day', models.PositiveIntegerField(default=1, help_text='e.g. glasses of water')),
                ('reminder_time', models.TimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='habits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HabitLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.localdate)),
                ('completed', models.BooleanField(default=False)),
                ('habit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='habits.habit')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('habit', 'date')},
            },
        ),
    ]
