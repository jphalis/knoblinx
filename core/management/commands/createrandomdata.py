import random

from random import randint
from urllib import urlopen
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from accounts.models import Company, Degree, Hobby, MyUser, School
from jobs.models import Applicant, Job

# Create your commands here.


class Command(BaseCommand):
    help = 'Generates random data to be used for demonstration purposes.'

    def handle(self, *args, **options):
        # Get default profile image
        image_url = '''http://cdn.scahw.com.au/cdn-1cfaa3a9e77a520/
            imagevaultfiles/id_301664/cf_3/random-animals-16.jpg'''
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urlopen(image_url).read())
        img_temp.flush()
        pic = File(img_temp)

        # Get default file to use for resume
        resume_url = '''http://writing.colostate.edu/guides/documents/resume/
            functionalSample.pdf'''
        resume_temp = NamedTemporaryFile(delete=True)
        resume_temp.write(urlopen(resume_url).read())
        resume_temp.flush()
        resume = File(resume_temp)

        # Demo hobbies to be used in following functions
        demo_hobbies = [
            Hobby.objects.all().order_by('?').first(),
            Hobby.objects.all().order_by('?').first(),
            Hobby.objects.all().order_by('?').first(),
            Hobby.objects.all().order_by('?').first(),
            Hobby.objects.all().order_by('?').first(),
        ]

        # Create demo student user
        if not MyUser.objects.filter(email='student@demo.com').exists():
            student_demo = MyUser.objects.create_user(
                email='student@demo.com',
                first_name='Student',
                last_name='Sample',
                password='demo',
                gpa=3.45,
                degree_earned=MyUser.BACHELOR,
                year=MyUser.SENIOR,
                opp_sought=MyUser.FULL_TIME,
            )
            student_demo.profile_pic.save(
                "image_%s" % student_demo.username, pic),
            student_demo.resume.save(
                "resume_%s" % student_demo.username, resume),
            student_demo.is_confirmed = True
            student_demo.account_type = MyUser.STUDENT
            student_demo.video = 'https://www.youtube.com/watch?v=_OBlgSz8sSM'
            student_demo.undergrad_uni = School.objects.get(
                name='Brown University')
            student_demo.undergrad_degree.add(
                Degree.objects.get(name='Business'))
            student_demo.save()

            for hobby in demo_hobbies:
                student_demo.hobbies.add(hobby)

            self.stdout.write(
                self.style.WARNING('Created demo student account.'))

        # Create demo employer user
        if not MyUser.objects.filter(email='employer@demo.com').exists():
            employer_demo = MyUser.objects.create_user(
                email='employer@demo.com',
                first_name='Employer',
                last_name='Sample',
                password='demo'
            )
            employer_demo.is_confirmed = True
            employer_demo.account_type = MyUser.EMPLOYER
            employer_demo.save()

            self.stdout.write(
                self.style.WARNING('Created demo employer account.'))

        # Create users
        users = [
            ['John', 'Doe'],
            ['Bill', 'Clarkson'],
            ['Jessica', 'Hall'],
            ['Franklin', 'Rose'],
            ['Bobby', 'Collins'],
            ['Fred', 'Flinstone'],
            ['Blake', 'Casper'],
            ['Marissa', 'Smiles'],
            ['Tyler', 'Simm'],
            ['Gina', 'Zentenial'],
            ['Michelle', 'Gregs'],
            ['Oscar', 'Behaves'],
            ['Heather', 'Hoolihan'],
            ['Scott', 'Dragonile'],
            ['Charlie', 'Bitfinger'],
            ['Pryia', 'Havalopolous'],
            ['Chris', 'Wildwood'],
            ['Jonathan', 'Newguinea'],
            ['Anne', 'Hathaway'],
            ['Brooke', 'Orchard']
        ]

        if not MyUser.objects.filter(first_name=users[0][0]).exists():

            for user in users:
                user = MyUser.objects.create_user(
                    email='{}.{}@{}'.format(
                        user[0],
                        user[1],
                        School.objects.all().order_by('?').first().email
                    ).lower(),
                    first_name=user[0],
                    last_name=user[1],
                    password='demo',
                    gpa=randint(int(2), int(100 * 4)) / 100.0,
                    degree_earned=random.choice(
                        [x[0] for x in MyUser.DEGREE_TYPES]
                    ),
                    year=random.choice([x[0] for x in MyUser.YEAR_TYPES]),
                    opp_sought=random.choice(
                        [x[0] for x in MyUser.OPPORTUNITY_TYPES]
                    )
                )
                user.is_confirmed = True
                user.account_type = MyUser.STUDENT
                user.profile_pic.save("image_%s" % user.username, pic),
                user.resume.save("resume_%s" % user.username, resume),
                user.undergrad_uni = School.objects.all().order_by('?').first()
                user.undergrad_degree.add(
                    Degree.objects.all().order_by('?').first())
                user.save()

                for hobby in demo_hobbies:
                    user.hobbies.add(hobby)

            self.stdout.write(
                self.style.WARNING('Created demo student accounts.'))

        # Create companies
        company_owners = [
            ['Jeff', 'Bezos'],
            ['Pablo', 'Padre'],
            ['Jaime', 'Windell'],
            ['Naome', 'Watts']
        ]

        if not MyUser.objects.filter(first_name=company_owners[0][0]).exists():

            for user in company_owners:
                user = MyUser.objects.create_user(
                    email='{}.{}@demo.com'.format(user[0], user[1]).lower(),
                    first_name=user[0],
                    last_name=user[1],
                    password='demo'
                )
                user.is_confirmed = True
                user.account_type = MyUser.EMPLOYER
                user.save()

            self.stdout.write(
                self.style.WARNING('Created demo employer owner accounts.'))

        companies = [
            ['Goldman Sachs', MyUser.objects.get(first_name='Jeff')],
            ['JPMorgan Chase', MyUser.objects.get(first_name='Pablo')],
            ['Morgan Stanley', MyUser.objects.get(first_name='Jaime')],
            ['American Express', MyUser.objects.get(first_name='Naome')],
            ['KPMG', MyUser.objects.get(first_name='Employer')],
        ]

        if not Company.objects.filter(name=companies[0][0]).exists():

            for company in companies:
                Company.objects.create(user=company[1], name=company[0])

            self.stdout.write(
                self.style.WARNING('Created demo employer accounts.'))

        # Create jobs
        description = '''Affert officiis consequat ut his. Vix cu ferri
        nostrum contentiones, in pri partem principes, pri id aliquid
        pericula. Nam atqui intellegat at. Et soleat perfecto mei, elitr
        abhorreant his an. Ex soleat habemus splendide mei, duo eu suas iisque,
        id eam justo argumentum. In sea cetero erroribus vituperatoribus.
        Dolorum senserit ad pri, no est nusquam definitiones.
        Has ipsum tincidunt ne. Eu mea aperiri euismod, vix in nominati
        inimicus. At simul adipiscing nec, dolore laboramus pro no, sea tale
        fierent ne. An corpora detracto corrumpit pri, epicurei intellegam quo
        in, dicit verterem id sit'''
        start = datetime.now()
        end = start + timedelta(days=21)
        contact_email = 'demo@demo.com'
        jobs = [
            ['Sales Associate', 'New York, NY'],
            ['IT Consultant', 'Hoboken, NJ'],
            ['Event Manager', 'Los Angeles, CA'],
            ['Senior Director', 'New York, NY'],
            ['EVP', 'Boston, MA'],
            ['Software Developer', 'Menlo Park, CA'],
            ['Marketing Associate', 'La Jolla, CA']
        ]

        if not Job.objects.filter(title=jobs[0][0]).exists():
            for job in jobs:
                company = Company.objects.order_by('?').first()
                Job.objects.create(
                    user=company.user,
                    company=company,
                    title=job[0],
                    contact_email=contact_email,
                    description=description,
                    location=job[1],
                    list_date_start=start,
                    list_date_end=end,
                )

            self.stdout.write(
                self.style.WARNING('Created demo job listings.'))

        # Create applicants
        if not Applicant.objects.filter(
                user=MyUser.objects.get(first_name=users[0][0])).exists():

            for applicant in users:
                _user = MyUser.objects.get(first_name=applicant[0])
                Applicant.objects.create(
                    user=_user,
                    resume=settings.STATIC_URL + 'img/default-profile-pic.jpg',
                    email=_user.email
                )

            self.stdout.write(
                self.style.WARNING('Created demo applicants.'))

        # Add applicants to jobs
        for applicant in Applicant.objects.all():
            job = Job.objects.all().order_by('?').first()
            job.applicants.add(applicant)

        self.stdout.write(
            self.style.WARNING('Added applicants to demo job listings.'))

        self.stdout.write(
            self.style.SUCCESS('Successfully generated all sample data.'))
