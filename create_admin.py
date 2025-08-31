import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from pages.models import CustomUser

# Create superuser with different mobile number
try:
    user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123456',
        first_name='Admin',
        last_name='User',
        mobile_phone='01111111111'  # Different mobile number
    )
    print(f"Superuser created successfully: {user.username}")
    print(f"Email: {user.email}")
    print(f"Password: admin123456")
    print(f"Mobile: {user.mobile_phone}")
except Exception as e:
    print(f"Error creating superuser: {e}")
