import random
import string
from django.utils.text import slugify
import phonenumbers

from decouple import config
from twilio.rest import Client


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def format_number_for_sms(number):
    parsed_number = phonenumbers.parse(number, 'US')  # US code for now
    if not phonenumbers.is_valid_number(parsed_number):
        return None
    formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    return formatted_number


sid = config('TWILIO_ACCOUNT_SID')
token = config("TWILIO_AUTH_TOKEN")

twilio_client = Client(sid, token)


def send_sms(to, message):
    message = twilio_client.messages.create(
        to=format_number_for_sms(to),
        from_="+13182257525",
        body=message
    )


def get_client_ip(request):
    remote_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    ip = remote_address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        while (len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
            if len(proxies) > 0:
                ip = proxies[0]
                print('IP Address', ip)
    return ip
