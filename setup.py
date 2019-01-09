from setuptools import setup, find_packages

VERSION = '0.2.1'

setup(
    name='common_helper_files',
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        'bitmath'
    ],
    description='file operation helper functions',
    author='Fraunhofer FKIE',
    author_email='peter.weidenbach@fkie.fraunhofer.de',
    url='http://www.fkie.fraunhofer.de',
    license='GPL-3.0'
)
