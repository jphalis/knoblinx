from django.core.management.base import BaseCommand
from accounts.schools import schools
from accounts.models import School

# Create your commands here.


class Command(BaseCommand):
    help = 'Creates a default list of schools.'

    def handle(self, *args, **options):
        for school in schools:
            if not School.objects.filter(name=school[0]).exists():
                School.objects.create(
                    name=school[0], location=school[1], email=school[2])
                self.stdout.write(
                    self.style.WARNING('Created {}.'.format(school[0])))
        self.stdout.write(
            self.style.SUCCESS('Successfully created all schools.'))
