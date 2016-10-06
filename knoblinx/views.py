from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from accounts.models import Company
from jobs.models import Job

# Create views here.


# REMOVE WHEN IN PRODUCTION ! ! !
def generate_data(request):
    from datetime import datetime, timedelta
    from django.contrib import messages
    from django.shortcuts import redirect
    from accounts.models import MyUser, School

    # Create demo user
    if not MyUser.objects.filter(email='demo@demo.com').exists():
        demo_user = MyUser.objects.create_user(
            email='demo@demo.com',
            first_name='Sample',
            last_name='User',
            password='demo'
        )
        demo_user.is_confirmed = True
        demo_user.video = 'https://www.youtube.com/embed/_OBlgSz8sSM'
        demo_user.skills = 'Python,Marketing,Public Speaking,Microsoft Office'
        demo_user.degree = 'Business Administration'
        demo_user.save()

    # Create schools
    schools = [
        ['Brown University', 'Providence, Rhode Island'],
        ['Columbia University', 'New York, New York'],
        ['Cornell University', 'Ithaca, New York'],
        ['Dartmouth College', 'Hanover, New Hampshire'],
        ['Harvard University', 'Cambridge, Massachusetts'],
        ['Princeton University', 'Princeton, New Jersey'],
        ['University of Pennsylvania', 'Philadelphia, Pennsylvania'],
        ['Yale University', 'New Haven, Connecticut']
    ]
    for school in schools:
        if not School.objects.filter(name=school[0]).exists():
            School.objects.create(name=school[0], location=school[1])

    # Create users
    users = [
        ['John', 'Doe'],
        ['Bill', 'Clarkson'],
        ['Jessica', 'Hall'],
    ]
    for user in users:
        if not MyUser.objects.filter(first_name=user[0]).exists():
            user = MyUser.objects.create_user(
                email='{}.{}@demo.com'.format(user[0], user[1]),
                first_name=user[0],
                last_name=user[1],
                password='demo'
            )
            user.is_confirmed = True
            user.save()

    # Create companies
    companies = [
        ['Goldman Sachs', MyUser.objects.get(first_name='John')],
        ['JPMorgan Chase', MyUser.objects.get(first_name='Bill')],
        ['Morgan Stanley', MyUser.objects.get(first_name='Jessica')]
    ]
    for company in companies:
        if not Company.objects.filter(name=company[0]).exists():
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
        [Company.objects.order_by('?').first(), 'Sales Associate',
         description, 'New York, NY', start, end],
        [Company.objects.order_by('?').first(), 'IT Consultant',
         description, 'Hoboken, NJ', start, end],
        [Company.objects.order_by('?').first(), 'Event Manager',
         description, 'Los Angeles, CA', start, end],
        [Company.objects.order_by('?').first(), 'Senior Director',
         description, 'New York, NY', start, end],
        [Company.objects.order_by('?').first(), 'EVP',
         description, 'Boston, MA', start, end],
        [Company.objects.order_by('?').first(), 'Software Developer',
         description, 'Menlo Park, CA', start, end],
        [Company.objects.order_by('?').first(), 'Marketing Associate',
         description, 'La Jolla, CA', start, end]
    ]
    for job in jobs:
        if not Job.objects.filter(title=job[1]).exists():
            Job.objects.create(
                company=job[0],
                title=job[1],
                contact_email=contact_email,
                description=job[2],
                location=job[3],
                list_date_start=job[4],
                list_date_end=job[5]
            )

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


@cache_page(60 * 3)
@login_required
def home(request):
    jobs = Job.objects.active()
    recent_posts = Job.objects.recent()[:7]

    paginator = Paginator(jobs, 12)  # Show 12 jobs per page
    page = request.GET.get('page')

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        jobs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        jobs = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs,
        'recent_posts': recent_posts,
        'user': request.user,
    }
    return render(request, 'jobs/list.html', context)


@cache_page(60 * 60 * 24 * 60)
def privacy_policy(request):
    return render(request, 'general/privacy_policy.html', {})


@cache_page(60 * 60 * 24 * 60)
def terms_of_use(request):
    return render(request, 'general/terms_of_use.html', {})
