from itertools import chain

from django.db.models import Q
from django.utils import timezone
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
        return Job.objects.filter(
            Q(list_date_start__lte=timezone.now()) &
            Q(list_date_end__gt=timezone.now()) &
            Q(title__icontains=query) |
            Q(location__icontains=query)
        )

    def users(self, query):
        return MyUser.objects.filter(
            Q(is_active=True) &
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

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
        return list(chain(companies, jobs, users))
