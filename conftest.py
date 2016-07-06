from __future__ import absolute_import

import os
os.environ.setdefault('DB', 'sqlite')

pytest_plugins = [
    'sentry.utils.pytest'
]


def pytest_configure(config):
    from django.conf import settings
    settings.INSTALLED_APPS += ('sentry_jira',)
