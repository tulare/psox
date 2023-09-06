# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup

def readme() :
    with open('README.md') as f :
        return f.read()

def license() :
    with open('LICENSE') as f:
        return f.read()

# Get version without import module
with open('src/psox/version.py') as f :
    exec(compile(f.read(), 'psox/version.py', 'exec'))

setup(
    name='psox',
    version=__version__,
    description='Encapsulation process sox.exe',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Topic :: Sound Processing :: Audio',
    ],
    keywords='sox audio sound',
    url='https://github.com/tulare/psox',
    author='Tulare Regnus',
    author_email='tulare.paxgalactica@gmail.com',
    license=license(),
    package_dir={'psox' : str('src/psox')},
    packages=['psox'],
    package_data={'psox' : ['*.dll']},
    include_package_data=True,
    install_requires=[
    ],
    scripts=['bin/embed_sox.cmd'],
    entry_points={
        'console_scripts' : ['psoxdemo=psox.__main__:main'],
    },
    data_files=[
        ('scripts', ['bin/libmad.dll', 'bin/libmp3lame.dll'])
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)
          
