import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import Project, Category, CustomUser

print("=== DEBUGGING PROJECTS ===")

# Check categories
print("\n1. Categories:")
categories = Category.objects.all()
for cat in categories:
    print(f"  - {cat.id}: {cat.name}")

# Check users
print("\n2. Users:")
users = CustomUser.objects.all()
for user in users:
    print(f"  - {user.id}: {user.username} ({user.email})")

# Check all projects
print("\n3. All Projects:")
projects = Project.objects.all()
if projects:
    for project in projects:
        print(f"  - ID: {project.id}")
        print(f"    Title: {project.title}")
        print(f"    Creator: {project.creator.username}")
        print(f"    Category: {project.category.name}")
        print(f"    Is Active: {project.is_active}")
        print(f"    Created: {project.created_at}")
        print(f"    Start Date: {project.start_date}")
        print(f"    End Date: {project.end_date}")
        print("    ---")
else:
    print("  No projects found in database!")

# Check active projects specifically
print("\n4. Active Projects:")
active_projects = Project.objects.filter(is_active=True)
if active_projects:
    for project in active_projects:
        print(f"  - {project.id}: {project.title} (by {project.creator.username})")
else:
    print("  No active projects found!")

print("\n=== END DEBUG ===")
