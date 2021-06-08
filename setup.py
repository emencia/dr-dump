# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='dr-dump',
    version=__import__('drdump').__version__,
    description=__import__('drdump').__doc__,
    long_description=open('README.rst').read(),
    long_description_content_type="text/x-rst",
    author='David Thenon',
    author_email='dthenon@emencia.com',
    url='https://github.com/emencia/dr-dump',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        "django>=1.9",
    ],
    include_package_data=True,
    zip_safe=False
)
