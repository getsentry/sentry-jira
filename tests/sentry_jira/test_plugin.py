from __future__ import absolute_import

import responses

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from exam import fixture
from sentry.plugins import register, unregister
from sentry.testutils import TestCase

from sentry_jira.plugin import JIRAPlugin


def jira_mock():
    # TODO(dcramer): we cannot currently assert on auth, which is pretty damned
    # important

    priority_response = [
        {
            "self": "https://getsentry.atlassian.net/rest/api/2/priority/1",
            "statusColor": "#d04437",
            "description": "This problem will block progress.",
            "iconUrl": "https://getsentry.atlassian.net/images/icons/priorities/highest.svg",
            "name": "Highest",
            "id": "1"
        },
    ]

    project_response = [
        {
            "expand": "description,lead,url,projectKeys",
            "self": "https://getsentry.atlassian.net/rest/api/2/project/10000",
            "id": "10000",
            "key": "SEN",
            "name": "Sentry",
            "avatarUrls": {
                "48x48": "https://getsentry.atlassian.net/secure/projectavatar?avatarId=10324",
                "24x24": "https://getsentry.atlassian.net/secure/projectavatar?size=small&avatarId=10324",
                "16x16": "https://getsentry.atlassian.net/secure/projectavatar?size=xsmall&avatarId=10324",
                "32x32": "https://getsentry.atlassian.net/secure/projectavatar?size=medium&avatarId=10324"
            },
            "projectTypeKey": "software"
        },
    ]

    mock = responses.RequestsMock(assert_all_requests_are_fired=False)
    mock.add(mock.GET, 'https://getsentry.atlassian.net/rest/api/2/priority',
             json=priority_response)
    mock.add(mock.GET, 'https://getsentry.atlassian.net/rest/api/2/project',
             json=project_response)
    return mock


class JIRAPluginTest(TestCase):
    plugin_cls = JIRAPlugin

    @fixture
    def plugin(self):
        return self.plugin_cls()

    @fixture
    def configure_path(self):
        project = self.project
        return reverse('sentry-configure-project-plugin', args=[
            project.organization.slug, project.slug, self.plugin.slug,
        ])

    def setUp(self):
        super(JIRAPluginTest, self).setUp()
        register(self.plugin_cls)

    def tearDown(self):
        unregister(self.plugin_cls)
        super(JIRAPluginTest, self).tearDown()

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

    @responses.activate
    def test_configure_renders(self):
        self.login_as(self.user)
        response = self.client.get(self.configure_path)
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'sentry_jira/project_conf_form.html')
        assert '<input type="hidden" name="plugin" value="jira" />' in response.content
        assert 'default_project' not in response.content
        assert 'default_issue_type' not in response.content
        assert 'default_priority' not in response.content
        assert 'ignored_fields' not in response.content

    @responses.activate
    def test_configure_without_credentials(self):
        self.login_as(self.user)
        with jira_mock():
            response = self.client.post(self.configure_path, {
                'plugin': 'jira',
                'jira-username': 'foo',
                'jira-password': 'bar',
                'jira-instance_url': 'https://getsentry.atlassian.net',
            })
        assert response.status_code == 302

        project = self.project
        plugin = self.plugin

        assert plugin.get_option('username', project) == 'foo'
        assert plugin.get_option('password', project) == 'bar'
        assert plugin.get_option('instance_url', project) == 'https://getsentry.atlassian.net'

    @responses.activate
    def test_configure_renders_with_credentials(self):
        project = self.project
        plugin = self.plugin

        plugin.set_option('username', 'foo', project)
        plugin.set_option('password', 'bar', project)
        plugin.set_option('instance_url', 'https://getsentry.atlassian.net', project)

        self.login_as(self.user)

        with jira_mock():
            response = self.client.get(self.configure_path, {
                'plugin': 'jira',
            })
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'sentry_jira/project_conf_form.html')

        assert 'default_project' in response.content
        assert 'default_issue_type' in response.content
        assert 'default_priority' in response.content
        assert 'ignored_fields' in response.content
