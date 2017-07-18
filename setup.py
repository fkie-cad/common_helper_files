from setuptools import setup, find_packages
from common_helper_files import __version__

setup(
    name="common_helper_files",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'hurry.filesize'
    ],
    description="file operation helper functions",
    author="Fraunhofer FKIE",
    author_email="peter.weidenbach@fkie.fraunhofer.de",
    url="http://www.fkie.fraunhofer.de",
    license="GPL-3.0"
)
