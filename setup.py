from setuptools import setup, find_packages

setup(
    name='dr-dump',
    version=__import__('drdump').__version__,
    description=__import__('drdump').__doc__,
    long_description=open('README.rst').read() + "\n" + open("CHANGELOG.rst").read(),
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
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[],
    include_package_data=True,
    zip_safe=False
)
