import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import Project, Category
from django.test import RequestFactory
from pages.views import home

print("=== HOMEPAGE TEST ===")

# Create a mock request
factory = RequestFactory()
request = factory.get('/')

# Call the home view
response = home(request)

print(f"Response status: {response.status_code}")

# Check what projects exist
featured_projects = Project.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:5]
latest_projects = Project.objects.filter(is_active=True).order_by('-created_at')[:5]
categories = Category.objects.all()

print(f"\nFeatured projects: {featured_projects.count()}")
for project in featured_projects:
    print(f"  - {project.title} (Featured: {project.is_featured})")

print(f"\nLatest projects: {latest_projects.count()}")
for project in latest_projects:
    print(f"  - {project.title}")

print(f"\nCategories: {categories.count()}")
for category in categories:
    print(f"  - {category.name}")

print("\n=== END TEST ===")
