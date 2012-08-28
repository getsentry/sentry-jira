sentry-jira
===========

A flexible extension for Sentry which allows you to create issues in JIRA based on sentry events.
It is capable of rendering and saving many custom fields, and will display the proper fields depending on 
which issue type you are trying to create.

Visual Walkthrough
------------------

When viewing a Sentry event, the Actions dropdown now contains a "Create JIRA Issue" button.

.. image:: http://sentry-jira.s3.amazonaws.com/ss1.jpg

The Create JIRA Issue form is fully customized based on your JIRA Configuration and loads different
fields depending on which issue type you choose.

.. image:: http://sentry-jira.s3.amazonaws.com/ss2.png

Once the Issue has been linked through JIRA there's a link that you can follow from Sentry to
go directly to the issue on your configurated JIRA instance.

.. image:: http://sentry-jira.s3.amazonaws.com/ss3.jpg

Installation
------------

Install the package via ``pip``:

::

    pip install sentry-jira

Add ``sentry-jira`` to your ``INSTALLED_APPS`` in your ``sentry.conf.py``:

::

    from sentry.conf.server import *

    INSTALLED_APPS += (
        'sentry_jira',
    )

Configuration
-------------

Go to your project's configuration page (Projects -> [Project]) and select the
JIRA tab. Enter the JIRA credentials and Project configuration and save changes.
Filling out the form is a two step process (one to fill in data, one to select
project).