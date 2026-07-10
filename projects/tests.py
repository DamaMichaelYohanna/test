from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, ProjectCategory, FeeType, ProjectFee

class ProjectRestructuringTests(TestCase):
    def setUp(self):
        # Get or create categories
        self.category_power, _ = ProjectCategory.objects.get_or_create(name="POWER", defaults={"description": "Power projects"})
        self.category_const, _ = ProjectCategory.objects.get_or_create(name="Construction", defaults={"description": "Construction work"})
        
        # Get or create fee types
        self.fee_admin, _ = FeeType.objects.get_or_create(name="Admin Fee", defaults={"description": "Admin charges"})
        self.fee_vat, _ = FeeType.objects.get_or_create(name="VAT", defaults={"description": "Value Added Tax"})
        
        # Create user
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.staff_user = User.objects.create_user(username="staffuser", password="testpassword", is_staff=True)
        
        # Add staff_user to Level 3 group to satisfy Level3RequiredMixin checks
        from django.contrib.auth.models import Group
        level3_group, _ = Group.objects.get_or_create(name='Level 3')
        self.staff_user.groups.add(level3_group)

        # Create parent project
        self.parent_project = Project.objects.create(
            project_code="PRJ-PARENT",
            mda="Ministry of Power",
            project_name="Grid Expansion Project",
            location="Abuja",
            category=self.category_power,
            budget_amount=50000000.00
        )

    def test_project_creation_and_attributes(self):
        # Create child project rolled over from parent
        project = Project.objects.create(
            project_code="PRJ-001",
            mda="Ministry of Works",
            project_name="Bridge Rehabilitation",
            location="Lagos",
            category=self.category_const,
            rolled_over_from=self.parent_project,
            budget_amount=15000000.00,
            current_phase="POST_AWARD"
        )
        
        self.assertEqual(project.category.name, "Construction")
        self.assertEqual(project.rolled_over_from.project_code, "PRJ-PARENT")
        self.assertEqual(project.current_phase, "POST_AWARD")
        self.assertEqual(project.get_current_phase_display(), "Post-Award Phase")

    def test_project_fees_relationship(self):
        # Create fees for the parent project
        fee1 = ProjectFee.objects.create(
            project=self.parent_project,
            fee_type=self.fee_admin,
            amount=250000.00
        )
        fee2 = ProjectFee.objects.create(
            project=self.parent_project,
            fee_type=self.fee_vat,
            amount=375000.00
        )
        
        self.assertEqual(self.parent_project.fees.count(), 2)
        fees_dict = {f.fee_type.name: f.amount for f in self.parent_project.fees.all()}
        self.assertEqual(fees_dict["Admin Fee"], 250000.00)
        self.assertEqual(fees_dict["VAT"], 375000.00)

    def test_project_form_and_views(self):
        self.client.login(username="staffuser", password="testpassword")
        
        # Test project creation via POST with fees formset
        url = reverse('projects:project_create')
        data = {
            'project_code': 'PRJ-NEW',
            'mda': 'Ministry of Environment',
            'project_name': 'Erosion Control',
            'project_type': 'CONSTRUCTION',
            'execution_mode': 'SELF_EXECUTED',
            'location': 'Anambra',
            'category': self.category_const.pk,
            'rolled_over_from': '',
            'parent_project': '',
            'part_name': '',
            'part_percentage': '100.00',
            'budget_amount': '8000000.00',
            'current_phase': 'PRE_AWARD',
            'execution_level_percentage': 0,
            'project_status': 'Initiated',
            'payment_status': 'Pending',
            'actual_contract_amount': '0.00',
            'in_house_benchmark': '0.00',
            'cost_percentage': '0.00',
            'mobilization_received': '0.00',
            'final_payment_received': '0.00',
            
            # Formset management fields
            'fees-TOTAL_FORMS': '1',
            'fees-INITIAL_FORMS': '0',
            'fees-MIN_NUM_FORMS': '0',
            'fees-MAX_NUM_FORMS': '1000',
            
            # Formset data fields
            'fees-0-fee_type': self.fee_admin.pk,
            'fees-0-amount': '150000.00',
            'fees-0-id': '',
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        
        # Verify project and associated fee were created
        self.assertTrue(Project.objects.filter(project_code="PRJ-NEW").exists())
        new_project = Project.objects.get(project_code="PRJ-NEW")
        self.assertEqual(new_project.fees.count(), 1)
        self.assertEqual(new_project.fees.first().amount, 150000.00)

    def test_settings_page_access_denied_for_regular_user(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse('projects:settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Redirected to dashboard

    def test_settings_page_access_allowed_for_staff(self):
        self.client.login(username="staffuser", password="testpassword")
        url = reverse('projects:settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200) # Access granted
        
    def test_settings_page_create_category(self):
        self.client.login(username="staffuser", password="testpassword")
        url = reverse('projects:settings')
        data = {
            'action': 'save_category',
            'name': 'Infrastructure',
            'description': 'Roads and rails'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProjectCategory.objects.filter(name="Infrastructure").exists())

    def test_settings_page_delete_category_blocked_when_in_use(self):
        self.client.login(username="staffuser", password="testpassword")
        url = reverse('projects:settings')
        
        # Test parent_project is using self.category_power
        data = {
            'action': 'delete_category',
            'cat_id': self.category_power.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Verify it was not deleted
        self.assertTrue(ProjectCategory.objects.filter(pk=self.category_power.pk).exists())
        
        # Verify message error was thrown
        # (We check that a message warning user is present)
        response_get = self.client.get(url)
        self.assertContains(response_get, "Cannot delete category")

    def test_project_split_parts_inheritance_and_rollups(self):
        # 1. Verify inheritance when saving a child project part
        child_part1 = Project.objects.create(
            parent_project=self.parent_project,
            project_name="Grid Expansion Part A",
            part_name="Part A",
            part_percentage=60.00,
            budget_amount=30000000.00,
            actual_contract_amount=35000000.00,
            mobilization_received=10000000.00,
            final_payment_received=0.00,
            execution_level_percentage=80
        )
        # Verify inherited fields
        self.assertEqual(child_part1.project_code, self.parent_project.project_code)
        self.assertEqual(child_part1.mda, self.parent_project.mda)
        self.assertEqual(child_part1.location, self.parent_project.location)
        self.assertEqual(child_part1.category, self.parent_project.category)

        # 2. Verify non-unique project code is allowed
        child_part2 = Project.objects.create(
            parent_project=self.parent_project,
            project_name="Grid Expansion Part B",
            part_name="Part B",
            part_percentage=40.00,
            budget_amount=20000000.00,
            actual_contract_amount=25000000.00,
            mobilization_received=5000000.00,
            final_payment_received=15000000.00,
            execution_level_percentage=30
        )
        self.assertEqual(child_part2.project_code, self.parent_project.project_code)

        # 3. Verify rollup values on the parent project
        self.assertTrue(self.parent_project.is_parent)
        self.assertEqual(self.parent_project.total_budget_amount, 50000000.00)
        self.assertEqual(self.parent_project.total_actual_contract_amount, 60000000.00)
        self.assertEqual(self.parent_project.total_mobilization_received, 15000000.00)
        self.assertEqual(self.parent_project.total_final_payment_received, 15000000.00)
        
        # 4. Verify weighted average execution level: (80% * 60 + 30% * 40) / 100 = (4800 + 1200) / 100 = 60%
        self.assertEqual(self.parent_project.average_execution_percentage, 60)
