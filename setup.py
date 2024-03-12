# requirements will be loaded from requirements.txt

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ghostbuster',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points= {
        'console_scripts' : [
        'ghostbuster-admin-server=ghostbuster.admin_server:run',
        'ghostbuster-agent-server=ghostbuster.agent_server:run'
        ]

    },
    package_data={
        "": ["*.yml", "*.sql", 'ghostbuster/data', 'resources'],
    },
)