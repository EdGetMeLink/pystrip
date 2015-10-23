from setuptools import setup, find_packages
from os.path import join, dirname

VERSION = '0.0.1'

setup(
    author='Mike Deltgen',
    author_email='mike@deltgen.net',
    name='halloween',
    version=VERSION,
    description='Halloween Pi Software',
    url='www.deltgen.net',
    include_package_data=True,
    license="Private",
    install_requires=[
        'Flask',
        'pyzmq',
    ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)
