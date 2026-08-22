#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
username = 'swetha';
email = 'swetha@example.com';
password = 'MyStrongPassword123!';

user, _ = User.objects.get_or_create(username=username, defaults={'email': email});
user.email = email;
user.set_password(password);
user.is_staff = True;
user.is_superuser = True;
user.is_active = True;
user.save();
print('ADMIN USER SUCCESSFULLY CREATED/UPDATED');
"