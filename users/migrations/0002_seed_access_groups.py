from django.db import migrations


def create_level_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ('Level 1', 'Level 2', 'Level 3', 'Level 4'):
        Group.objects.get_or_create(name=name)


def delete_level_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=('Level 1', 'Level 2', 'Level 3', 'Level 4')).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_level_groups, delete_level_groups),
    ]
