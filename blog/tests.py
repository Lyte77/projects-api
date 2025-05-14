


from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from blog.models import Post
import tempfile
from PIL import Image
import uuid
import os

User = get_user_model()

class BlogApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', 
                                             password='testpass123',
                                             is_staff= True)
        self.client = APIClient()


    def create_test_image(self):
        """Create a valid JPEG image file for testing."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Generate a 1x1 pixel image
            image = Image.new('RGB', (1, 1), color='black')
            image.save(temp_file, format='JPEG')
            temp_file_path = temp_file.name
            

        # Read the file content
        with open(temp_file_path, 'rb') as f:
            content = f.read()

        # Clean up the temporary file
        os.unlink(temp_file_path)

        # Create SimpleUploadedFile
        return SimpleUploadedFile(
            "test_image.jpg",
            content,
            content_type="image/jpeg"
        )

    def test_create_post_authenticated(self):
        """Testing that admins can create posts."""
        # Obtain JWT token
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'email': 'test@example.com', 'password': 'testpass123'},
            format='json'
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Prepare post data
        post_data = {
            'title': 'How to build an API with Drf',
            'content': 'Its a work of art',
        }

        # Send POST request
        response = self.client.post(reverse('blog-list'), post_data, format='json')

        # Debug output if request fails
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'How to build an API with Drf')
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().author, self.user)

    
    def test_create_post_with_image(self):
        self.client.login(email='test@example.com', password='testpass123')
        test_image = self.create_test_image()
        data = {
            'title': 'How to build an API with Drf and image',
            'content': 'Its a work of art ',
            'featured_image': test_image,
        }
        response = self.client.post(reverse('blog-list'), data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)
            print("Image file name:", test_image.name)
            print("Image content length:", len(test_image.read()))
            test_image.seek(0)  # Reset file pointer
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['featured_image'].endswith('.jpg'))
        