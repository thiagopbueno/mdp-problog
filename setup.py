import mdpproblog

from setuptools import setup
import os

def read(filename):
	return open(os.path.join(os.path.dirname(__file__), filename), 'r').read()

setup(
	name = 'mdpproblog',
	version = mdpproblog.__version__,
	author = 'Thiago P. Bueno',
	author_email = 'thiago.pbueno@gmail.com',
	description = 'A probabilistic logic programming framework '
					'to represent and solve MDPs.',
	long_description = read('README.rst'),
	license = 'GNU General Public License v3.0',
	keywords = ['planning', 'mdp', 'problog', 'probabilistic logic programming'],
	url = 'https://github.com/thiagopbueno/mdp-problog',
	packages = ['mdpproblog', 'tests'],
	scripts = ['bin/mdp-problog'],
	install_requires = ['problog'],
	include_package_data = True,
	zip_safe=False,
	classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
)
