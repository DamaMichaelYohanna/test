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

def load_nde_projects():
    # Ensure categories exist
    cat_training, _ = ProjectCategory.objects.get_or_create(name='Training', defaults={'description': 'Training Projects'})
    cat_supply, _ = ProjectCategory.objects.get_or_create(name='Supply', defaults={'description': 'Supply Projects'})
    cat_construction, _ = ProjectCategory.objects.get_or_create(name='Construction', defaults={'description': 'Construction Projects'})

    cat_map = {
        'TRAINING': cat_training,
        'SUPPLY': cat_supply,
        'CONSTRUCTION': cat_construction,
    }

    # Ensure fee types exist
    fee_admin, _ = FeeType.objects.get_or_create(name='Admin Fee', defaults={'description': 'Administrative Fee'})
    fee_facilitation, _ = FeeType.objects.get_or_create(name='Facilitation Fee (PR)', defaults={'description': 'Facilitation Fee (PR)'})
    fee_logistics, _ = FeeType.objects.get_or_create(name='Logistics and Monitoring', defaults={'description': 'Logistics and Monitoring Fee (10% of Contract Amount)'})

    # Staff mapping
    dmy_user = User.objects.filter(username='dama@azani').first()
    aim_user = User.objects.filter(username='monday@azani').first()
    
    cs_user, _ = User.objects.get_or_create(username='CS', defaults={'first_name': 'CS', 'is_staff': True})
    as_user, _ = User.objects.get_or_create(username='AS', defaults={'first_name': 'AS', 'is_staff': True})

    user_map = {
        'CS': cs_user,
        'AIM': aim_user,
        'AS': as_user,
        'DMY': dmy_user,
    }

    projects_data = [
        {
            "sn_orig": 1,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261799",
            "project_name": "PROVISION OF EDUCATIONAL GRANT TO INDIGENT STUDENTS TO SUPPORT LEARNING IN ICT IN NIGER EAST SENATORIAL DISTRICT (A)",
            "part_name": "Part A",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/Ec2N9q-fl4BBsjoIxCtgX-gB75DmmmIwBncBr1EFHqvWQg?e=pqk5cp",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EU4AW50agyNHvaa8e0ANuhkBHETt-SixMfpDdzoB50O18w?e=8eJXfZ",
            "type_str": "NEW*",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "TRAINING",
            "budget_amount": Decimal("100000000.00"),
            "actual_contract_amount": Decimal("95000000.00"),
            "in_house_benchmark": Decimal("25441000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": "1001438811",
            "cost_percentage": Decimal("26.78"),
            "staff_key": "CS",
            "subcontractor": "YARIMA",
            "lot": "LOT C25",
            "final_companies": "TRADEVAULT ENTERPRISES LTD - (YARIMA)",
            "updated_recommended_companies": "TRADEVAULT ENTERPRISES(C25)",
            "comments": "AWARD LETTERS AND BOQs RECEIVED, MOBILIZATION HAS BEEN REQUESTED FOR ONE PROJECT (EMPTECH)",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/Ec2N9q-fl4BBsjoIxCtgX-gB75DmmmIwBncBr1EFHqvWQg?e=pqk5cp\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/EU4AW50agyNHvaa8e0ANuhkBHETt-SixMfpDdzoB50O18w?e=8eJXfZ"
        },
        {
            "sn_orig": 2,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261799",
            "project_name": "PROVISION OF EDUCATIONAL GRANT TO INDIGENT STUDENTS TO SUPPORT LEARNING IN MATHEMATICS AND SCIENCE EDUCATION IN NIGER EAST SENATORIAL DISTRICT (B)",
            "part_name": "Part B",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EUA8iNw2lepKnvnK8r5wt6oBKEDZSkBq7WLdKsJof4OhsQ?e=Isws6q",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EXnDId45MK5Lv78yRB3Fx2EBWR-h-PsUZ7Mf0-aY-uumgw?e=EYtxqb",
            "type_str": "NEW*",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "TRAINING",
            "budget_amount": Decimal("100000000.00"),
            "actual_contract_amount": Decimal("95000000.00"),
            "in_house_benchmark": Decimal("25441000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": "1001438810",
            "cost_percentage": Decimal("26.78"),
            "staff_key": "CS",
            "subcontractor": "YARIMA",
            "lot": "LOT C26",
            "final_companies": "NAS CAPITAL - (YARIMA)",
            "updated_recommended_companies": "NAS CAPITAL LTD (C26)",
            "comments": "",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EUA8iNw2lepKnvnK8r5wt6oBKEDZSkBq7WLdKsJof4OhsQ?e=Isws6q\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/EXnDId45MK5Lv78yRB3Fx2EBWR-h-PsUZ7Mf0-aY-uumgw?e=EYtxqb"
        },
        {
            "sn_orig": 3,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261801",
            "project_name": "VOCATIONAL TECHNICAL TRAINING AND SKILL ACQUISITION FOR YOUNG GRADUATES AND PROVISION OF STARTER PACKS TO WOMEN AND YOUTHS IN NIGER EAST SENATORIAL DISTRICT (A)",
            "part_name": "Part A",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/Ec7xBUytbjNLtQAU5KmFuCIBsI8QYBD7kJ2_ljuk1rlS2Q?e=lGWf3D",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EaNvVywAR9pMp3o46z6U1tsB79S1RW07Ez9fBfAonOWw6w?e=VVuK89",
            "type_str": "NEW *",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "TRAINING",
            "budget_amount": Decimal("60000000.00"),
            "actual_contract_amount": Decimal("57000000.00"),
            "in_house_benchmark": Decimal("20531000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("36.02"),
            "staff_key": "CS",
            "subcontractor": "YARIMA",
            "lot": "LOT C27",
            "final_companies": "ALMOND AND OAK LTD - (OFFICE)",
            "updated_recommended_companies": "",
            "comments": "",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/Ec7xBUytbjNLtQAU5KmFuCIBsI8QYBD7kJ2_ljuk1rlS2Q?e=lGWf3D\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/EaNvVywAR9pMp3o46z6U1tsB79S1RW07Ez9fBfAonOWw6w?e=VVuK89"
        },
        {
            "sn_orig": 4,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261801",
            "project_name": "PROVISION OF STARTER PACKS TO WOMEN IN NIGER EAST SENATORIAL DISTRICT (B)",
            "part_name": "Part B",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/Eb95qeWYPPhOmpfB_pQS3OUBoez6j0pbyLNWoInRrq3C4w?e=fwRffl",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EUfXJRWQwnRPrKSka-l8cTIBMLmEC8HIJ5uw0stsfRNk_w?e=T4AHKY",
            "type_str": "NEW*",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("95000000.00"),
            "actual_contract_amount": Decimal("90250000.00"),
            "in_house_benchmark": Decimal("35279000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": "1001438808",
            "cost_percentage": Decimal("39.09"),
            "staff_key": None,
            "subcontractor": "YARIMA",
            "lot": "A67",
            "final_companies": "DIGITEXPOINT CONCEPT LIMITED -(OFFICE)",
            "updated_recommended_companies": "RIFFSTINE NIGERIA LIMITED",
            "comments": "In-house cost breakdown: https://docs.google.com/spreadsheets/d/1UDr8b3D2-8_luH4QdPrJFKi-gObfkgAN/edit?gid=1634189543#gid=1634189543",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/Eb95qeWYPPhOmpfB_pQS3OUBoez6j0pbyLNWoInRrq3C4w?e=fwRffl\nAward Letter and BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EUfXJRWQwnRPrKSka-l8cTIBMLmEC8HIJ5uw0stsfRNk_w?e=T4AHKY"
        },
        {
            "sn_orig": 5,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261801",
            "project_name": "PROVISION OF STARTER PACKS TO YOUTHS IN NIGER EAST SENATORIAL DISTRICT (C)",
            "part_name": "Part C",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EQBrh9HsKYdOm6gGkuJ-J8UB5BSMmAXQkADtTE_AGtXORw?e=cVJKF1",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EYDpNFbN1oNAs0tFySniTd8B2tKJLZN-b8MEaHw1hCJHCg?e=fjkgTN",
            "type_str": "NEW *",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("95000000.00"),
            "actual_contract_amount": Decimal("90250000.00"),
            "in_house_benchmark": Decimal("37570000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("41.63"),
            "staff_key": "CS",
            "subcontractor": "YARIMA",
            "lot": "A68",
            "final_companies": "HASHTAG TECHNOLOGY LTD- (ISAAC)",
            "updated_recommended_companies": "HERITAGE PLUS MULTI CONCEPT LIMITED",
            "comments": "",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EQBrh9HsKYdOm6gGkuJ-J8UB5BSMmAXQkADtTE_AGtXORw?e=cVJKF1\nAward Letter and BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EYDpNFbN1oNAs0tFySniTd8B2tKJLZN-b8MEaHw1hCJHCg?e=fjkgTN"
        },
        {
            "sn_orig": 6,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261798",
            "project_name": "FURNISHINGS TO CBT CENTERS IN NIGER EAST SENATORIAL DISTRICT (A)",
            "part_name": "Part A",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EdTxlTW8tEJInfTxX1ZCxo8Bux0vlnnUEYSpAjj9o1lY2A?e=RhCPae",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EUkS9FQP5vdIpj_lOsgrdoABE-J67saB6Rbu6As8ru176g?e=HFqjrJ",
            "type_str": "NEW*",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("50000000.00"),
            "actual_contract_amount": Decimal("46075000.00"),
            "in_house_benchmark": Decimal("16280000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("35.33"),
            "staff_key": "CS",
            "subcontractor": "YARIMA",
            "lot": "A66",
            "final_companies": "SYNERSIS LINEAR- (YARIMA)",
            "updated_recommended_companies": "CHELIXIR",
            "comments": "In-house cost breakdown: https://docs.google.com/spreadsheets/d/1UDr8b3D2-8_luH4QdPrJFKi-gObfkgAN/edit?gid=1219121261#gid=1219121261",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EdTxlTW8tEJInfTxX1ZCxo8Bux0vlnnUEYSpAjj9o1lY2A?e=RhCPae\nAward Letter and BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EUkS9FQP5vdIpj_lOsgrdoABE-J67saB6Rbu6As8ru176g?e=HFqjrJ"
        },
        {
            "sn_orig": 7,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261798",
            "project_name": "SUPPLYOF COMPUTERS, PRINTERS, SOLAR PANELS AND INVERTERS, IPS AND OTHER IT EQUIPMENT TO CBT CENTERS IN NIGER EAST SENATORIAL DISTRICT (B)",
            "part_name": "Part B",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EVT7y-HtcDVLkyJstzy1rQoBwXnfBYO4FwCg5EHPdtNCQQ?e=5eZlq2",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EW3Js2qbS-xPqg7bUzgubIsB4aHYlphyGc6qitWRqVK2AA?e=ZqZdMh",
            "type_str": "NEW *",
            "project_type": "SUPPLY_TRAINING",
            "location": "NIGER EAST",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("95000000.00"),
            "actual_contract_amount": Decimal("89300000.00"),
            "in_house_benchmark": Decimal("62000000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": "1001438802",
            "cost_percentage": Decimal("69.43"),
            "staff_key": "AIM",
            "subcontractor": "ALHAJI BALARABE (SANTURAKI)",
            "lot": "A108",
            "final_companies": "LIGTH BOX TECHNOLOGY NIGERIA LIMITED -(YARIMA)",
            "updated_recommended_companies": "TAWMAN GLOBAL CONCEPTS NIGERIA LIMITED",
            "comments": "PROJECTS GIVEN TO ALHAJI BALARABE. In-house cost breakdown: https://docs.google.com/spreadsheets/d/1UDr8b3D2-8_luH4QdPrJFKi-gObfkgAN/edit?gid=1219121261#gid=1219121261",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EVT7y-HtcDVLkyJstzy1rQoBwXnfBYO4FwCg5EHPdtNCQQ?e=5eZlq2\nAward Letter and BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EW3Js2qbS-xPqg7bUzgubIsB4aHYlphyGc6qitWRqVK2AA?e=ZqZdMh"
        },
        {
            "sn_orig": 8,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20261798",
            "project_name": "CONSTRUCTION OF PERIMETER FENCING, GATE HOUSE AND BOREHOLE WITH OVERHEAD TANKS TO CBT CENTERS IN NIGER EAST SENATORIAL DISTRICT (C)",
            "part_name": "Part C",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EdKQc5bNddVGpRTL3uhsIkEBuKH1UzefTPK9s0bHwkMakw?e=R5FRgS",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/sites/teams/Shared%20Documents/ALL%20PROJECTS/NIGER/2025/NDE/AWARD%20LETTERS/Emptech%20NDE%202025%20.pdf",
            "type_str": "NEW *",
            "project_type": "CONSTRUCTION",
            "location": "NIGER EAST",
            "category_key": "CONSTRUCTION",
            "budget_amount": Decimal("55000000.00"),
            "actual_contract_amount": Decimal("50312500.00"),
            "in_house_benchmark": Decimal("17609375.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("35.00"),
            "staff_key": None,
            "subcontractor": "YARIMA",
            "lot": "B54",
            "final_companies": "EMPTECH TECHNOLOGIES NIGERIA LTD - (OFFICE)",
            "updated_recommended_companies": "M&W RESOURCES LIMITED",
            "comments": "AWARD LETTER RECEIVED AND MOBILIZATION HAS BEEN REQUESTED",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EdKQc5bNddVGpRTL3uhsIkEBuKH1UzefTPK9s0bHwkMakw?e=R5FRgS\nAward Letter: https://azanigroupn.sharepoint.com/sites/teams/Shared%20Documents/ALL%20PROJECTS/NIGER/2025/NDE/AWARD%20LETTERS/Emptech%20NDE%202025%20.pdf"
        },
        {
            "sn_orig": 9,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20262142",
            "project_name": "SUPPLYOF SEWING, GRINDING/ FOOD PROCESSING MACHINE FOR WOMEN IN P/KNUKNU (A)",
            "part_name": "Part A",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EQUhxmTBRa9Bk8iCIQWyxcEBRQzEdho3UK7vFKt1sLJ-2A?e=wa4yu3",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EbiVaCgx_WNLqwvVMGOyoCwBRUMQj4xZz95HYB_OpIBRyw?e=vps2jn",
            "type_str": "NEW *",
            "project_type": "SUPPLY_TRAINING",
            "location": "P/KNUKNU",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("100000000.00"),
            "actual_contract_amount": Decimal("95000000.00"),
            "in_house_benchmark": Decimal("33756000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("35.53"),
            "staff_key": "AIM",
            "subcontractor": "ALHAJI BALARABE (SANTURAKI)",
            "lot": "A112",
            "final_companies": "BAKUS MULTILINKS NIG LTD - (OFFICE)",
            "updated_recommended_companies": "SKD-GOLDEN GATE CONCEPT LIMITED",
            "comments": "PROJECT GIVEN TO ALHAJI BALARABE",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EQUhxmTBRa9Bk8iCIQWyxcEBRQzEdho3UK7vFKt1sLJ-2A?e=wa4yu3\nAward Letter and BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EbiVaCgx_WNLqwvVMGOyoCwBRUMQj4xZz95HYB_OpIBRyw?e=vps2jn"
        },
        {
            "sn_orig": 10,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20262142",
            "project_name": "SUPPLYOF SEWING, GRINDING/ FOOD PROCESSING MACHINE FOR WOMEN IN BONU (B)",
            "part_name": "Part B",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EauqkqYTQ5NGgVpP0ihUeXQB3tlVmwc5CINKaLBWJ_GgVw?e=9vOhwF",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/Ed4wjj_IwtBCo28HbRGRC2gBrirCQBhSIqhWbVq9Bp2nDQ?e=awoevn",
            "type_str": "NEW *",
            "project_type": "SUPPLY_TRAINING",
            "location": "BONU",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("100000000.00"),
            "actual_contract_amount": Decimal("95000000.00"),
            "in_house_benchmark": Decimal("33224000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("34.97"),
            "staff_key": "AS",
            "subcontractor": "GIVEN TO AGENCY",
            "lot": "A113",
            "final_companies": "DUNE ENERGY - (SUDAIS)",
            "updated_recommended_companies": "FIRETECH",
            "comments": "PROJECTS GIVEN AGENCY. In-house cost breakdown: https://docs.google.com/spreadsheets/d/1UDr8b3D2-8_luH4QdPrJFKi-gObfkgAN/edit?gid=2126037922#gid=2126037922",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EauqkqYTQ5NGgVpP0ihUeXQB3tlVmwc5CINKaLBWJ_GgVw?e=9vOhwF\nAward Letter: https://azanigroupn.sharepoint.com/:b:/s/teams/Ed4wjj_IwtBCo28HbRGRC2gBrirCQBhSIqhWbVq9Bp2nDQ?e=awoevn"
        },
        {
            "sn_orig": 11,
            "mda": "NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)",
            "project_code": "ERGP20262142",
            "project_name": "SUPPLYOF SEWING, GRINDING/ FOOD PROCESSING MACHINE FOR WOMEN IN GWAM AND ENVIRONS IN NIGER STATE (C)",
            "part_name": "Part C",
            "plain_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/EZ-B7rlOpK1GprnVY6z5DtUB5eOYE0XZLHQSlvevzSUpdA?e=arujAj",
            "award_letter_and_boq": "https://azanigroupn.sharepoint.com/:b:/s/teams/ERGSpvaXB9tHmBACFlPVVU4Bbpv-gJbnZJNAflH2mSJ5lg?e=t2aiHH",
            "type_str": "NEW *",
            "project_type": "SUPPLY_TRAINING",
            "location": "GWAM",
            "category_key": "SUPPLY",
            "budget_amount": Decimal("100000000.00"),
            "actual_contract_amount": Decimal("95000000.00"),
            "in_house_benchmark": Decimal("33808000.00"),
            "mobilization_received": Decimal("0.00"),
            "batch_no_mobilization": None,
            "cost_percentage": Decimal("35.59"),
            "staff_key": "DMY",
            "subcontractor": "ALHAJI BALARABE (SANTURAKI)",
            "lot": "A114",
            "final_companies": "ZEDMAN GLOBAL SERVICES - (OFFICE)",
            "updated_recommended_companies": "TRADEVAULT ENTERPRISES",
            "comments": "PROJECTS GIVEN TO ALHAJI BALARABE",
            "remarks": "BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/EZ-B7rlOpK1GprnVY6z5DtUB5eOYE0XZLHQSlvevzSUpdA?e=arujAj\nAward Letter and BOQ: https://azanigroupn.sharepoint.com/:b:/s/teams/ERGSpvaXB9tHmBACFlPVVU4Bbpv-gJbnZJNAflH2mSJ5lg?e=t2aiHH"
        }
    ]

    created_projects = []

    with transaction.atomic():
        for item in projects_data:
            cat_obj = cat_map.get(item['category_key'])
            staff_obj = user_map.get(item['staff_key']) if item['staff_key'] else None
            
            proj = Project.objects.filter(
                project_code=item['project_code'],
                lot=item['lot']
            ).first()

            if not proj:
                proj = Project(
                    mda=item['mda'],
                    project_code=item['project_code'],
                    project_name=item['project_name'],
                    lot=item['lot'],
                    project_type=item['project_type'],
                    location=item['location'],
                    category=cat_obj,
                    budget_amount=item['budget_amount'],
                    actual_contract_amount=item['actual_contract_amount'],
                    in_house_benchmark=item['in_house_benchmark'],
                    mobilization_received=Decimal("0.00"),
                    batch_no_mobilization=item['batch_no_mobilization'],
                    cost_percentage=item['cost_percentage'],
                    staff_assigned=staff_obj,
                    execution_mode='SUBCONTRACTED' if item['subcontractor'] else 'SELF_EXECUTED',
                    current_phase='POST_AWARD',
                    project_status='Awarded',
                    payment_status='Pending',
                    plain_boq='',
                    award_letter_and_boq='',
                    final_companies=item['final_companies'],
                    updated_recommended_companies=item['updated_recommended_companies'],
                    comments=item['comments'],
                    remarks=item['remarks'],
                    part_name=item['part_name']
                )
                proj.save()
                print(f"Created Project #{proj.sn}: {proj.project_code} - {proj.lot} ({proj.project_name[:50]}...)", flush=True)
            else:
                proj.mda = item['mda']
                proj.project_name = item['project_name']
                proj.project_type = item['project_type']
                proj.location = item['location']
                proj.category = cat_obj
                proj.budget_amount = item['budget_amount']
                proj.actual_contract_amount = item['actual_contract_amount']
                proj.in_house_benchmark = item['in_house_benchmark']
                proj.mobilization_received = Decimal("0.00")
                proj.batch_no_mobilization = item['batch_no_mobilization']
                proj.cost_percentage = item['cost_percentage']
                proj.staff_assigned = staff_obj
                proj.execution_mode = 'SUBCONTRACTED' if item['subcontractor'] else 'SELF_EXECUTED'
                proj.current_phase = 'POST_AWARD'
                proj.project_status = 'Awarded'
                proj.payment_status = 'Pending'
                proj.plain_boq = ''
                proj.award_letter_and_boq = ''
                proj.final_companies = item['final_companies']
                proj.updated_recommended_companies = item['updated_recommended_companies']
                proj.comments = item['comments']
                proj.remarks = item['remarks']
                proj.part_name = item['part_name']
                proj.save()
                print(f"Updated Project #{proj.sn}: {proj.project_code} - {proj.lot}", flush=True)

            created_projects.append(proj)

            # Clear any old Admin Fee for NDE projects
            ProjectFee.objects.filter(project=proj, fee_type=fee_admin).delete()

            # Facilitation Fee = 16,000.00
            ProjectFee.objects.update_or_create(
                project=proj,
                fee_type=fee_facilitation,
                defaults={'amount': Decimal("16000.00")}
            )

            # Logistics and Monitoring Fee = 10% of actual_contract_amount
            logistics_fee_amount = item['actual_contract_amount'] * Decimal("0.10")
            ProjectFee.objects.update_or_create(
                project=proj,
                fee_type=fee_logistics,
                defaults={'amount': logistics_fee_amount}
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

    # Ensure all NDE projects have created_at set to 2025
    import datetime
    dt_2025 = datetime.datetime(2025, 6, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    Project.objects.filter(mda='NATIONAL DIRECTORATE OF EMPLOYMENT (NDE)').update(created_at=dt_2025)

    print(f"Successfully loaded {len(created_projects)} projects into database for year 2025!", flush=True)

load_nde_projects()
