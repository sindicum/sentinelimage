from setuptools import setup, find_packages

setup(
    name='sentinelimage',
    version='0.11',
    packages=find_packages(),
    install_requires=[
        'Fiona>=1.8.21',
        'geopandas>=0.11.1',
        'pyproj>=3.4.0',
        'rasterio>=1.3.2',
        'Shapely>=1.8.5',
        'Rtree>=1.0.1',
        'geetools>=0.6.14',
        'earthengine-api>=0.1.326',
        'geetools>=0.6.14'
        ]
)