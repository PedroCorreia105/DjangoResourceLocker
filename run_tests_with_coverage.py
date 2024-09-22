#!/usr/bin/env python
import os
import sys
import coverage
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Start code coverage
    cov = coverage.Coverage()
    cov.start()

    # Run tests
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    # failures = test_runner.run_tests(["apps.users.tests.UsersAPITestCase.test_create_resource"])
    failures = test_runner.run_tests(["apps"])

    # Stop coverage
    cov.stop()
    cov.save()

    # Generate coverage report
    cov.report()
    cov.html_report(directory="htmlcov")
    cov.xml_report(outfile="coverage.xml")

    sys.exit(bool(failures))
