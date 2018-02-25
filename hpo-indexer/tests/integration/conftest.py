# content of conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--solr", action="store",
                     default="http://localhost:8983/solr/test-core/",
                     help="path to solr core")

@pytest.fixture
def solr_core(request):
    return request.config.getoption("--solr")