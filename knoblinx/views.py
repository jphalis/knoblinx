from django.contrib import messages
from django.contrib.auth import logout
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
    from random import randint
    from datetime import datetime, timedelta
    from django.conf import settings
    from accounts.models import Degree, MyUser, School
    from jobs.models import Applicant
    from .degrees import degrees
    from .schools import schools

    # Create schools
    for school in schools:
        if not School.objects.filter(name=school[0]).exists():
            School.objects.create(
                name=school[0], location=school[1], email=school[2])

    # Create degrees
    for degree in degrees:
        if not Degree.objects.filter(name=degree).exists():
            Degree.objects.create(name=degree)

    # Create demo user
    if not MyUser.objects.filter(email='demo@demo.com').exists():
        demo_user = MyUser.objects.create_user(
            email='demo@demo.com',
            first_name='Sample',
            last_name='User',
            password='demo',
            profile_pic=settings.STATIC_URL + 'img/default-profile-pic.jpg',
            resume=settings.STATIC_URL + 'img/default-profile-pic.jpg',
            gpa=3.45,
            university=School.objects.get(name='Brown University'),
            degree=Degree.objects.get(name='Business and Technology'),
        )
        demo_user.is_confirmed = True
        demo_user.video = 'https://www.youtube.com/embed/_OBlgSz8sSM'
        demo_user.hobbies = 'Python,Marketing,Public Speaking,Microsoft Office'
        demo_user.save()

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
                profile_pic=settings.STATIC_URL + 'img/default-profile-pic.jpg',
                resume=settings.STATIC_URL + 'img/default-profile-pic.jpg',
                gpa=randint(int(2), int(100 * 4)) / 100.0,
                university=School.objects.all().order_by('?').first(),
                degree=Degree.objects.all().order_by('?').first()
            )
            user.is_confirmed = True
            user.save()

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
            user.save()

    companies = [
        ['Goldman Sachs', MyUser.objects.get(first_name='Jeff')],
        ['JPMorgan Chase', MyUser.objects.get(first_name='Pablo')],
        ['Morgan Stanley', MyUser.objects.get(first_name='Jaime')],
        ['American Express', MyUser.objects.get(first_name='Naome')]
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
            Job.objects.create(
                company=Company.objects.order_by('?').first(),
                title=job[0],
                contact_email=contact_email,
                description=description,
                location=job[1],
                list_date_start=start,
                list_date_end=end,
            )

    # Create applicants
    applicants = [
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
    if not Applicant.objects.filter(name='{0} {1}'.format(applicants[0][0], applicants[0][1])).exists():
        for applicant in applicants:
            _user = MyUser.objects.get(first_name=applicant[0])
            Applicant.objects.create(
                user=_user,
                resume=settings.STATIC_URL + 'img/default-profile-pic.jpg',
                name='{0} {1}'.format(_user.first_name, _user.last_name),
                email=_user.email,
                university='{} ({})'.format(_user.university, _user.degree)
            )

    # Add applicants to jobs
    created_applicants = Applicant.objects.all()
    for applicant in created_applicants:
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
            'company_username': company.username,
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
            Q(user=user) | Q(collaborators=user) & Q(is_active=True))

        if company_qs.exists():
            company = company_qs[0]
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
                'collaborators': company.get_collaborators_info,
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
        registered_uni = False

        if domain.endswith(tuple(uni_emails)):
            registered_uni = True

        context = {
            'registered_uni': registered_uni
        }
    return render(request, 'auth/selection.html', context)


@cache_page(60 * 60 * 24 * 60)
def privacy_policy(request):
    return render(request, 'general/privacy_policy.html', {})


@cache_page(60 * 60 * 24 * 60)
def terms_of_use(request):
    return render(request, 'general/terms_of_use.html', {})
