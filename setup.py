from setuptools import setup, find_packages

setup(
    name='sentinelimage',
    version='0.19',
    packages=find_packages(),
    install_requires=[
        'earthengine-api>=0.1.326',
        'geetools>=0.6.14,<0.7'
        ]
)