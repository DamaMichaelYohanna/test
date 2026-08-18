import os
import sys
from decimal import Decimal

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'material_logistics.settings')
import django
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from projects.models import Project, ProjectCategory, FeeType, ProjectFee, ProjectAllocation
from contractors.models import Subcontractor

def load_bcda_projects():
    # Ensure category exists
    cat_construction, _ = ProjectCategory.objects.get_or_create(name='Construction', defaults={'description': 'Construction Projects'})

    # Ensure fee types exist
    fee_facilitation, _ = FeeType.objects.get_or_create(name='Facilitation Fee (PR)', defaults={'description': 'Facilitation Fee (PR)'})
    fee_logistics, _ = FeeType.objects.get_or_create(name='Logistics and Monitoring', defaults={'description': 'Logistics and Monitoring Fee (10% of Contract Amount)'})
    fee_tender, _ = FeeType.objects.get_or_create(name='Tender Fee', defaults={'description': 'Tender / Processing Fee'})

    # Staff mapping
    cs_user, _ = User.objects.get_or_create(username='CS', defaults={'first_name': 'CS', 'is_staff': True})
    eta_user, _ = User.objects.get_or_create(username='ETA', defaults={'first_name': 'ETA', 'is_staff': True})
    amo_user, _ = User.objects.get_or_create(username='A.M.O', defaults={'first_name': 'A.M.O', 'is_staff': True})

    user_map = {
        'CS': cs_user,
        'ETA': eta_user,
        'A.M.O': amo_user,
    }

    projects_data = [
        {
            "sn_orig": 1,
            "mda": "BORDER COMMUNITIES DEVELOPMENT AGENCY (BCDA)",
            "project_code": "ERGP20261818",
            "project_name": "CONSTRUCTION OF LECTURE THEATRE AND SCIENCE AUDITORIUM AND LANDSCAPING AT INSTITUTE OF CONTINUED EDUCATION AND E-LEARNING PAIKO.",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EZz4QsAkJt1BoT9RhOnSnm4BaYvkfTzh7w-Jz_W8lR8XwA?e=0ZscHr",
            "drawing_design": "https://azanigroupn.sharepoint.com/:b:/s/teams/IQBpuDTbUAR1TqsH0spinB5uAUzecwZkK60_Hd6Ne3mZsQk?e=KsgUjU",
            "type_str": "ONGOING",
            "project_type": "CONSTRUCTION",
            "location": "PAIKO",
            "category_obj": cat_construction,
            "budget_amount": Decimal("400000000.00"),
            "actual_contract_amount": Decimal("0.00"),
            "facilitation_fee": Decimal("120000.00"),
            "logistics_fee": Decimal("0.00"),
            "tender_fee": Decimal("0.00"),
            "in_house_benchmark": Decimal("140000000.00"),
            "cost_percentage": Decimal("35.00"),
            "staff_key": "ETA",
            "subcontractor": "UMMARU ISHAQ",
            "lot": "",
            "final_companies": "***CHELIXIR NIG LTD- (OFFICE)",
            "comments": "PENDING AWARD LETTER FROM THE AGENCY. 3 AWARD LETTER RECEIVED",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EZz4QsAkJt1BoT9RhOnSnm4BaYvkfTzh7w-Jz_W8lR8XwA?e=0ZscHr\nDrawing: https://azanigroupn.sharepoint.com/:b:/s/teams/IQBpuDTbUAR1TqsH0spinB5uAUzecwZkK60_Hd6Ne3mZsQk?e=KsgUjU\nSubcontractor Drawing: https://azanigroupn.sharepoint.com/:b:/s/teams/IQBpuDTbUAR1TqsH0spinB5uAUzecwZkK60_Hd6Ne3mZsQk?e=KsgUjU\nSubcontractor Price BOQ: https://azanigroupn.sharepoint.com/:x:/s/teams/IQDTY9c5bfssT5DOe8KCJJjiAQuFtBGDmcsKnkJtCJsbxSg?e=enEHGL\nPROJECT CONTINUED FROM SEDI-M (2024) TO BCDA (2025). BCDA SAYS THE WORK DOES NOT ALIGN WITH THEIR DRAWING/DESIGN FOR 2025. PRINCIPAL TO INTERVENE. (MD TO REMIND PRINCIPAL)"
        },
        {
            "sn_orig": 2,
            "mda": "BORDER COMMUNITIES DEVELOPMENT AGENCY (BCDA)",
            "project_code": "ERGP20261819",
            "project_name": "ROAD REHABILITATION OF SELECTED KAGARA COMMUNITY ROADS (ASPHALT) AND GWADA, NIGER STATE.",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EWRC2Q9FcMJKqNI4e1n1K2ABJ5-Fj9RUlgVqQ6bhu3M4gA?e=3F6oP9",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/IQBzB0gn62PXRp-zh2wCsdceAf4E1MXecPtqArLKi6AC54w?e=d3eZbj",
            "type_str": "ONGOING",
            "project_type": "CONSTRUCTION",
            "location": "KAGARA, GWADA",
            "category_obj": cat_construction,
            "budget_amount": Decimal("300000000.00"),
            "actual_contract_amount": Decimal("298222358.75"),
            "facilitation_fee": Decimal("120000.00"),
            "logistics_fee": Decimal("29822235.88"),
            "tender_fee": Decimal("447333.54"),
            "batch_no_mobilization": "1001465295 (30% OF 30%)",
            "in_house_benchmark": Decimal("105000000.00"),
            "cost_percentage": Decimal("35.00"),
            "staff_key": "CS",
            "subcontractor": "UMAR SANI",
            "lot": "",
            "final_companies": "MAIKWATO GLOBAL RESOURCES LIMITED- (ALH. SULEYMAN)",
            "comments": "",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EWRC2Q9FcMJKqNI4e1n1K2ABJ5-Fj9RUlgVqQ6bhu3M4gA?e=3F6oP9\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/IQBzB0gn62PXRp-zh2wCsdceAf4E1MXecPtqArLKi6AC54w?e=d3eZbj"
        },
        {
            "sn_orig": 3,
            "mda": "BORDER COMMUNITIES DEVELOPMENT AGENCY (BCDA)",
            "project_code": "ERGP20261820",
            "project_name": "PROVISION AND INSTALLATION OF WATER PIPES WITH ACCESSORIES FOR PAIKO WATER PROJECT CONSTRUCTION OF RETICULATION SYSTEM. NIGER EAST",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EXyLe7KTQDBLo2xtyFg0ie8Btc5jU7pvcRHx_kZD_RRhfg?e=mVvQuC",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/IQBRtCtmUfgJTZDLYSxu1SvfAQLSRdE-PloSYGNk2XwmaUI?e=rirnNG",
            "type_str": "ONGOING",
            "project_type": "CONSTRUCTION",
            "location": "PAIKO",
            "category_obj": cat_construction,
            "budget_amount": Decimal("500000000.00"),
            "actual_contract_amount": Decimal("498094534.00"),
            "facilitation_fee": Decimal("120000.00"),
            "logistics_fee": Decimal("49809453.40"),
            "tender_fee": Decimal("747141.80"),
            "batch_no_mobilization": "1001465442 (30% OF 30%)",
            "in_house_benchmark": Decimal("175000000.00"),
            "cost_percentage": Decimal("35.00"),
            "staff_key": "ETA",
            "subcontractor": "MUHAMMAD SK",
            "lot": "",
            "final_companies": "BLUE ELEMENT LTD -(MUHAMMED SK)",
            "comments": "",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EXyLe7KTQDBLo2xtyFg0ie8Btc5jU7pvcRHx_kZD_RRhfg?e=mVvQuC\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/IQBRtCtmUfgJTZDLYSxu1SvfAQLSRdE-PloSYGNk2XwmaUI?e=rirnNG"
        },
        {
            "sn_orig": 4,
            "mda": "BORDER COMMUNITIES DEVELOPMENT AGENCY (BCDA)",
            "project_code": "ERGP20262159",
            "project_name": "CONSTRUCTION OF 4NOS 50 BED MODERN DIAGNOSTIC MEDICAL CENTER IN RAFI (KAGARA), /MAKERA MINNA,/ IJAH GWARI AND BOSSO (MAIKUNKELE) A",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/IQCrVc4Ewnw2Q5x7u0bkUlD_AXHPxIVz4_ClqZO4rvI9rjQ?e=W4WLGv",
            "type_str": "NEW",
            "project_type": "CONSTRUCTION",
            "location": "RAFI (KAGARA), MAKERA MINNA, IJAH GWARI, BOSSO (MAIKUNKELE)",
            "category_obj": cat_construction,
            "budget_amount": Decimal("420000000.00"),
            "actual_contract_amount": Decimal("419781976.20"),
            "facilitation_fee": Decimal("120000.00"),
            "logistics_fee": Decimal("41978197.62"),
            "tender_fee": Decimal("0.00"),
            "in_house_benchmark": Decimal("0.00"),
            "cost_percentage": Decimal("0.00"),
            "staff_key": "ETA",
            "subcontractor": "UMMARU ISHAQ/MUHAMMAD SK",
            "lot": "",
            "final_companies": "M&W RESOURCES LIMITED - (YARIMA)",
            "comments": "",
            "remarks": "Award Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/IQCrVc4Ewnw2Q5x7u0bkUlD_AXHPxIVz4_ClqZO4rvI9rjQ?e=W4WLGv"
        },
        {
            "sn_orig": 5,
            "mda": "BORDER COMMUNITIES DEVELOPMENT AGENCY (BCDA)",
            "project_code": "ERGP20262160",
            "project_name": "REHABILITATION AND THE FURNISHING OF THE OFFICIAL PALACE OF THE DISTRICT HEAD OF PAIKO, NIGER STATE",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/Ef6XMWp-VNlBnufLpjHhzbUBU36C5j8lrhpS-fevFzWwtA?e=IGL4py",
            "drawing_design": "https://azanigroupn.sharepoint.com/:b:/s/teams/IQD_cdssaz5jR4bBtfoixehVASFUVlCdXuyWLD5CtcBwXas?e=5GXIMS",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/ETS2Ww9G1PlMvaCSAJpxN6oBIWwKQA9rL-mCgEKBI_peeg?e=5yC25K",
            "type_str": "NEW",
            "project_type": "CONSTRUCTION",
            "location": "PAIKO",
            "category_obj": cat_construction,
            "budget_amount": Decimal("500000000.00"),
            "actual_contract_amount": Decimal("482979157.77"),
            "facilitation_fee": Decimal("120000.00"),
            "logistics_fee": Decimal("48297915.78"),
            "tender_fee": Decimal("0.00"),
            "batch_no_mobilization": "1001426850",
            "in_house_benchmark": Decimal("169042705.22"),
            "cost_percentage": Decimal("35.00"),
            "staff_key": "A.M.O",
            "subcontractor": "YARIMA",
            "lot": "LOT B 167",
            "final_companies": "GRAND LEGEND PLUS LTD - (OFFICE)",
            "comments": "",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/Ef6XMWp-VNlBnufLpjHhzbUBU36C5j8lrhpS-fevFzWwtA?e=IGL4py\nDrawing: https://azanigroupn.sharepoint.com/:b:/s/teams/IQD_cdssaz5jR4bBtfoixehVASFUVlCdXuyWLD5CtcBwXas?e=5GXIMS\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/ETS2Ww9G1PlMvaCSAJpxN6oBIWwKQA9rL-mCgEKBI_peeg?e=5yC25K"
        }
    ]

    created_projects = []

    with transaction.atomic():
        for item in projects_data:
            staff_obj = user_map.get(item['staff_key']) if item['staff_key'] else None
            
            proj = Project.objects.filter(
                project_code=item['project_code'],
                mda=item['mda']
            ).first()

            if not proj:
                proj = Project(
                    mda=item['mda'],
                    project_code=item['project_code'],
                    project_name=item['project_name'],
                    lot=item['lot'],
                    project_type=item['project_type'],
                    location=item['location'],
                    category=item['category_obj'],
                    budget_amount=item['budget_amount'],
                    actual_contract_amount=item['actual_contract_amount'],
                    in_house_benchmark=item['in_house_benchmark'],
                    mobilization_received=Decimal("0.00"),
                    batch_no_mobilization=item.get('batch_no_mobilization', ''),
                    cost_percentage=item['cost_percentage'],
                    staff_assigned=staff_obj,
                    execution_mode='SUBCONTRACTED' if item['subcontractor'] else 'SELF_EXECUTED',
                    current_phase='POST_AWARD',
                    project_status='Awarded',
                    payment_status='Pending',
                    plain_boq='',
                    award_letter_and_boq='',
                    final_companies=item['final_companies'],
                    comments=item['comments'],
                    remarks=item['remarks']
                )
                proj.save()
                print(f"Created BCDA Project #{proj.sn}: {proj.project_code} - {proj.project_name[:40]}...", flush=True)
            else:
                proj.mda = item['mda']
                proj.project_name = item['project_name']
                proj.project_type = item['project_type']
                proj.location = item['location']
                proj.category = item['category_obj']
                proj.budget_amount = item['budget_amount']
                proj.actual_contract_amount = item['actual_contract_amount']
                proj.in_house_benchmark = item['in_house_benchmark']
                proj.mobilization_received = Decimal("0.00")
                proj.batch_no_mobilization = item.get('batch_no_mobilization', '')
                proj.cost_percentage = item['cost_percentage']
                proj.staff_assigned = staff_obj
                proj.execution_mode = 'SUBCONTRACTED' if item['subcontractor'] else 'SELF_EXECUTED'
                proj.current_phase = 'POST_AWARD'
                proj.project_status = 'Awarded'
                proj.payment_status = 'Pending'
                proj.final_companies = item['final_companies']
                proj.comments = item['comments']
                proj.remarks = item['remarks']
                proj.lot = item['lot']
                proj.save()
                print(f"Updated BCDA Project #{proj.sn}: {proj.project_code}", flush=True)

            created_projects.append(proj)

            # Facilitation Fee = 120,000.00
            ProjectFee.objects.update_or_create(
                project=proj,
                fee_type=fee_facilitation,
                defaults={'amount': item['facilitation_fee']}
            )

            # Logistics Fee = 10% of contract amount
            if item['logistics_fee'] > 0:
                ProjectFee.objects.update_or_create(
                    project=proj,
                    fee_type=fee_logistics,
                    defaults={'amount': item['logistics_fee']}
                )

            # Tender Fee if applicable
            if item['tender_fee'] > 0:
                ProjectFee.objects.update_or_create(
                    project=proj,
                    fee_type=fee_tender,
                    defaults={'amount': item['tender_fee']}
                )

            # Handle Subcontractor allocation
            if item.get('subcontractor'):
                sub_name = item['subcontractor']
                sub_obj, _ = Subcontractor.objects.get_or_create(
                    name=sub_name,
                    defaults={'company_type': 'EXTERNAL'}
                )
                ProjectAllocation.objects.get_or_create(
                    project=proj,
                    subcontractor=sub_obj
                )

    # Ensure all BCDA projects have created_at set to 2025
    import datetime
    dt_2025 = datetime.datetime(2025, 6, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    Project.objects.filter(mda='BORDER COMMUNITIES DEVELOPMENT AGENCY (BCDA)').update(created_at=dt_2025)

    print(f"Successfully loaded {len(created_projects)} BCDA projects into database for year 2025!", flush=True)

load_bcda_projects()
