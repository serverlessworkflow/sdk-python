from setuptools import find_packages, setup
setup(
    name='serverlessworkflow_sdk',
    packages=find_packages(include=['serverlessworkflow_sdk']),
    version='0.1.0',
    description='Serverless Workflow Specification - Python SDK',
    author='Serverless Workflow Contributors',
    license='http://www.apache.org/licenses/LICENSE-2.0.txt',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)