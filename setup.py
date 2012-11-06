# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='django-mobileme',
    version=__import__('mobileme').__version__,
    url='https://github.com/zyegfryed/django-mobileme',
    license='BSD',
    description=u'Detect mobile browsers and serve different template flavours to them.',
    long_description=long_description,
    author='Sébastien Fievet',
    author_email='zyegfryed@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    zip_safe=False,
)
