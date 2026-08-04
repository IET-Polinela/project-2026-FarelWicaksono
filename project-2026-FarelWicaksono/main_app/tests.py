from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Report


User = get_user_model()


class Lab10AuthenticationAndPermissionTests(APITestCase):
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
        self.assertTrue(user.check_password('PasswordKuat456!'))

    def test_citizen_can_create_report_without_reporter_payload(self):
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
        self.assertEqual(response.data['reporter'], 'citizen1')

    def test_admin_cannot_create_report_through_citizen_endpoint(self):
        self.login_as('admin1')
        response = self.client.post(
            '/api/reports/',
            {
                'title': 'Laporan Admin',
                'category': 'Lainnya',
                'description': 'Tidak boleh dibuat sebagai Citizen.',
                'location': 'Kantor',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_citizen_list_hides_other_users_draft(self):
        own_draft = Report.objects.create(
            title='Draft sendiri',
            category='Jalan',
            description='Draft milik citizen1',
            location='Lokasi A',
            status='DRAFT',
            reporter=self.citizen,
        )
        Report.objects.create(
            title='Draft orang lain',
            category='Jalan',
            description='Draft milik citizen2',
            location='Lokasi B',
            status='DRAFT',
            reporter=self.other_citizen,
        )
        published = Report.objects.create(
            title='Laporan verified',
            category='Jalan',
            description='Boleh dilihat semua user login',
            location='Lokasi C',
            status='VERIFIED',
            reporter=self.other_citizen,
        )

        self.login_as('citizen1')
        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item['id'] for item in response.data}
        self.assertIn(own_draft.id, ids)
        self.assertIn(published.id, ids)
        self.assertEqual(len(ids), 2)

    def test_owner_can_update_own_draft(self):
        report = Report.objects.create(
            title='Judul lama',
            category='Jalan',
            description='Deskripsi lama',
            location='Lokasi lama',
            status='DRAFT',
            reporter=self.citizen,
        )
        self.login_as('citizen1')
        response = self.client.put(
            f'/api/reports/{report.id}/',
            {
                'title': 'Judul baru',
                'category': 'Drainase',
                'description': 'Deskripsi baru',
                'location': 'Lokasi baru',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.title, 'Judul baru')
        self.assertEqual(report.status, 'DRAFT')

    def test_delete_verified_report_returns_403(self):
        report = Report.objects.create(
            title='Sudah diverifikasi',
            category='Jalan',
            description='Tidak boleh dihapus Citizen.',
            location='Lokasi A',
            status='VERIFIED',
            reporter=self.citizen,
        )
        self.login_as('citizen1')
        response = self.client.delete(f'/api/reports/{report.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Report.objects.filter(pk=report.id).exists())

    def test_api_requires_authentication(self):
        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
