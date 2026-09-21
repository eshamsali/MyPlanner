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
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('icon', models.CharField(default='🎯', max_length=10)),
                ('category', models.CharField(choices=[('university', 'University'), ('work', 'Work'), ('personal', 'Personal'), ('health', 'Health'), ('finance', 'Finance')], default='personal', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('is_achieved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['deadline', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('is_completed', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='goals.goal')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]
