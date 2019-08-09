# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


version = '0.3.0'
setup(

  name = 'nebulacli',

  version = version,
  py_modules=['nebulacli'],

  description = '',
  long_description=open('README.md').read(),
  long_description_content_type="text/markdown",
  python_requires='>=3',

  author = 'Robert Hafner',
  author_email = 'tedivm@tedivm.com',
  url = 'https://github.com/tedivm/nebula-cli',
  download_url = "https://github.com/tedivm/nebula-cli/archive/v%s.tar.gz" % (version),
  keywords = '',

  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',

    'Intended Audience :: Developers',

    'Programming Language :: Python :: 3',
    'Environment :: Console',
  ],

  install_requires=[
    'click>=5.0,<6.0',
    'requests>=2.18.0,<3',
  ],

  extras_require={
    'dev': [
      'twine',
      'wheel'
    ],
  },

  entry_points={
    'console_scripts': [
      'nebulacli=nebulacli:cli',
    ],
  },

)
