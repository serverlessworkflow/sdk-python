from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name='serverlessworkflow.sdk',
    packages=find_packages(include=['serverlessworkflow', 'serverlessworkflow.sdk']),
    version='0.1.0',
    description='Serverless Workflow Specification - Python SDK',
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://serverlessworkflow.io/",
    author='Serverless Workflow Contributors',
    license='http://www.apache.org/licenses/LICENSE-2.0.txt',
    install_requires=['pyyaml==6.0', "jsonschema==4.4.0", "requests"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',

)
