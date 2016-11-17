from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# Create your managers here.


class EmailConfirmationManager(models.Manager):
    def send_confirmation(
            self, user, request,
            subject_template_name='KnobLinx Account Confirmation',
            email_template_name='auth/account_confirm_email.html',
            use_https=False,
            token_generator=default_token_generator,
            extra_email_context=None,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_email_template_name='auth/account_confirm_email.html'):

        obj, created = self.model.objects.using('default').get_or_create(
            user=user, key=token_generator.make_token(user=user))

        emails = self.model.objects.filter(
            user=user).values_list("pk", flat=True).order_by('sent_date')

        if emails.count() > 1:
            self.model.objects.exclude(pk__in=list(emails[:1])).delete()

        context = {
            'email': obj.user.email,
            'domain': request.get_host(),
            'site_name': request.META['SERVER_NAME'],
            'uid': urlsafe_base64_encode(force_bytes(obj.user.pk)),
            'user': obj.user,
            'token': obj.key,
            'protocol': 'https' if use_https else 'http',
        }
        subject = subject_template_name
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body,
                                               from_email, [obj.user.email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name,
                                                 context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
        return obj

    def confirm(self, user):
        obj = get_object_or_404(self.model, user=user)
        if obj.key_valid():
            obj.user.is_confirmed = True
            obj.user.save(update_fields=['is_confirmed'])
            obj.delete()
            return True
        return False
