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
        # Create child project linked to parent
        project = Project.objects.create(
            project_code="PRJ-001",
            mda="Ministry of Works",
            project_name="Bridge Rehabilitation",
            location="Lagos",
            category=self.category_const,
            linked_project=self.parent_project,
            budget_amount=15000000.00,
            current_phase="POST_AWARD"
        )
        
        self.assertEqual(project.category.name, "Construction")
        self.assertEqual(project.linked_project.project_code, "PRJ-PARENT")
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
        self.client.login(username="testuser", password="testpassword")
        
        # Test project creation via POST with fees formset
        url = reverse('projects:project_create')
        data = {
            'project_code': 'PRJ-NEW',
            'mda': 'Ministry of Environment',
            'project_name': 'Erosion Control',
            'project_type': 'CONSTRUCTION',
            'location': 'Anambra',
            'category': self.category_const.pk,
            'linked_project': '',
            'budget_amount': '8000000.00',
            'current_phase': 'PRE_AWARD',
            'level_of_completion_percentage': 0,
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
