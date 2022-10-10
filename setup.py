from setuptools import setup, find_packages

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name='sentinelimage',
    version='0.1',
    packages=find_packages(),
    install_requires=['earthengine-api','geetools']
)