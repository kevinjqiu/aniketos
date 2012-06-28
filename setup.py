from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='aniketos',
      version=version,
      description="Git server hook",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Kevn Jing Qiu',
      author_email='kevin.jing.qiu@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
      include_package_data=True,
      zip_safe=False,
      install_requires=open('requirements.txt').readlines(),
      entry_points={
          'console_scripts':[
              'update=aniketos.cli:update',
              'install-hook=aniketos.cli:install'
              ]
          }
      )
