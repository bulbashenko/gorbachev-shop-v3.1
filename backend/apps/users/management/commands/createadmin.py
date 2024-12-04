from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import CommandError
import getpass

class Command(BaseCommand):
    help = 'Create a superuser with email, username and password prompt'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get email
        while True:
            email = input('Email address: ')
            if email:
                break
            self.stderr.write('Error: Email cannot be blank.')
            
        # Get username
        while True:
            username = input('Username: ')
            if username:
                break
            self.stderr.write('Error: Username cannot be blank.')
            
        # Get password
        while True:
            password = getpass.getpass()
            password2 = getpass.getpass('Password (again): ')
            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                continue
            if password.strip() == '':
                self.stderr.write("Error: Blank passwords aren't allowed.")
                continue
            break

        try:
            User.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                first_name='Admin',
                last_name='User',
                marketing_preferences={'email_notifications': False, 'sms_notifications': False}
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        except Exception as e:
            raise CommandError(str(e))
