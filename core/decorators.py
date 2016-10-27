from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404

from accounts.models import Company
from jobs.models import Job

# Create your decorators here.


def user_is_company_collab(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        _obj_exists = True

        if 'job_pk' in kwargs:
            job = get_object_or_404(Job, pk=kwargs['job_pk'])
            _is_company_owner = job.company.user == user
            _is_company_collab = job.company.collaborators.filter(
                pk=user.pk).exists()
        elif 'username' in kwargs:
            company = get_object_or_404(
                Company, Q(is_active=True), username=kwargs['username'])
            _is_company_owner = company.user == user
            _is_company_collab = company.collaborators.filter(
                pk=user.pk).exists()
        elif 'company_pk' in kwargs:
            company = get_object_or_404(
                Company, Q(is_active=True), pk=kwargs['company_pk'])
            _is_company_owner = company.user == user
            _is_company_collab = company.collaborators.filter(
                pk=user.pk).exists()
        else:
            _obj_exists = False

        if _obj_exists and _is_company_owner or _is_company_collab:
            return function(request, *args, **kwargs)
        raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
