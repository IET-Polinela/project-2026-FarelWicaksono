from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Report


User = get_user_model()


class Lab12ReportAPITests(APITestCase):
    def setUp(self):
        self.citizen = User.objects.create_user(
            username='citizen1',
            email='citizen1@example.com',
            password='PasswordKuat123!',
            is_admin=False,
            is_member=True,
        )
        self.other_citizen = User.objects.create_user(
            username='citizen2',
            email='citizen2@example.com',
            password='PasswordKuat123!',
            is_admin=False,
            is_member=True,
        )
        self.admin_user = User.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            password='PasswordKuat123!',
            is_admin=True,
            is_member=False,
        )

    def login_as(self, username, password='PasswordKuat123!'):
        response = self.client.post(
            '/api/token/',
            {'username': username, 'password': password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        return response

    def create_report(self, owner, title, status_value='DRAFT'):
        return Report.objects.create(
            title=title,
            category='Drainase',
            description=f'Deskripsi {title}',
            location='Bandar Lampung',
            status=status_value,
            reporter=owner,
        )

    def test_register_creates_citizen_role(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'warga_baru',
                'email': 'warga@example.com',
                'password': 'PasswordKuat456!',
                'password2': 'PasswordKuat456!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='warga_baru')
        self.assertTrue(user.is_member)
        self.assertFalse(user.is_admin)

    def test_create_report_uses_jwt_owner_and_default_draft(self):
        self.login_as('citizen1')
        response = self.client.post(
            '/api/reports/',
            {
                'title': 'Banjir di Jalan Utama',
                'category': 'Drainase',
                'description': 'Air menggenangi jalan.',
                'location': 'Jalan Utama',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = Report.objects.get(pk=response.data['id'])
        self.assertEqual(report.reporter, self.citizen)
        self.assertEqual(report.status, 'DRAFT')
        self.assertTrue(response.data['is_owner'])

    def test_citizen_can_submit_new_report_as_reported(self):
        self.login_as('citizen1')
        response = self.client.post(
            '/api/reports/',
            {
                'title': 'Laporan langsung diajukan',
                'category': 'Sampah',
                'description': 'Sampah menumpuk.',
                'location': 'Jalan A',
                'status': 'REPORTED',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'REPORTED')

    def test_my_reports_returns_only_current_users_reports(self):
        own_draft = self.create_report(self.citizen, 'Draft sendiri')
        own_reported = self.create_report(self.citizen, 'Reported sendiri', 'REPORTED')
        self.create_report(self.other_citizen, 'Laporan orang lain', 'VERIFIED')

        self.login_as('citizen1')
        response = self.client.get('/api/reports/?tab=my_reports')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item['id'] for item in response.data['results']}
        self.assertEqual(ids, {own_draft.id, own_reported.id})
        self.assertTrue(all(item['is_owner'] for item in response.data['results']))

    def test_feed_hides_draft_excludes_owner_and_anonymizes_reporter(self):
        self.create_report(self.citizen, 'Laporan sendiri', 'REPORTED')
        self.create_report(self.other_citizen, 'Draft orang lain', 'DRAFT')
        public_report = self.create_report(self.other_citizen, 'Feed publik', 'VERIFIED')

        self.login_as('citizen1')
        response = self.client.get('/api/reports/?tab=feed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        item = response.data['results'][0]
        self.assertEqual(item['id'], public_report.id)
        self.assertEqual(item['reporter'], 'Warga Anonim')
        self.assertFalse(item['is_owner'])

    def test_pagination_limits_results_to_ten(self):
        for index in range(12):
            self.create_report(self.citizen, f'Laporan {index + 1}')

        self.login_as('citizen1')
        response = self.client.get('/api/reports/?tab=my_reports&page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 12)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])

    def test_results_are_sorted_by_latest_updated_at(self):
        older = self.create_report(self.citizen, 'Laporan lama')
        newer = self.create_report(self.citizen, 'Laporan baru')
        Report.objects.filter(pk=older.pk).update(updated_at=timezone.now() - timedelta(days=2))
        Report.objects.filter(pk=newer.pk).update(updated_at=timezone.now())

        self.login_as('citizen1')
        response = self.client.get('/api/reports/?tab=my_reports')
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids[:2], [newer.id, older.id])

    def test_owner_can_edit_and_submit_own_draft(self):
        report = self.create_report(self.citizen, 'Judul lama')
        self.login_as('citizen1')
        response = self.client.put(
            f'/api/reports/{report.id}/',
            {
                'title': 'Judul baru',
                'category': 'Drainase',
                'description': 'Deskripsi baru',
                'location': 'Lokasi baru',
                'status': 'REPORTED',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.title, 'Judul baru')
        self.assertEqual(report.status, 'REPORTED')

    def test_reported_report_cannot_be_edited_again(self):
        report = self.create_report(self.citizen, 'Sudah diajukan', 'REPORTED')
        self.login_as('citizen1')
        response = self.client.patch(
            f'/api/reports/{report.id}/',
            {'title': 'Manipulasi'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_citizen_cannot_choose_workflow_status_owned_by_admin(self):
        self.login_as('citizen1')
        response = self.client.post(
            '/api/reports/',
            {
                'title': 'Status ilegal',
                'category': 'Umum',
                'description': 'Mencoba langsung resolved.',
                'location': 'Lokasi',
                'status': 'RESOLVED',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_requires_authentication(self):
        response = self.client.get('/api/reports/?tab=my_reports')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
