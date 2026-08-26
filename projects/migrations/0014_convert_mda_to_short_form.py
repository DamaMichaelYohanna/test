import re
from django.db import migrations

def extract_short_mda(mda_val):
    if not mda_val:
        return ""
    mda_str = str(mda_val).strip()
    if 'HOUSING AND URBAN DEVELOPMENT' in mda_str.upper():
        return 'FMHUD'
    if 'NIGERIA STORED PRODUCTS RESEARCH' in mda_str.upper():
        return 'NSPRI'
    
    matches = re.findall(r'\(([A-Za-z0-9\s\-]+)\)', mda_str)
    if matches:
        acronyms = [x.strip() for x in matches if len(x.strip()) <= 15 and 'SPECIAL' not in x.upper() and 'MINISTRY' not in x.upper()]
        if acronyms:
            return acronyms[0]
        return matches[0].strip()
    return mda_str

def convert_mda_to_short_form(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    for project in Project.objects.all():
        if project.mda:
            short = extract_short_mda(project.mda)
            if short and short != project.mda:
                project.mda = short
                project.save(update_fields=['mda'])

def reverse_convert_mda(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_projectactivitylog'),
    ]

    operations = [
        migrations.RunPython(convert_mda_to_short_form, reverse_convert_mda),
    ]
