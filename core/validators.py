import os

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

# Create validators here.


def validate_resume_ext(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx']

    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))
