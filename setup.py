from distutils.core import setup
from setuptools import find_packages

setup(
    name='ddfeedback',
    packages=find_packages(exclude=['test', '*.test', '*.test.*']),
    version='0.1',
    description='Smart feedback for code quizzes',
    author='konstantin.charkin',
    author_email='93kostya@gmail.com',
    url='https://github.com/StepicOrg/data-driven-feedback',
    keywords=['data-driven feedback'],
    scripts=['bin/ddfeedback'],
)
