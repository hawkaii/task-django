from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from tasks.models import Task, Comment

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            full_name='Admin User',
            password='admin123',
            role='Admin'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            full_name='Regular User',
            password='user123',
            role='User'
        )

    def test_unauthenticated_user_cannot_access_tasks(self):
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_soft_deleted_user_cannot_login(self):
        # Soft delete the user
        self.regular_user.is_active = False
        self.regular_user.save()
        
        # Try to login
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@example.com',
            'password': 'user123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The error message will be "Invalid email or password" because Django's auth
        # backend doesn't authenticate inactive users at all

    def test_regular_user_can_only_see_own_tasks(self):
        # Create a task for the regular user
        task = Task.objects.create(
            title='User Task',
            description='Task for regular user',
            assigned_to=self.regular_user
        )
        
        # Create a task for admin
        admin_task = Task.objects.create(
            title='Admin Task',
            description='Task for admin',
            assigned_to=self.admin_user
        )
        
        # Login as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Get tasks
        url = reverse('task-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'User Task')


class RBACTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            full_name='Admin User',
            password='admin123',
            role='Admin'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            full_name='Regular User',
            password='user123',
            role='User'
        )

    def test_only_admin_can_create_tasks(self):
        # Try as regular user
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'Test task',
            'assigned_to_id': self.regular_user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_admin_can_soft_delete_users(self):
        # Try as regular user
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-soft-delete', kwargs={'pk': self.regular_user.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)