import os
import sys
sys.path.append(os.path.dirname(__file__))
from paver.easy import sh, task, needs, consume_args
from profilehooks import timecall

@task
@timecall
def test_dags():
    """Execute Python test suite and generate a code coverage report
    """
    sh('python -m pytest --junitxml=/tmp/tests.xml --cov=dag --cov=util --cov-report xml:/tmp/coverage.xml --cov-report term-missing:skip-covered -v test/')

@task
def airflow():
    sh('./entrypoint.sh webserver')
