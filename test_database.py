import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import Project, Category, CustomUser
from django.utils import timezone

print("=== DATABASE TEST ===")

# Test 1: Check if we can connect to database
try:
    user_count = CustomUser.objects.count()
    print(f"✅ Database connection OK - {user_count} users found")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# Test 2: Check categories
try:
    categories = Category.objects.all()
    print(f"✅ Categories found: {categories.count()}")
    for cat in categories:
        print(f"  - {cat.id}: {cat.name}")
except Exception as e:
    print(f"❌ Error getting categories: {e}")

# Test 3: Try to create a test project
try:
    user = CustomUser.objects.first()
    category = Category.objects.first()
    
    if not user or not category:
        print("❌ No user or category found for testing")
        exit(1)
    
    print(f"Using user: {user.username}")
    print(f"Using category: {category.name}")
    
    # Create a test project
    start_date = timezone.now()
    end_date = start_date + timedelta(days=30)
    
    project = Project.objects.create(
        creator=user,
        title="Database Test Project",
        details="This is a test project to verify database functionality",
        category=category,
        total_target=10000.00,
        current_amount=0.00,
        tags="test, database",
        start_date=start_date,
        end_date=end_date,
        is_featured=False,
        is_active=True
    )
    
    print(f"✅ Test project created successfully!")
    print(f"Project ID: {project.id}")
    print(f"Title: {project.title}")
    
    # Clean up - delete the test project
    project.delete()
    print("✅ Test project cleaned up")
    
except Exception as e:
    print(f"❌ Error creating test project: {e}")
    import traceback
    traceback.print_exc()

print("\n=== END TEST ===")
