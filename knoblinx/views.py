from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from accounts.models import Company, MyUser, School
from activity.models import Activity
from jobs.models import Job

# Create views here.


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
            'all_post_count': Job.objects.all().count(),
            'jobs': jobs,
            'recent_posts': Job.objects.recent()[:7],
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
