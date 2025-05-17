from django.test import TestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import os
from PIL import Image
from testimonials.models import Testimonial

User = get_user_model()

class TestimonialTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            email='staff@example.com', password='staffpass123', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com', password='userpass123'
        )
        self.testimonial_data = {
            'quote': 'Amazing work by Lyte!',
            'reviewer_name': 'Jane Doe',
            'reviewer_title': 'CEO, Tech Corp',
            'approved': True,
            
        }

    def get_jwt_token(self, email, password):
        """Helper to obtain JWT token."""
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'email': email, 'password': password},
            format='json'
        )
        return response.data['access'] if response.status_code == status.HTTP_200_OK else None

    def create_test_image(self):
        """Create a valid JPEG image for testing."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            image = Image.new('RGB', (1, 1), color='black')
            image.save(temp_file, format='JPEG')
            temp_file_path = temp_file.name
        with open(temp_file_path, 'rb') as f:
            content = f.read()
        os.unlink(temp_file_path)
        return SimpleUploadedFile(
            "test_image.jpg",
            content,
            content_type="image/jpeg"
        )

    # Model Tests
    def test_create_testimonial_model(self):
        """Test creating a testimonial via the model."""
        testimonial = Testimonial.objects.create(
            quote=self.testimonial_data['quote'],
            reviewer_name=self.testimonial_data['reviewer_name'],
            reviewer_title=self.testimonial_data['reviewer_title'],
            approved=False,
            created_by=self.staff_user
        )
        self.assertEqual(testimonial.quote, self.testimonial_data['quote'])
        self.assertEqual(testimonial.reviewer_name, self.testimonial_data['reviewer_name'])
        self.assertEqual(testimonial.created_by, self.staff_user)
        self.assertFalse(testimonial.approved)
        self.assertTrue(testimonial.created_at)
        self.assertTrue(testimonial.updated_at)

    # def test_required_fields(self):
    #     """Test that quote and reviewer_name are required."""
    #     with self.assertRaises(Exception):
    #         Testimonial.objects.create(
    #             reviewer_name='Jane Doe',
                
    #             created_by=self.staff_user
    #         )
    #     with self.assertRaises(Exception):
    #         Testimonial.objects.create(
    #             quote='Amazing work!',
    #             created_by=self.staff_user
    #         )


    def test_required_fields(self):
            """Test that quote and reviewer_name are required."""
            # Test missing quote
            testimonial = Testimonial(
                reviewer_name='Jane Doe',
                created_by=self.staff_user
            )
            with self.assertRaises(ValidationError):
                testimonial.full_clean()

        # Test missing reviewer_name
            testimonial = Testimonial(
                quote='Amazing work!',
                created_by=self.staff_user
            )
            with self.assertRaises(ValidationError):
                testimonial.full_clean()
    # API Tests
    def test_create_testimonial_staff(self):
        """Test creating a testimonial as a staff user."""
        token = self.get_jwt_token('staff@example.com', 'staffpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            reverse('testimonial-list'),
            self.testimonial_data,
            format='json'
        )
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quote'], self.testimonial_data['quote'])
        self.assertEqual(response.data['reviewer_name'], self.testimonial_data['reviewer_name'])
        self.assertEqual(Testimonial.objects.count(), 1)
        self.assertEqual(Testimonial.objects.first().created_by, self.staff_user)

    # def test_create_testimonial_non_staff(self):
    #     """Test that non-staff users cannot create testimonials."""
    #     token = self.get_jwt_token('user@example.com', 'userpass123')
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    #     response = self.client.post(
    #         reverse('testimonial-list'),
    #         self.testimonial_data,
    #         format='json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(Testimonial.objects.count(), 0)

    # def test_create_testimonial_unauthenticated(self):
    #     """Test that unauthenticated users cannot create testimonials."""
    #     response = self.client.post(
    #         reverse('testimonial-list'),
    #         self.testimonial_data,
    #         format='json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #     self.assertEqual(Testimonial.objects.count(), 0)

    # def test_create_testimonial_with_image(self):
    #     """Test creating a testimonial with an image as a staff user."""
    #     token = self.get_jwt_token('staff@example.com', 'staffpass123')
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    #     test_image = self.create_test_image()
    #     data = self.testimonial_data.copy()
    #     data['image'] = test_image
    #     response = self.client.post(
    #         reverse('testimonial-list'),
    #         data,
    #         format='multipart'
    #     )
    #     if response.status_code != status.HTTP_201_CREATED:
    #         print("Response data:", response.data)
    #         print("Image file name:", test_image.name)
    #         print("Image content length:", len(test_image.read()))
    #         test_image.seek(0)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertTrue(response.data['image'].startswith('testimonials/test_image'))
    #     self.assertEqual(Testimonial.objects.count(), 1)

    # def test_list_testimonials_public(self):
    #     """Test listing approved testimonials without authentication."""
    #     Testimonial.objects.create(
    #         quote='Great work!',
    #         reviewer_name='John Smith',
    #         approved=True,
    #         created_by=self.staff_user
    #     )
    #     Testimonial.objects.create(
    #         quote='Not visible!',
    #         reviewer_name='Jane Doe',
    #         approved=False,
    #         created_by=self.staff_user
    #     )
    #     response = self.client.get(reverse('testimonial-list'))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)
    #     self.assertEqual(response.data[0]['reviewer_name'], 'John Smith')

    # def test_update_testimonial_creator(self):
    #     """Test updating a testimonial as the creator (staff)."""
    #     testimonial = Testimonial.objects.create(
    #         quote='Initial quote',
    #         reviewer_name='Jane Doe',
    #         approved=True,
    #         created_by=self.staff_user
    #     )
    #     token = self.get_jwt_token('staff@example.com', 'staffpass123')
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    #     update_data = {'quote': 'Updated quote', 'reviewer_name': 'Jane Doe'}
    #     response = self.client.put(
    #         reverse('testimonial-detail', kwargs={'pk': testimonial.pk}),
    #         update_data,
    #         format='json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['quote'], 'Updated quote')

    # def test_update_testimonial_non_creator(self):
    #     """Test that non-creators (non-staff) cannot update testimonials."""
    #     testimonial = Testimonial.objects.create(
    #         quote='Initial quote',
    #         reviewer_name='Jane Doe',
    #         approved=True,
    #         created_by=self.staff_user
    #     )
    #     token = self.get_jwt_token('user@example.com', 'userpass123')
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    #     update_data = {'quote': 'Updated quote', 'reviewer_name': 'Jane Doe'}
    #     response = self.client.put(
    #         reverse('testimonial-detail', kwargs={'pk': testimonial.pk}),
    #         update_data,
    #         format='json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_delete_testimonial_creator(self):
    #     """Test deleting a testimonial as the creator (staff)."""
    #     testimonial = Testimonial.objects.create(
    #         quote='Initial quote',
    #         reviewer_name='Jane Doe',
    #         approved=True,
    #         created_by=self.staff_user
    #     )
    #     token = self.get_jwt_token('staff@example.com', 'staffpass123')
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    #     response = self.client.delete(
    #         reverse('testimonial-detail', kwargs={'pk': testimonial.pk})
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(Testimonial.objects.count(), 0)

