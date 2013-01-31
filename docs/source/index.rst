.. sentry-jira documentation master file, created by
   sphinx-quickstart on Mon Sep 10 15:06:37 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sentry-jira's documentation
======================================


Configuration Overview
----------------------

Go to your project's configuration page (Projects -> [Project]) and select the
JIRA tab. Enter the JIRA credentials and Project configuration and save changes.
Filling out the form is a two step process (one to fill in data, one to select
project).

Once the configuration is saved, you have the option of filling in raw field
names (comma separated) that you don't want displayed on the create form. This
is useful if you have plugins installed which use custom fields to store
additional data on Issues.

Configuration Tips
------------------

 - JIRA >= 5.0 is required.

 - You should use `https://<instanceurl>` for the configuration since the plugin
   uses basic auth with the JIRA API to authenticate requests.

 - Ensure that the account you're using has a few key permissions:
    1. CREATE_ISSUE
    2. ASSIGN_ISSUE
    3. USER_PICKER

 - You cannot link to a JIRA server behind a firewall, unless sentry is also
   behind that firewall.

 - You need to configure the plugin for each Sentry project, and you have the
   ability to assign a default JIRA project for each sentry project.

 - JIRA servers with self-signed SSL Certs are supported.


Change Log
----------

There have been a few changes recently that depend on the version of sentry
that is installed alongside the plugin, so I'm keeping track of changes for
versions of the plugins (along with which version of sentry they actually
support).

0.7.1
#####

 - Add support for self-signed SSL Certs for JIRA instances
 
 - Removes self-included select2 library in favour of the one built into sentry

 - Now requires at least Sentry v. 5.3.3

0.6.12
######

 - Add support for the `select` custom field type in JIRA

 - Fixed form -> API type conversions 

 - Add more specific cache keys for hosted sentry support

 - Supports Sentry v 5.0.x - 5.2.x

0.6.x
#####

 - Old versions, don't use them.

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

