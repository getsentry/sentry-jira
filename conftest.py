from __future__ import absolute_import

pytest_plugins = [
    'sentry.utils.pytest'
]


def pytest_configure(config):
    from django.conf import settings
    settings.INSTALLED_APPS += ('sentry_jira',)
