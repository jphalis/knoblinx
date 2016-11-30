from django.core.management.base import BaseCommand
from accounts.degrees import degrees
from accounts.models import Degree

# Create your commands here.


class Command(BaseCommand):
    help = 'Creates a default list of degrees.'

    def handle(self, *args, **options):
        for degree in degrees:
            if not Degree.objects.filter(name=degree).exists():
                Degree.objects.create(name=degree)
                self.stdout.write(
                    self.style.WARNING('Created {}.'.format(degree)))
        self.stdout.write(
            self.style.SUCCESS('Successfully created all degrees.'))
