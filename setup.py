# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup

with open('LICENSE') as f:
    license = f.read()

# Get version without import module
with open('src/psox/version.py') as f :
    exec(compile(f.read(), 'psox/version.py', 'exec'))

setup(
    version=__version__,
    license=license,
    package_dir = {
        '' : str('src')
    },
)
          
