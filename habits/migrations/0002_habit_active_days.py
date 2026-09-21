from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='active_days',
            field=models.CharField(
                blank=True, default='', max_length=20,
                help_text="Comma-separated weekday numbers (0=Mon..6=Sun), used when frequency='weekly'",
            ),
        ),
    ]
