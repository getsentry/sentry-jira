from __future__ import absolute_import

import responses

from django.core.urlresolvers import reverse
from exam import fixture
from sentry.models import GroupMeta
from sentry.plugins import register, unregister
from sentry.testutils import TestCase
from sentry.utils import json

from sentry_jira.plugin import JIRAPlugin


def jira_mock():
    # TODO(dcramer): we cannot currently assert on auth, which is pretty damned
    # important

    priority_response = [
        {
            'self': 'https://getsentry.atlassian.net/rest/api/2/priority/1',
            'statusColor': '#d04437',
            'description': 'This problem will block progress.',
            'iconUrl': 'https://getsentry.atlassian.net/images/icons/priorities/highest.svg',
            'name': 'Highest',
            'id': '1'
        },
    ]

    project_response = [
        {
            'expand': 'description,lead,url,projectKeys',
            'self': 'https://getsentry.atlassian.net/rest/api/2/project/10000',
            'id': '10000',
            'key': 'SEN',
            'name': 'Sentry',
            'avatarUrls': {
                '48x48': 'https://getsentry.atlassian.net/secure/projectavatar?avatarId=10324',
                '24x24': 'https://getsentry.atlassian.net/secure/projectavatar?size=small&avatarId=10324',
                '16x16': 'https://getsentry.atlassian.net/secure/projectavatar?size=xsmall&avatarId=10324',
                '32x32': 'https://getsentry.atlassian.net/secure/projectavatar?size=medium&avatarId=10324'
            },
            'projectTypeKey': 'software'
        },
    ]

    # TODO(dcramer): find one of these
    versions_response = []

    create_meta_response = {
        'expand': 'projects',
        'projects': [
            {
                'expand': 'issuetypes',
                'self': 'https://getsentry.atlassian.net/rest/api/2/project/10000',
                'id': '10000',
                'key': 'SEN',
                'name': 'Sentry',
                'avatarUrls': {
                    '48x48': 'https://getsentry.atlassian.net/secure/projectavatar?avatarId=10324',
                    '24x24': 'https://getsentry.atlassian.net/secure/projectavatar?size=small&avatarId=10324',
                    '16x16': 'https://getsentry.atlassian.net/secure/projectavatar?size=xsmall&avatarId=10324',
                    '32x32': 'https://getsentry.atlassian.net/secure/projectavatar?size=medium&avatarId=10324'
                },
                'issuetypes': [
                    {
                        'self': 'https://getsentry.atlassian.net/rest/api/2/issuetype/10002',
                        'id': '10002',
                        'description': 'A task that needs to be done.',
                        'iconUrl': 'https://getsentry.atlassian.net/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype',
                        'name': 'Task',
                        'subtask': False,
                        'expand': 'fields',
                        'fields': {
                            'summary': {
                                'required': True,
                                'schema': {
                                    'type': 'string',
                                    'system': 'summary',
                                },
                                'name': 'Summary',
                                'hasDefaultValue': False,
                                'operations': ['set']
                            },
                            'issuetype': {
                                'required': True,
                                'schema': {
                                    'type': 'issuetype',
                                    'system': 'issuetype'
                                },
                                'name': 'Issue Type',
                                'hasDefaultValue': False,
                                'operations': [],
                                'allowedValues': [
                                    {
                                        'self': 'https://getsentry.atlassian.net/rest/api/2/issuetype/10002',
                                        'id': '10002',
                                        'description': 'A task that needs to be done.',
                                        'iconUrl': 'https://getsentry.atlassian.net/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype',
                                        'name': 'Task',
                                        'subtask': False,
                                        'avatarId': 10318,
                                    }
                                ]
                            },
                            'components': {
                                'required': False,
                                'schema': {
                                    'type': 'array',
                                    'items': 'component',
                                    'system': 'components',
                                },
                                'name': 'Component/s',
                                'hasDefaultValue': False,
                                'operations': ['add', 'set', 'remove'],
                                'allowedValues': [],
                            },
                            'description': {
                                'required': False,
                                'schema': {
                                    'type': 'string',
                                    'system': 'description',
                                },
                                'name': 'Description',
                                'hasDefaultValue': False,
                                'operations': ['set']
                            },
                            'project': {
                                'required': True,
                                'schema': {
                                    'type': 'project',
                                    'system': 'project'
                                },
                                'name': 'Project',
                                'hasDefaultValue': False,
                                'operations': ['set'],
                                'allowedValues': [
                                    {
                                        'self': 'https://getsentry.atlassian.net/rest/api/2/project/10000',
                                        'id': '10000',
                                        'key': 'SEN',
                                        'name': 'Sentry',
                                        'avatarUrls': {
                                            '48x48': 'https://getsentry.atlassian.net/secure/projectavatar?avatarId=10324',
                                            '24x24': 'https://getsentry.atlassian.net/secure/projectavatar?size=small&avatarId=10324',
                                            '16x16': 'https://getsentry.atlassian.net/secure/projectavatar?size=xsmall&avatarId=10324',
                                            '32x32': 'https://getsentry.atlassian.net/secure/projectavatar?size=medium&avatarId=10324',
                                        }
                                    }
                                ]
                            },
                            'reporter': {
                                'required': True,
                                'schema': {
                                    'type': 'user',
                                    'system': 'reporter',
                                },
                                'name': 'Reporter',
                                'autoCompleteUrl': 'https://getsentry.atlassian.net/rest/api/latest/user/search?username=',
                                'hasDefaultValue': False,
                                'operations': ['set'],
                            },
                            'fixVersions': {
                                'required': False,
                                'schema': {
                                    'type': 'array',
                                    'items': 'version',
                                    'system': 'fixVersions',
                                },
                                'name': 'Fix Version/s',
                                'hasDefaultValue': False,
                                'operations': ['set', 'add', 'remove'],
                                'allowedValues': [],
                            },
                            'priority': {
                                'required': False,
                                'schema': {
                                    'type': 'priority',
                                    'system': 'priority',
                                },
                                'name': 'Priority',
                                'hasDefaultValue': True,
                                'operations': ['set'],
                                'allowedValues': [
                                    {
                                        'self': 'https://getsentry.atlassian.net/rest/api/2/priority/1',
                                        'iconUrl': 'https://getsentry.atlassian.net/images/icons/priorities/highest.svg',
                                        'name': 'Highest',
                                        'id': '1'
                                    },
                                ]
                            },
                            'customfield_10003': {
                                'required': False,
                                'schema': {
                                    'type': 'array',
                                    'items': 'string',
                                    'custom': 'com.pyxis.greenhopper.jira:gh-sprint',
                                    'customId': 10003,
                                },
                                'name': 'Sprint',
                                'hasDefaultValue': False,
                                'operations': ['set']
                            },
                            'labels': {
                                'required': False,
                                'schema': {
                                    'type': 'array',
                                    'items': 'string',
                                    'system': 'labels',
                                },
                                'name': 'Labels',
                                'autoCompleteUrl': 'https://getsentry.atlassian.net/rest/api/1.0/labels/suggest?query=',
                                'hasDefaultValue': False,
                                'operations': ['add', 'set', 'remove'],
                            },
                            'attachment': {
                                'required': False,
                                'schema': {
                                    'type': 'array',
                                    'items': 'attachment',
                                    'system': 'attachment',
                                },
                                'name': 'Attachment',
                                'hasDefaultValue': False,
                                'operations': [],
                            },
                            'assignee': {
                                'required': False,
                                'schema': {
                                    'type': 'user',
                                    'system': 'assignee',
                                },
                                'name': 'Assignee',
                                'autoCompleteUrl': 'https://getsentry.atlassian.net/rest/api/latest/user/assignable/search?issueKey=null&username=',
                                'hasDefaultValue': False,
                                'operations': ['set'],
                            }
                        }
                    }
                ]
            }
        ]
    }

    mock = responses.RequestsMock(assert_all_requests_are_fired=False)
    mock.add(mock.GET, 'https://getsentry.atlassian.net/rest/api/2/priority',
             json=priority_response)
    mock.add(mock.GET, 'https://getsentry.atlassian.net/rest/api/2/project',
             json=project_response)
    mock.add(mock.GET, 'https://getsentry.atlassian.net/rest/api/2/project/SEN/versions',
             json=versions_response)
    # TODO(dcramer): validate input params
    # create_meta_params = {
    #     'projectKeys': 'SEN',
    #     'expand': 'projects.issuetypes.fields'
    # }
    mock.add(mock.GET, 'https://getsentry.atlassian.net/rest/api/2/issue/createmeta',
             json=create_meta_response)
    mock.add(mock.POST, 'https://getsentry.atlassian.net/rest/api/2/issue',
             json={'key': 'SEN-1234'})
    return mock


class JIRAPluginTest(TestCase):
    plugin_cls = JIRAPlugin

    def setUp(self):
        super(JIRAPluginTest, self).setUp()
        register(self.plugin_cls)
        self.group = self.create_group(message='Hello world', culprit='foo.bar')
        self.event = self.create_event(group=self.group, message='Hello world')

    def tearDown(self):
        unregister(self.plugin_cls)
        super(JIRAPluginTest, self).tearDown()

    @fixture
    def plugin(self):
        return self.plugin_cls()

    @fixture
    def action_path(self):
        project = self.project
        return reverse('sentry-group-plugin-action', args=[
            project.organization.slug, project.slug, self.group.id, self.plugin.slug,
        ])

    @fixture
    def configure_path(self):
        project = self.project
        return reverse('sentry-configure-project-plugin', args=[
            project.organization.slug, project.slug, self.plugin.slug,
        ])

    def test_create_issue_renders(self):
        project = self.project
        plugin = self.plugin

        plugin.set_option('username', 'foo', project)
        plugin.set_option('password', 'bar', project)
        plugin.set_option('instance_url', 'https://getsentry.atlassian.net', project)
        plugin.set_option('default_project', 'SEN', project)

        self.login_as(self.user)

        with jira_mock(), self.options({'system.url-prefix': 'http://example.com'}):
            response = self.client.get(self.action_path)

        assert response.status_code == 200, vars(response)
        self.assertTemplateUsed(response, 'sentry_jira/create_jira_issue.html')

    def test_create_issue_saves(self):
        project = self.project
        plugin = self.plugin

        plugin.set_option('username', 'foo', project)
        plugin.set_option('password', 'bar', project)
        plugin.set_option('instance_url', 'https://getsentry.atlassian.net', project)
        plugin.set_option('default_project', 'SEN', project)

        self.login_as(self.user)

        with jira_mock() as mock:
            response = self.client.post(self.action_path, {
                'changing_issuetype': '0',
                'issuetype': '10002',
                'priority': '1',
                'customfield_10003': '',
                'project': '10000',
                'description': 'A ticket description',
                'summary': 'A ticket summary',
                'assignee': 'assignee',
                'reporter': 'reporter',
            })

            assert response.status_code == 302, dict(response.context['form'].errors)
            assert GroupMeta.objects.get(group=self.group, key='jira:tid').value == 'SEN-1234'

            jira_request = mock.calls[-1].request
            assert jira_request.url == 'https://getsentry.atlassian.net/rest/api/2/issue'
            assert json.loads(jira_request.body) == {
                "fields": {
                    "priority": {"id": "1"},
                    "description": "A ticket description",
                    "reporter": {"name": "reporter"},
                    "summary": "A ticket summary",
                    "project": {"id": "10000"},
                    "assignee": {"name": "assignee"},
                    "issuetype": {"id": "10002"},
                },
            }

    def test_configure_renders(self):
        self.login_as(self.user)
        with jira_mock():
            response = self.client.get(self.configure_path)
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'sentry_jira/project_conf_form.html')
        assert '<input type="hidden" name="plugin" value="jira" />' in response.content
        assert 'default_project' not in response.content
        assert 'default_issue_type' not in response.content
        assert 'default_priority' not in response.content
        assert 'ignored_fields' not in response.content

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
