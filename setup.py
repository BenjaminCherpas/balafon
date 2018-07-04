# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('balafon').__version__

setup(
    name='balafon',
    version=VERSION,
    description='Contacts management',
    packages=find_packages(),
    include_package_data=True,
    author='Luc Jean',
    author_email='ljean@apidev.fr',
    license='CeCILL 2.1',
    zip_safe=False,
    install_requires=[
        'django >= 1.9, <2.0',
        'djangorestframework',
        'django-extensions',
        'apidev-coop_cms>=1.3.1',
        'beautifulsoup4',
        'django-wkhtmltopdf',
        'xlwt',
        'xlrd',
        'django-simple-captcha',
        'django-registration',
        'model_mommy',
        'django-cors-headers',
    ],
    dependency_links=[
        # Python3 version
        'git+https://github.com/ljean/coop_cms.git@98d869ad61eaf381f1d081e0e862e52f1bf2f814#egg=apidev_coop_cms-1.3.1'
    ],
    long_description=open('README.rst').read(),
    url='https://github.com/ljean/balafon',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Natural Language :: English',
        'Natural Language :: French',
        'Topic :: Office/Business',
    ],
)
