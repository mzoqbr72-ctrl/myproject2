import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import Project

# Make the test project featured
try:
    project = Project.objects.get(id=1)
    project.is_featured = True
    project.save()
    print(f"✅ Project '{project.title}' is now featured!")
except Project.DoesNotExist:
    print("❌ Project not found!")
