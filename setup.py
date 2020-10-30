import os
import sys
from setuptools import setup, find_packages, Extension

sys.path.insert(0, os.path.abspath('./src'))

from freeway import __version__

with open('README.rst', 'r') as desc:
    long_description = desc.read()

config = {
    'name': "freeway",
    'version': __version__,
    'license': 'MIT',
    'packages': ["freeway"],
    'description': "Freeway is a module for managing file system structures with recursive pattern rules.",
    'long_description': long_description,
    'long_description_content_type': "text/x-rst",
    'url': "https://github.com/cesioarg",
    'download_url': 'https://github.com/cesioarg/freeway/archive/%s.tar.gz' % __version__,
    'author': "Leandro Inocencio",
    'author_email': "cesio.arg@gmail.com",
    'keywords': ['filesystem', 'pipeline', 'parser', 'forder', 'patternvideos'],
    'package_dir': {'':'src'},
    'install_requires': [
        'cython',
    ],
    'classifiers': [
        "Development Status :: 3 - Alpha",
        "Natural Language :: Spanish",
        "Programming Language :: Python :: 3.7",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    'extras_require': {
        "dev": [
            "pytest>=3.7",
            ]
    }

}

if not sys.platform.startswith('linux'):
    from Cython.Build import cythonize

    extensions = [
        Extension("freeway", ["src/freeway/freeway.py"]),
        Extension("versioner", ["src/freeway/versioner.py"]),
        Extension("errors", ["src/freeway/errors.py"])
    ]
    config.update({'ext_modules': cythonize(extensions, build_dir="build")})

setup(**config)
