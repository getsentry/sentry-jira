from django.utils.translation import ugettext_lazy as _
from sentry.plugins.base import register
from sentry.plugins.bases.issue import IssuePlugin
from forms import JIRAOptionsForm, JIRAIssueForm
from sentry_jira.jira import JIRAClient

@register
class JIRAPlugin(IssuePlugin):
    author = "Adam Thurlow"
    author_url = "https://github.com/thurloat/sentry_jira"
    version = "0.1a"

    slug = "jira"
    title = _("JIRA")
    cont_title = title
    conf_key = slug
    project_conf_form = JIRAOptionsForm
    new_issue_form = JIRAIssueForm
    create_issue_template = 'sentry_jira/create_jira_issue.html'

    def is_configured(self, project, **kwargs):
        if not self.get_option('instance_url', project):
            return False
        return True

    def get_jira_client(self, project):
        instance = self.get_option('instance_url', project)
        username = self.get_option('username', project)
        pw = self.get_option('password', project)
        return JIRAClient(instance, username, pw)

    def get_initial_form_data(self, request, group, event):
        return {
            'summary': self._get_group_title(request, group, event),
            'description': self._get_group_description(request, group, event),
            'project_key': self.get_option('default_project', group.project),
            'jira_client': self.get_jira_client(group.project)
        }

    def get_new_issue_title(self):
        return "Create JIRA Issue"

    def create_issue(self, group, form_data):
        jira_client = self.get_jira_client(group.project)
        issue_response = jira_client.create_issue(
            form_data["project_id"],
            form_data["issue_type"],
            form_data["summary"],
            form_data["description"],
            form_data["fix_version"]
        )
        return issue_response["key"]

    def get_issue_url(self, group, issue_id):
        instance = self.get_option('instance_url', group.project)
        return "%s/browse/%s" % (instance, issue_id)

