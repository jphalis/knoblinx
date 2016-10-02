from django.shortcuts import render
from django.views.decorators.cache import cache_page

from accounts.models import MyUser

# Create your views here.


@cache_page(60 * 3)
def tagged_list(request, tag):
    users = MyUser.objects.filter(skills__icontains='{}'.format(tag))[:50]
    return render(request, 'tags/tagged_list.html', {'users': users})
