from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from sentry.models import GroupMeta
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
        if not self.get_option('default_project', project):
            return False
        return True

    def get_jira_client(self, project):
        instance = self.get_option('instance_url', project)
        username = self.get_option('username', project)
        pw = self.get_option('password', project)
        return JIRAClient(instance, username, pw)

    def get_initial_form_data(self, request, group, event):
        initial = {
            'summary': self._get_group_title(request, group, event),
            'description': self._get_group_description(request, group, event),
            'project_key': self.get_option('default_project', group.project),
            'jira_client': self.get_jira_client(group.project)
        }

        if request.GET.get("issuetype"):
            # start rendering form with different issue type
            initial["issuetype"] = request.GET.get("issuetype")

        return initial

    def get_new_issue_title(self):
        return "Create JIRA Issue"

    def create_issue(self, group, form_data):
        """
        Since this is called wrapped in a try/catch on ValidationError to display
        an end user error, that's what I'll throw when JIRA doesn't like it.
        """
        jira_client = self.get_jira_client(group.project)
        issue_response = jira_client.create_issue(form_data)

        if issue_response.status_code is 200:
            return issue_response.json.get("key"), None
        else:
            # return some sort of error.
            errdict = {"__all__": None}
            if issue_response.status_code == 500:
                errdict["__all__"] = "JIRA Internal Server Error."
            elif issue_response.status_code == 400:
                for k in issue_response.json["errors"].keys():
                    errdict[k] = [issue_response.json["errors"][k],]
                errdict["__all__"] = issue_response.json["errorMessages"]
            else:
                errdict["__all__"] = "Something went wrong, Sounds like a configuration issue: code %s" % issue_response.status_code
            return None, errdict

    def get_issue_url(self, group, issue_id):
        instance = self.get_option('instance_url', group.project)
        return "%s/browse/%s" % (instance, issue_id)

    def view(self, request, group, **kwargs):
        """
        Overriding the super to alter the error checking functionality. Method
        source had to be copied in an altered, see huge comment below for changes.
        """
        if not self.is_configured(group.project):
            return self.render(self.not_configured_template)

        prefix = self.get_conf_key()
        event = group.get_latest_event()

        form = self.new_issue_form(request.POST or None, initial=self.get_initial_form_data(request, group, event))
        if form.is_valid():
            try:
                ################################################################
                # This is the only different part.
                # TODO: Find a workaround to remove this in the future. Hate Copypasta code.
                #
                issue_id, errors = self.create_issue(group, form.cleaned_data)
                if errors:
                    form.errors.update(errors)
                #
                #
                ################################################################
            except forms.ValidationError, e:
                form.errors['__all__'] = u'Error creating issue: %s' % e

        if form.is_valid():
            GroupMeta.objects.set_value(group, '%s:tid' % prefix, issue_id)

            return self.redirect(reverse('sentry-group', args=[group.project_id, group.pk]))

        context = {
            'form': form,
            'title': self.get_new_issue_title(),
            }

        return self.render(self.create_issue_template, context)