import logging
import requests
from sentry.utils import json
import collections
from simplejson.decoder import JSONDecodeError

log = logging.getLogger(__name__)

class JIRAClient(object):
    """
    The JIRA API Client, so you don't have to.
    """

    PROJECT_URL = '/rest/api/2/project'
    META_URL = '/rest/api/2/issue/createmeta'
    CREATE_URL = '/rest/api/2/issue'
    PRIORITIES_URL = '/rest/api/2/priority'
    VERSIONS_URL = '/rest/api/2/project/%s/versions'

    def __init__(self, instance_uri, username, password):
        self.instance_url = instance_uri
        self.username = username
        self.password = password

    def get_projects_list(self):
        return self.make_request('get', self.PROJECT_URL)

    def get_create_meta(self, project):
        return self.make_request('get', self.META_URL, {'projectKeys': project, 'expand': 'projects.issuetypes.fields'})

    def get_versions(self, project):
        return self.make_request('get', self.VERSIONS_URL % project)

    def create_issue(self, raw_form_data):
        """
        Take a set of raw form data and massage it into API postable goodness.
        """
        data = {'fields': raw_form_data}
        print data
        return self.make_request('post', self.CREATE_URL, payload=data)

    def get_priorities(self):
        return self.make_request('get', self.PRIORITIES_URL)

    def make_request(self, method, url, payload=None):
        url = self.instance_url + url
        auth = self.username, self.password
        headers = {'content-type': 'application/json'}
        try:
            if method is 'get':
                r = requests.get(url, params=payload, auth=auth, headers=headers)
            else:
                r = requests.post(url, data=json.dumps(payload), auth=auth, headers=headers)
        except Exception, e:
            logging.error('Error in request to %s: %s' % (url, e.message))
            return None

        return JIRAResponse(r.text, r.status_code)

class JIRAResponse(object):
    """
    A Slimy little wrapper around a python-requests response object that renders
    JSON from JIRA's ordered dicts (fields come back in order, but python obv.
    doesn't care)
    """
    def __init__(self, response_text, status_code):
        self.text = response_text
        try:
            self.json = json.loads(response_text, object_pairs_hook=collections.OrderedDict)
        except JSONDecodeError, e:
            # must be an awful code.
            self.json = None
        self.status_code = status_code