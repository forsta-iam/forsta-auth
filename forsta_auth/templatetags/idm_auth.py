import django_otp
from django import template

from django_otp.plugins.otp_totp.models import TOTPDevice

register = template.Library()

@register.filter('devices_for_user')
def devices_for_user(value):
    devices = list(django_otp.devices_for_user(value))
    for device in devices:
        if isinstance(device, TOTPDevice):
            device.type = 'TOTP'
            device.icon = 'qrcode'

    return devices