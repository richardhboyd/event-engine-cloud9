from setuptools import setup, find_packages

setup(
    name='your_project_name',
    version='0.1',
    description='A description.',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    package_data={'': ['/home/ec2-user/environment/blueprint/module01/instance-resizer/template.yaml']},
    include_package_data=True,
    install_requires=['cfnresponse'],
)