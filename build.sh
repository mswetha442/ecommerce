#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username_field = getattr(User, 'USERNAME_FIELD', 'username')

# Target credentials
username_val = 'swetha'
email_val = 'swetha@example.com'
password_val = 'MyStrongPassword123!'

filter_kwargs = {username_field: email_val if username_field == 'email' else username_val}

user = User.objects.filter(**filter_kwargs).first()

if not user:
    create_kwargs = {
        username_field: email_val if username_field == 'email' else username_val,
        'email': email_val,
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
    user = User.objects.create_user(**create_kwargs) if hasattr(User.objects, 'create_user') else User.objects.create(**create_kwargs)
    print(f'==> CREATED NEW SUPERUSER ({username_field})')

user.set_password(password_val)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

print(f'==> SUCCESS: Superuser password set for {getattr(user, username_field)}')
"