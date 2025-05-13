from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Project
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
import tempfile
from PIL import Image
import uuid
import os

MINIMAL_JPEG = (
    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00'
    b'\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05'
    b'\x0a\x07\x07\x06\x08\x0c\x0a\x0c\x0c\x0b\x0a\x0b\x0b\x0d\x0e\x12\x10\x0d\x0e\x11\x0e'
    b'\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15'
    b'\x14\xff\xdb\x00C\x01\x03\x04\x04\x05\x04\x05\x09\x05\x05\x09\x14\x0d\x0b\x0d\x14'
    b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
    b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
    b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03'
    b'\x01\x22\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01'
    b'\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    b'\x0a\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00'
    b'\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1'
    b'\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\x09\x0a\x16\x17\x18\x19\x1a&\'()*'
    b'456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89'
    b'\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2'
    b'\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4'
    b'\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4'
    b'\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01'
    b'\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff'
    b'\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w'
    b'\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1'
    b'\xb1\xc1\x09#3R\xf0\x15br\xd1\x0a\x16$4\x83\x92\xe1!5\x93\xa2\xe2\xff\xda'
    b'\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfd\xfc\x28\xa2\x80\x0a\x28\xa2'
    b'\x80\x0a\x28\xa2\x80\x0a\x28\xa2\x80\x3f\xff\xd9'
)

class ProjectModelTests(TestCase):
    def setUp(self):
        self.project_data = {
            'title': 'Drug Inventory App',
            'description': 'A web app for tracking drug sales and stock.',
            'technologies': 'Django, Tailwind, MySQL',
            'project_url': 'https://drugzz.example.com',
            'repository_url': 'https://github.com/user/drugzz',
        }

    def test_create_project(self):
        project = Project.objects.create(
            title=self.project_data['title'],
            description=self.project_data['description'],
            technologies=self.project_data['technologies'],
            project_url=self.project_data['project_url'],
            repository_url=self.project_data['repository_url'],
        )

        self.assertEqual(project.title, self.project_data['title'])
        self.assertEqual(project.description, self.project_data['description'])
        self.assertEqual(project.technologies, self.project_data['technologies'])
        self.assertEqual(project.project_url, self.project_data['project_url'])
        self.assertEqual(project.repository_url, self.project_data['repository_url'])
        self.assertTrue(project.created_at)
        self.assertTrue(project.updated_at)
        self.assertFalse(project.image)  # No image provided
        self.assertEqual(str(project), self.project_data['title'])

    def test_create_project_with_image(self):
        image = SimpleUploadedFile("test_image.jpg",
                                   b"file_content",
                                   content_type="image/jpeg")
        project = Project.objects.create(
            title = 'Image Project',
            description='A project with an image.',
            technologies='Django, Tailwind',
            image=image,
        )

        self.assertEqual(project.title, 'Image Project')
        self.assertEqual(project.description, 'A project with an image.')
        self.assertEqual(project.technologies, 'Django, Tailwind')
        self.assertTrue(project.image)
        # self.assertIn('projects/test_image', project.image.path)
        self.assertTrue(project.image.name.startswith('projects/test_image'))
        
    

    def test_unique_title_constraint(self):
        """Test that duplicate titles are not allowed."""
        Project.objects.create(
            title=self.project_data['title'],
            description='First project.',
        )

        with self.assertRaises(Exception):  
            Project.objects.create(
                title=self.project_data['title'],
                description='Second project with same title.',
            )

    def test_optional_fields(self):
        """Test creating a project with only required fields."""
        project = Project.objects.create(
            title='Minimal Project',
            description='A minimal project.',
        )

        self.assertEqual(project.title, 'Minimal Project')
        self.assertEqual(project.description, 'A minimal project.')
        self.assertEqual(project.technologies, '')
        self.assertEqual(project.project_url, '')
        self.assertEqual(project.repository_url, '')
        self.assertFalse(project.image)



class ProjectApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
           
            email='admin@example.com',
            password='adminpass'
        )
        self.project_data = {
            'title': 'Drug Inventory App',
            'description': 'A web app for tracking drug sales and stock.',
            'technologies': 'Django, Tailwind, MySQL',
            'project_url': 'https://drugzz.example.com',
            'repository_url': 'https://github.com/user/drugzz',
        }
        self.project = Project.objects.create(**self.project_data)

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


    def test_list_projects_public(self):
        """Testing if anyone can see the list of projects"""
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['title'], self.project_data['title'])

    def test_retrieve_project_public(self):
        """Testing that anyone can retrieve a project."""
        response = self.client.get(reverse('project-detail', kwargs={'pk': self.project.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.project_data['title'])

    def test_create_project_unauthenticated(self):
        """Testing that unauthenticated users cannot create projects."""
        response = self.client.post(reverse('project-list'), self.project_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_authenticated(self):
        """Testing that admins can create projects."""
        self.client.login(email='admin@example.com' ,password='adminpass')
        data = {
            'title': 'New Project',
            'description': 'A new project.',
            'technologies': 'Python, Django',
            'project_url': 'https://newproject.example.com',
            'repository_url': 'https://github.com/user/newproject',
        }
        response = self.client.post(reverse('project-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Project')

    def test_create_project_with_image(self):
        """Test that admins can create projects with images."""
        self.client.login(email='admin@example.com', password='adminpass')
        test_image = self.create_test_image()
        data = {
            'title': 'Image Project',
            'description': 'A project with an image.',
            'technologies': 'Django, Tailwind',
            'image': test_image,
        }
        response = self.client.post(reverse('project-list'), data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)
            print("Image file name:", test_image.name)
            print("Image content length:", len(test_image.read()))
            test_image.seek(0)  # Reset file pointer
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['image'].endswith('.jpg'))

