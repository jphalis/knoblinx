from django.test import Client, RequestFactory, TestCase

from accounts.models import Company, MyUser
from ..models import Job

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


def create_company(user):
    return Company.objects.create(user=user, name='Morgan Stanley')


class ApplicantTest(TestCase):

    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        self.factory = RequestFactory()
        self.user = create_student()

    def test_applicant_can_view_job_detail(self):
        from django.core.urlresolvers import reverse
        from ..views import detail

        job = create_job(company=create_company(user=self.user))
        url = reverse('jobs:detail',
                      kwargs={'username': job.company.username,
                              'job_pk': job.pk})
        request = self.factory.get(url)
        request.user = job.company.user
        response = detail(request, job.pk, job.company.username)
        html = response.content.decode('utf8')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h3>{}</h3>'.format(job.title), html)

    def test_applicant_can_apply(self):
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.core.urlresolvers import reverse
        from ..views import apply

        job = create_job(company=create_company(user=self.user))
        url = reverse('jobs:apply', kwargs={'job_pk': job.pk})
        request = self.factory.post(url)
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        response = apply(request, job.pk)
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        self.user.delete()
