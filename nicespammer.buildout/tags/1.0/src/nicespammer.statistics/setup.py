from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='nicespammer.statistics',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Riccardo Lemmi',
      author_email='riccardo@reflab.it',
      url='http://code.google.com/p/nicespammer/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['nicespammer'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Paste',
          'PasteDeploy',
          'PasteScript',
          'pysqlite',
      ],
      entry_points={
        'console_scripts': [
            "catcher = nicespammer.statistics.catcher:main",
            "nicespammer_db_setup = nicespammer.statistics.db_setup:main",
            ]
        },
      )
