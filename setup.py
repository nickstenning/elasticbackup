from setuptools import setup, find_packages

setup(
    name = 'elasticbackup',
    version = '0.0.2',
    packages = find_packages(),

    # metadata for upload to PyPI
    author = 'Nick Stenning',
    author_email = 'nick@whiteink.com',
    url = 'https://github.com/nickstenning/elasticbackup',
    description = 'elasticbackup: tools to backup and restore ElasticSearch indices',
    license = 'MIT',
    keywords = 'sysadmin elasticsearch backup restore',

    install_requires = [
        'requests==0.13.3',
    ],

    entry_points = {
        'console_scripts': [
            'elasticbackup = elasticbackup.backup:main',
            'elasticrestore = elasticbackup.restore:main'
        ]
    }
)
