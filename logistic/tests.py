from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from projects.models import Project
from .models import MilestoneCashRequest

class CashRequestTests(TestCase):
    def setUp(self):
        # Retrieve or create groups (seeded in migrations)
        self.level2_group, _ = Group.objects.get_or_create(name='Level 2')
        self.level3_group, _ = Group.objects.get_or_create(name='Level 3')
        self.level4_group, _ = Group.objects.get_or_create(name='Level 4')

        # Create users
        self.staff_user = User.objects.create_user(username='staff', password='password123')
        self.staff_user.groups.add(self.level2_group)

        self.manager_user = User.objects.create_user(username='manager', password='password123')
        self.manager_user.groups.add(self.level3_group)

        self.exec_user = User.objects.create_user(username='executive', password='password123')
        self.exec_user.groups.add(self.level4_group)

        self.superuser = User.objects.create_superuser(username='superuser', password='password123')

        # Create a test project
        self.project = Project.objects.create(
            project_code='PRJ001',
            project_name='Test Project',
            location='Lagos',
            mda='Ministry of Works'
        )

    def test_staff_can_create_cash_request(self):
        self.client.login(username='staff', password='password123')
        url = reverse('logistic:cash_requests_dashboard')
        
        response = self.client.post(url, {
            'project_id': self.project.pk,
            'milestone_title': 'Excavation Work',
            'amount_requested': '500000.00',
            'justification': 'Need funds for excavation machines.'
        })
        
        self.assertEqual(response.status_code, 302)
        # Verify the object was created in DB
        self.assertTrue(MilestoneCashRequest.objects.filter(milestone_title='Excavation Work').exists())
        req = MilestoneCashRequest.objects.get(milestone_title='Excavation Work')
        self.assertEqual(req.status, 'PENDING')
        self.assertEqual(req.requested_by, self.staff_user)

    def test_manager_cannot_create_cash_request_on_dashboard(self):
        self.client.login(username='manager', password='password123')
        url = reverse('logistic:cash_requests_dashboard')
        
        response = self.client.post(url, {
            'project_id': self.project.pk,
            'milestone_title': 'Excavation Work',
            'amount_requested': '500000.00',
            'justification': 'Need funds for excavation machines.'
        })
        
        # Managers should be redirected and see an error message
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MilestoneCashRequest.objects.filter(milestone_title='Excavation Work').exists())

    def test_executive_can_approve_cash_request(self):
        # Create a pending request
        req = MilestoneCashRequest.objects.create(
            project=self.project,
            requested_by=self.staff_user,
            milestone_title='Foundation Pouring',
            amount_requested='1000000.00',
            justification_notes='Concrete mixing',
            status='PENDING'
        )

        self.client.login(username='executive', password='password123')
        url = reverse('logistic:process_cash_request', kwargs={'request_id': req.pk})
        
        response = self.client.post(url, {
            'action': 'APPROVE',
            'management_comment': 'Approved by executive'
        })
        
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, 'APPROVED')
        self.assertEqual(req.management_comment, 'Approved by executive')

    def test_executive_can_cancel_cash_request(self):
        # Create a pending request
        req = MilestoneCashRequest.objects.create(
            project=self.project,
            requested_by=self.staff_user,
            milestone_title='Roofing',
            amount_requested='2000000.00',
            justification_notes='Sheets and wood',
            status='PENDING'
        )

        self.client.login(username='executive', password='password123')
        url = reverse('logistic:process_cash_request', kwargs={'request_id': req.pk})
        
        response = self.client.post(url, {
            'action': 'CANCEL',
            'management_comment': 'Cancelled due to budget constraints'
        })
        
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, 'CANCELLED')
        self.assertEqual(req.management_comment, 'Cancelled due to budget constraints')

    def test_staff_cannot_process_cash_request(self):
        req = MilestoneCashRequest.objects.create(
            project=self.project,
            requested_by=self.staff_user,
            milestone_title='Plastering',
            amount_requested='300000.00',
            justification_notes='Cement and sand',
            status='PENDING'
        )

        self.client.login(username='staff', password='password123')
        url = reverse('logistic:process_cash_request', kwargs={'request_id': req.pk})
        
        response = self.client.post(url, {
            'action': 'APPROVE',
            'management_comment': 'Approved by staff'
        })
        
        # Level3RequiredMixin redirects unauthorized users (302)
        self.assertIn(response.status_code, [302, 403])
        req.refresh_from_db()
        self.assertEqual(req.status, 'PENDING')
