"""
Various utility functions.
"""

from django.conf import settings
import boto
from boto.regioninfo import RegionInfo
from boto.ses import SESConnection

# dkim isn't required, but we'll use it if we have it.
try:
    import dkim
    HAS_DKIM = True
except ImportError:
    HAS_DKIM = False

DKIM_DOMAIN = getattr(settings, "DKIM_DOMAIN", None)
DKIM_PRIVATE_KEY = getattr(settings, 'DKIM_PRIVATE_KEY', None)
DKIM_SELECTOR = getattr(settings, 'DKIM_SELECTOR', 'ses')
DKIM_HEADERS = getattr(settings, 'DKIM_HEADERS', ('From', 'To', 'Cc', 'Subject'))


def get_boto_ses_connection():
    """
    Shortcut for instantiating and returning a boto SESConnection object.

    :rtype: boto.ses.SESConnection
    :returns: A boto SESConnection object, from which email sending is done.
    """

    access_key_id = getattr(
        settings, 'CUCUMBER_SES_ACCESS_KEY_ID',
        getattr(settings, 'AWS_ACCESS_KEY_ID', None))
    access_key = getattr(
        settings, 'CUCUMBER_SES_SECRET_ACCESS_KEY',
        getattr(settings, 'AWS_SECRET_ACCESS_KEY', None))

    return boto.connect_ses(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key,
        region=get_ses_region()
    )


def dkim_sign(message):
    """
    :returns: A signed email message if dkim package and settings are available.
    """

    if not HAS_DKIM:
        return message

    if not (DKIM_DOMAIN and DKIM_PRIVATE_KEY):
        return message

    sig = dkim.sign(
        message,
        DKIM_SELECTOR,
        DKIM_DOMAIN,
        DKIM_PRIVATE_KEY,
        include_headers=DKIM_HEADERS)
    return sig + message


def get_ses_region():
    """
    :returns: A boto RegionInfo object.
    """
    region_name = getattr(
        settings, 'CUCUMBER_SES_REGION_NAME',
        getattr(settings, 'AWS_SES_REGION_NAME',
                SESConnection.DefaultRegionName))
    region_endpoint = getattr(
        settings, 'CUCUMBER_SES_REGION_ENDPOINT',
        getattr(settings, 'AWS_SES_REGION_ENDPOINT',
                SESConnection.DefaultRegionEndpoint))
    return RegionInfo(name=region_name, endpoint=region_endpoint)
