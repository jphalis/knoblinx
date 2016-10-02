from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _


def rand_n_digits(n):
    """
    Returns an integer with n digits.
    """
    import random
    return random.randint(10**(n - 1), (10**n) - 1)


def gen_rand_username(initial_text='user', num_digits=7):
    """
    Generates a random username with some text and n digits following.
    """
    from django.utils.text import slugify
    return slugify(str(initial_text) + str(rand_n_digits(num_digits)))


def clean_passwords(data, password1, password2):
    if password1 in data and password2 in data:
        if data[password1] != data[password2]:
            raise forms.ValidationError(
                _("You must type the same password each time."))
        validate_password(data[password2])
    return data[password2]
