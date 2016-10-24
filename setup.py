import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-nemo',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    description='A simple Django app interfacing nemo',
    long_description=README,
    url='http:/gitlab.blueline.mg/default/django-nemo.git',
    author='Thomas Ayih-Akakpo',
    author_email='thomas.ayih-akakpo@gulfsat.mg',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved ::  Apache 2.0',
        'Operating System :: Debian 8',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

