from django.core.management.base import BaseCommand
from accounts.hobbies import hobbies
from accounts.models import Hobby

# Create your commands here.


class Command(BaseCommand):
    help = 'Creates a default list of hobbies.'

    def handle(self, *args, **options):
        for hobby in hobbies:
            if not Hobby.objects.filter(name=hobby).exists():
                Hobby.objects.create(name=hobby)
                self.stdout.write(
                    self.style.WARNING('Created {}.'.format(hobby)))
        self.stdout.write(
            self.style.SUCCESS('Successfully created all hobbies.'))
