#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'sentry>=5.0.14',
    'requests>=0.13.9',
    'BeautifulSoup>=3.2.1'
]

f = open('README.rst')
readme = f.read()
f.close()

setup(
    name='sentry-jira',
    version='0.6.5',
    author='Adam Thurlow',
    author_email='thurloat@gmail.com',
    url='http://github.com/thurloat/sentry-jira',
    description='A Sentry extension which creates JIRA issues from sentry events.',
    long_description=readme,
    license='BSD',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'sentry.apps': [
            'sentry_jira = sentry_jira',
            ],
        'sentry.plugins': [
            'sentry_jira = sentry_jira.plugin:JIRAPlugin'
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development'
    ],
)