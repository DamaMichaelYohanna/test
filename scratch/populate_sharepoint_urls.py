import os
import sys
import re

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'material_logistics.settings')
import django
django.setup()

from projects.models import Project

def populate_urls():
    projects = Project.objects.all()
    updated_count = 0

    for proj in projects:
        remarks = proj.remarks or ''
        comments = proj.comments or ''
        text_block = f"{remarks}\n{comments}"

        boq_url = None
        drawing_url = None
        award_url = None

        for line in text_block.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            # Extract URL if present
            m_md = re.search(r'\[(.*?)\]\((https?://[^\s\)]+)\)', line_str)
            m_raw = re.search(r'(https?://[^\s]+)', line_str)

            url = m_md.group(2) if m_md else (m_raw.group(1) if m_raw else None)
            if not url:
                continue

            line_lower = line_str.lower()
            if 'subcontractor' in line_lower:
                continue  # skip subcontractor drawings/boqs

            if ('award' in line_lower or 'letter' in line_lower):
                award_url = url
            elif ('drawing' in line_lower or 'design' in line_lower):
                drawing_url = url
            elif ('boq' in line_lower):
                boq_url = url

        # Update project fields
        changed = False
        if boq_url and proj.plain_boq != boq_url:
            proj.plain_boq = boq_url
            changed = True
        if drawing_url and proj.drawing_design != drawing_url:
            proj.drawing_design = drawing_url
            changed = True
        if award_url and proj.award_letter_and_boq != award_url:
            proj.award_letter_and_boq = award_url
            changed = True

        if changed:
            proj.save()
            updated_count += 1
            print(f"Updated Project #{proj.sn} ({proj.project_code}):", flush=True)
            print(f"  Plain BOQ: {proj.plain_boq}", flush=True)
            print(f"  Drawing: {proj.drawing_design}", flush=True)
            print(f"  Award Letter: {proj.award_letter_and_boq}", flush=True)

    print(f"\nDone! Updated SharePoint document links for {updated_count} projects.", flush=True)

if __name__ == '__main__':
    populate_urls()
