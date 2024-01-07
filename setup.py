from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand
import sys
import unittest


class TestCommandCustom(TestCommand):
    user_options = [('unittest-args=', 'a', "Arguments to pass to unittest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.unittest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover('./tests/')
        runner = unittest.TextTestRunner()
        result = runner.run(test_suite)
        sys.exit(not result.wasSuccessful())


setup(
    name='back-tester',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'yahoo-fin>=0.8.9.1',
        'pandas>=2.1.4',
        'numpy>=1.26.3',
        'setuptools>=69.0.3'
    ],
    tests_require=[],  # No need for additional testing dependencies if using unittest
    cmdclass={'test': TestCommandCustom},
)
