from setuptools import setup, find_packages

setup(
    name='hackintosh',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click','beautifulsoup4', 'requests'
    ],
    entry_points='''
        [console_scripts]
        yekki=hackintosh.main:cli
    ''',
)