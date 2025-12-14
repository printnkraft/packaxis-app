import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'pujanamin'
email = 'pujan@packaxis.ca'
password = 'Packaxis2025!'

# Check if user already exists
if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists!")
    user = User.objects.get(username=username)
    # Update password
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✓ Updated password for user '{username}'")
else:
    # Create new superuser
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✓ Created superuser '{username}' successfully!")

print(f"\nLogin credentials:")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"\nYou can now login at: http://127.0.0.1:8000/admin/")
