try:
    VERSION = __import__('pkg_resources').get_distribution('sentry-jira').version
except Exception, e:
    VERSION = "over 9000"
