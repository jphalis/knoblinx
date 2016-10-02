from itertools import chain

# from django.contrib.auth.decorators import login_required
from django.db.models import Q
# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
from django.views.generic.list import ListView

from accounts.models import MyUser, Company
from core.mixins import LoginRequiredMixin
from jobs.models import Job

# Create your views here.


class SearchListView(LoginRequiredMixin, ListView):
    # model = MyUser
    template_name = 'search/list.html'

    def companies(self, query):
        return Company.objects.filter(name__icontains=query)

    def jobs(self, query):
        results = Job.objects.filter(
            Q(is_active=True) &
            Q(title__icontains=query) |
            Q(location__icontains=query)
        )
        return results

    def users(self, query):
        results = MyUser.objects.filter(
            Q(is_active=True) &
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        return results

    def recent_jobs(self):
        return Job.objects.recent()[:18]

    def get_context_data(self, *args, **kwargs):
        context = super(SearchListView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        context['companies'] = self.companies(query)
        context['jobs'] = self.jobs(query)
        context['users'] = self.users(query)
        context['recent_jobs'] = self.recent_jobs()
        return context

    def get_queryset(self, *args, **kwargs):
        query = self.request.GET.get('q', None)
        companies = self.companies(query)
        jobs = self.jobs(query)
        users = self.users(query)
        all_results = list(chain(companies, jobs, users))
        # all_results.sort(key=lambda x: x.created)
        return all_results


# @login_required
# @require_http_methods(['GET'])
# def search_ajax(request):
#     q = request.GET.get('q', None)
#     data = {}

#     if q:
#         users = MyUser.objects.filter(username__icontains=q, is_active=True)
#         data = [{'username': user.username} for user in users]
#     return JsonResponse(data, safe=False)
