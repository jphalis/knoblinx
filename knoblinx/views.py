from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from accounts.models import Company, MyUser, School
from activity.models import Activity
from jobs.models import Job

# Create views here.






# REMOVE WHEN IN PRODUCTION ! ! !
def generate_data(request):
    import random
    from random import randint
    from urllib import urlopen
    from datetime import datetime, timedelta
    from django.conf import settings
    from django.core.files import File
    from django.core.files.temp import NamedTemporaryFile
    from accounts.degrees import degrees
    from accounts.hobbies import hobbies
    from accounts.models import Degree, Hobby, MyUser, School
    from accounts.schools import schools
    from jobs.models import Applicant

    image_url = 'http://cdn.scahw.com.au/cdn-1cfaa3a9e77a520/imagevaultfiles/id_301664/cf_3/random-animals-16.jpg'
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()
    pic = File(img_temp)

    resume_url = 'http://cdn.hloom.com/images/279-Goldfish-Bowl.jpg'
    resume_temp = NamedTemporaryFile(delete=True)
    resume_temp.write(urlopen(resume_url).read())
    resume_temp.flush()
    resume = File(resume_temp)

    # Create hobbies
    if not Hobby.objects.filter(name=hobbies[0]).exists():
        for hobby in hobbies:
            Hobby.objects.create(name=hobby)

    demo_hobbies = [
        Hobby.objects.all().order_by('?').first(),
        Hobby.objects.all().order_by('?').first(),
        Hobby.objects.all().order_by('?').first(),
        Hobby.objects.all().order_by('?').first(),
        Hobby.objects.all().order_by('?').first(),
    ]

    # Create schools
    if not School.objects.filter(name=schools[0][0]).exists():
        for school in schools:
            School.objects.create(
                name=school[0], location=school[1], email=school[2])

    # Create degrees
    if not Degree.objects.filter(name=degrees[0]).exists():
        for degree in degrees:
            Degree.objects.create(name=degree)

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
        student_demo.profile_pic.save("image_%s" % student_demo.username, pic),
        student_demo.resume.save("resume_%s" % student_demo.username, resume),
        student_demo.is_confirmed = True
        student_demo.account_type = MyUser.STUDENT
        student_demo.video = 'https://www.youtube.com/watch?v=_OBlgSz8sSM'
        student_demo.undergrad_uni = School.objects.get(name='Brown University')
        student_demo.undergrad_degree.add(Degree.objects.get(name='Business'))
        student_demo.save()
        for hobby in demo_hobbies:
            student_demo.hobbies.add(hobby)

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
                    School.objects.all().order_by('?').first().email).lower(),
                first_name=user[0],
                last_name=user[1],
                password='demo',
                gpa=randint(int(2), int(100 * 4)) / 100.0,
                degree_earned=random.choice([x[0] for x in MyUser.DEGREE_TYPES]),
                year=random.choice([x[0] for x in MyUser.YEAR_TYPES]),
                opp_sought=random.choice([x[0] for x in MyUser.OPPORTUNITY_TYPES])
            )
            user.is_confirmed = True
            user.account_type = MyUser.STUDENT
            user.profile_pic.save("image_%s" % user.username, pic),
            user.resume.save("resume_%s" % user.username, resume),
            user.undergrad_uni = School.objects.all().order_by('?').first()
            user.undergrad_degree.add(Degree.objects.all().order_by('?').first())
            user.save()
            for hobby in demo_hobbies:
                user.hobbies.add(hobby)

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

    # Create jobs
    description = '''Affert officiis consequat ut his. Vix cu ferri
    nostrum contentiones, in pri partem principes, pri id aliquid
    pericula. Nam atqui intellegat at. Et soleat perfecto mei, elitr
    abhorreant his an. Ex soleat habemus splendide mei, duo eu suas iisque,
    id eam justo argumentum. In sea cetero erroribus vituperatoribus.
    Dolorum senserit ad pri, no est nusquam definitiones.
    Has ipsum tincidunt ne. Eu mea aperiri euismod, vix in nominati inimicus.
    At simul adipiscing nec, dolore laboramus pro no, sea tale fierent ne.
    An corpora detracto corrumpit pri, epicurei intellegam quo in, dicit verterem id sit'''
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

    # Create applicants
    if not Applicant.objects.filter(user=MyUser.objects.get(first_name=users[0][0])).exists():
        for applicant in users:
            _user = MyUser.objects.get(first_name=applicant[0])
            Applicant.objects.create(
                user=_user,
                resume=settings.STATIC_URL + 'img/default-profile-pic.jpg',
                email=_user.email
            )

    # Add applicants to jobs
    for applicant in Applicant.objects.all():
        job = Job.objects.all().order_by('?').first()
        job.applicants.add(applicant)

    messages.success(request, 'Data generated.')
    return redirect('home')







@login_required
@require_http_methods(['POST'])
def get_company_ajax(request):
    user = request.user
    data = {}

    try:
        company = Company.objects.get(Q(user=user) | Q(collaborators=user))
        data.update({
            'company_name': company.name,
            'company_username': company.username
        })
    except:
        company = None
    return JsonResponse(data)


@cache_page(60)
@login_required
def home(request):
    user = request.user

    if user.account_type == MyUser.STUDENT:
        jobs = Job.objects.qualified(user=user)
        all_post_count = Job.objects.all().count()
        recent_posts = Job.objects.recent()[:7]

        paginator = Paginator(jobs, 12)  # Show 12 jobs per page
        page = request.GET.get('page')

        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            jobs = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results
            jobs = paginator.page(paginator.num_pages)

        context = {
            'all_post_count': all_post_count,
            'jobs': jobs,
            'recent_posts': recent_posts,
            'user': user
        }
        return render(request, 'jobs/list.html', context)
    elif user.account_type == MyUser.EMPLOYER:
        company_qs = Company.objects.filter(
            Q(user=user) | Q(collaborators=user), is_active=True)

        if company_qs.exists():
            company = company_qs.first()
            jobs = Job.objects.own(company=company)
            active_job_count = jobs.filter(
                Q(list_date_start__lte=timezone.now()) &
                Q(list_date_end__gt=timezone.now())
            ).count()

            context = {
                'company': company,
                'jobs': jobs,
                'jobs_count': jobs.count,
                'active_job_count': active_job_count,
                'collaborator_count': company.collaborators.count() + 1,
                'collaborators': company.get_collaborators_info
            }

            try:
                activity = Activity.objects.own(company=company)[:12]
            except:
                activity = None

            if activity:
                context.update({'activity': activity})

            return render(request, 'accounts/company_dash.html', context)
        return HttpResponseForbidden()
    else:
        uni_emails = School.objects.active().values_list('email', flat=True)
        username, domain = user.email.split('@')
        context = {
            'registered': True if domain.endswith(tuple(uni_emails)) else False
        }
    return render(request, 'auth/selection.html', context)


@cache_page(60 * 60 * 24 * 60)
def privacy_policy(request):
    return render(request, 'general/privacy_policy.html', {})


@cache_page(60 * 60 * 24 * 60)
def terms_of_use(request):
    return render(request, 'general/terms_of_use.html', {})
