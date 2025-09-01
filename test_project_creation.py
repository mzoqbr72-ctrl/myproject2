import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import Project, Category, CustomUser
from django.utils import timezone

print("=== TESTING PROJECT CREATION ===")

# Get a user and category
try:
    user = CustomUser.objects.first()
    category = Category.objects.first()
    
    print(f"Using user: {user.username}")
    print(f"Using category: {category.name}")
    
    # Create test dates
    start_date = timezone.now()
    end_date = start_date + timedelta(days=30)
    
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    
    # Create project
    project = Project.objects.create(
        creator=user,
        title="Test Project - Smart Water System",
        details="This is a test project for debugging purposes. An innovative IoT-based system to monitor and conserve water usage.",
        category=category,
        total_target=50000.00,
        current_amount=0.00,
        tags="test, iot, water, conservation",
        start_date=start_date,
        end_date=end_date,
        is_featured=False,
        is_active=True
    )
    
    print(f"\n✅ Project created successfully!")
    print(f"Project ID: {project.id}")
    print(f"Title: {project.title}")
    print(f"Creator: {project.creator.username}")
    print(f"Category: {project.category.name}")
    print(f"Is Active: {project.is_active}")
    
except Exception as e:
    print(f"\n❌ Error creating project: {e}")
    import traceback
    traceback.print_exc()

print("\n=== END TEST ===")
