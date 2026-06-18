# Generated manually for the users app.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g., Group Managing Director, Civil Engineer, Procurement Specialist', max_length=100, unique=True)),
                ('permission_group', models.ForeignKey(help_text='Which foundational access level does this title map to?', on_delete=django.db.models.deletion.PROTECT, related_name='job_titles', to='auth.group')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Job Title',
                'verbose_name_plural': 'Job Titles',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('job_title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='users.jobtitle')),
                ('last_active_project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.project')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
