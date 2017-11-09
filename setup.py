from distutils.core import setup
from setuptools import find_packages

setup(
    name='amorph',
    packages=find_packages(exclude=['test', '*.test', '*.test.*']),
    version='0.1.3',
    description='Finds set of patches to transform one code into another',
    author='konstantin.charkin <93kostya@gmail.com>, Nikita Lapkov <nikita.lapkov@stepik.org>',
    url='https://github.com/StepicOrg/amorph',
    install_requires=['schema', 'requests', 'asttokens'],
    keywords=['transform', 'refactor', 'restructure', 'code'],
)
