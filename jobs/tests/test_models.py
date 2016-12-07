from django.test import Client, RequestFactory, TestCase

from accounts.models import Company, MyUser
from ..models import Applicant, Job

# Create your tests here.


def create_job(company):
    from datetime import datetime, timedelta

    company = company
    return Job.objects.create(
        user=company.user,
        company=company,
        title='Financial Analyst',
        contact_email=company.user.email,
        description='Some sample job description',
        location='New York, NY',
        list_date_start=datetime.now(),
        list_date_end=datetime.now() + timedelta(days=21)
    )


def create_student():
    return MyUser.objects.create_superuser(
        email='myemail@harvard.edu',
        first_name='JP',
        last_name='Halis',
        password='pbkdf2_sha256$120',
        account_type=MyUser.STUDENT
    )


def create_employer():
    return MyUser.objects.create_superuser(
        email='myemail@harvard.edu',
        first_name='JP',
        last_name='Halis',
        password='pbkdf2_sha256$120',
        account_type=MyUser.EMPLOYER
    )


def create_company(user):
    return Company.objects.create(user=user, name='Morgan Stanley')


class ApplicantTest(TestCase):

    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        self.factory = RequestFactory()
        self.user = create_student()
        self.logged_in = self.client.login(
            email=self.user.email,
            password='pbkdf2_sha256$120'
        )

    def create_applicant(self):
        from urllib import urlopen
        from django.core.files import File
        from django.core.files.temp import NamedTemporaryFile

        resume_url = '''http://writing.colostate.edu/guides/documents/resume/
            functionalSample.pdf'''
        resume_temp = NamedTemporaryFile(delete=True)
        resume_temp.write(urlopen(resume_url).read())
        resume_temp.flush()
        resume = File(resume_temp)
        return Applicant.objects.create(
            user=self.user, resume=resume, email=self.user.email
        )

    def test_applicant_created(self):
        c = self.create_applicant()
        # Check object is an Applicant instance
        self.assertTrue(isinstance(c, Applicant))
        # Check object's full_name matches __str__()
        self.assertEqual(c.__str__(), c.user.get_full_name)
        # Check new Applicant object created
        self.assertEqual(Applicant.objects.count(), 1)
        # Check user is logged in
        self.assertEqual(self.logged_in, True)

    def tearDown(self):
        self.user.delete()


class JobTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_employer()
        self.company = create_company(user=self.user)

    def test_job_created(self):
        c = create_job(company=self.company)
        # Check object is an Job instance
        self.assertTrue(isinstance(c, Job))
        # Check object's full_name matches __str__()
        self.assertEqual(c.__str__(), 'Financial Analyst')
        # Check new Job object created
        self.assertEqual(Job.objects.count(), 1)

    def tearDown(self):
        self.user.delete()
        self.company.delete()
