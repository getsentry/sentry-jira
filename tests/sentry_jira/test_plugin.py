from __future__ import absolute_import

import responses

from django.http import HttpRequest
from exam import fixture
from sentry.testutils import TestCase

from sentry_jira.plugin import JIRAPlugin


class JIRAPluginTest(TestCase):
    @fixture
    def plugin(self):
        return JIRAPlugin()

    # TODO(dcramer): assert request body
    # TODO(dcramer): pull full fixture from JIRA
    @responses.activate
    def test_create_issue(self):
        responses.add('POST', 'https://jira.atlassian.com/rest/api/2/issue',
                      json={"key": "JIRA-1234"})

        self.plugin.set_option('instance_url', 'https://jira.atlassian.com', self.project)
        self.plugin.set_option('username', 'example', self.project)
        self.plugin.set_option('password', 'example', self.project)

        request = HttpRequest()
        group = self.create_group(message='Hello world', culprit='foo.bar')
        self.create_event(group=group, message='Hello world')

        form_data = {

        }

        with self.options({'system.url-prefix': 'http://example.com'}):
            response = self.plugin.create_issue(request, group, form_data)

        assert response == ('JIRA-1234', None)
