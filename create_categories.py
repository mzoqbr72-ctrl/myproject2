import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import Category

# Categories to create
categories_data = [
    {
        'name': 'Technology',
        'description': 'Innovative tech projects and startups'
    },
    {
        'name': 'Education',
        'description': 'Educational initiatives and learning projects'
    },
    {
        'name': 'Healthcare',
        'description': 'Medical and health-related projects'
    },
    {
        'name': 'Environment',
        'description': 'Environmental and sustainability projects'
    },
    {
        'name': 'Arts & Culture',
        'description': 'Creative and cultural projects'
    },
    {
        'name': 'Business',
        'description': 'Business and entrepreneurship projects'
    },
    {
        'name': 'Social Impact',
        'description': 'Projects that create positive social change'
    }
]

# Create categories
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"Created category: {category.name}")
    else:
        print(f"Category already exists: {category.name}")

print("\nAll categories created successfully!")
