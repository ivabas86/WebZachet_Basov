## Для запуска из файла (или тестирования) раскомментировать
# import os
# import django
# from django.conf import settings
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
# settings.ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
# django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from api_rest.models import restaurant, table, Booking

from datetime import date, timedelta

User = get_user_model()


class BookingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123')
        self.admin = User.objects.create_superuser(
            username='adminuser', password='adminpass123')

        self.hotel = restaurant.objects.create(
            name='Test Hotel', city='Test City', address='Test Address',
            description='Test Desc', rating=4.5)

        self.room = table.objects.create(
            hotel=self.hotel, room_number='101', room_type='single',
            price_per_night=100.00, capacity=1)

    def authenticate(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_create_booking_authenticated(self):
        self.authenticate()
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)
        response = self.client.post('/api/bookings/', {
            'room': self.room.id,
            'check_in_date': check_in,
            'check_out_date': check_out
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['room'], self.room.id)

    def test_booking_conflict(self):
        self.authenticate()
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)
        Booking.objects.create(
            user=self.user, room=self.room,
            check_in_date=check_in, check_out_date=check_out,
            status='active')

        response = self.client.post('/api/bookings/', {
            'room': self.room.id,
            'check_in_date': check_in,
            'check_out_date': check_out
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_list_hotels(self):
        response = self.client.get('/api/hotels/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_admin_can_create_hotel(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'adminuser',
            'password': 'adminpass123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.post('/api/hotels/', {
            'name': 'New Hotel',
            'city': 'New City',
            'address': 'Some address',
            'description': 'Nice place',
            'rating': 4.0
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
