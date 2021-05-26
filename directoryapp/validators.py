import phonenumbers
from django.core.exceptions import ValidationError


def validate_us_phone_number(number):
    parsed_number = phonenumbers.parse(number, 'US')  # US code for now
    if not phonenumbers.is_valid_number(parsed_number):
        raise ValidationError('Not a valid US Phone Number.')

