import logging
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
from jira import JIRAClient

log = logging.getLogger(__name__)

class JIRAOptionsForm(forms.Form):
    instance_url = forms.CharField(
        label=_("JIRA Instance URL"),
        widget=forms.TextInput(attrs={'class': 'span3', 'placeholder': 'e.g. https://jira.atlassian.com'}),
        help_text=_("Enter your JIRA Instance URI, it must be visible to the sentry server.")
    )
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'span3'}),
        help_text=_("Make sure to use a user who has access to create issues on the project.")
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'span3'}),
        help_text=_("Only enter a value if you wish to change it."),
        required=False
    )
    default_project = forms.ChoiceField(
        label=_("Linked Project"),
    )

    def __init__(self, *args, **kwargs):
        super(JIRAOptionsForm, self).__init__(*args, **kwargs)

        initial = kwargs.get("initial")
        if initial:
            # make a connection to JIRA to fetch a default project.
            jira = JIRAClient(initial.get("instance_url"), initial.get("username"), initial.get("password"))
            projects = jira.get_projects_list()
            if projects:
                project_choices = [(p.get('key'), "%s (%s)" % (p.get('name'), p.get('key'))) for p in projects]
                self.fields["default_project"].choices = project_choices
            else:
                del self.fields["default_project"]
        else:
            del self.fields["default_project"]

    def clean_password(self):
        pw = self.cleaned_data.get("password")
        if pw:
            return pw
        else:
            old_pw = self.initial.get("password")
            if not old_pw:
                raise ValidationError("A Password is Required")
            return old_pw

class JIRAIssueForm(forms.Form):
    summary = forms.CharField()
    description = forms.CharField(widget=forms.Textarea())
    project_key = forms.CharField(widget=forms.HiddenInput())
    project_id = forms.CharField(widget=forms.HiddenInput())
    issue_type = forms.ChoiceField()
    priority = forms.ChoiceField()
    fix_version = forms.MultipleChoiceField()



    def __init__(self, *args, **kwargs):
        self.jira_client = None
        initial = kwargs.get("initial")
        self.jira_client = initial.pop("jira_client")
        kwargs["initial"] = initial

        super(JIRAIssueForm, self).__init__(*args, **kwargs)

        meta = self.jira_client.get_create_meta(self.initial.get("project_key"))
        project = meta["projects"][0]

        self.fields["project_id"].initial = project["id"]

        issue_type_choices = [(it["id"], it["name"]) for it in project["issuetypes"]]
        self.fields["issue_type"].choices = issue_type_choices

        priorities = self.jira_client.get_priorities()
        self.fields["priority"].choices = [(p["id"], p["name"]) for p in priorities]

        versions = self.jira_client.get_versions(self.initial.get("project_key"))
        self.fields["fix_version"].choices = [(v["id"], v["name"]) for v in versions]


