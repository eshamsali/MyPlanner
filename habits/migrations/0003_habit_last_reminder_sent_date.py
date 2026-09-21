from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0002_habit_active_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='last_reminder_sent_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
