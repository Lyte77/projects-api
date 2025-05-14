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

