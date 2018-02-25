## hpo-indexer
Python module for generating a solr index of plain language terms in the HPO,
and their phenotype and anatomy facets.

Instructions are included for running this with docker-compose; however, this
can also be ran as a standalone python package.

#### Building and running with virtualenv
    virtualenv venv -p /usr/bin/python3.6
    source venv/bin/activate
    pip install -r requirements.txt

Run the integration tests:

    python -m pytest tests/integration/ --solr "http://localhost:8983/solr/test-core/"

Run the unit tests:

    python -m pytest tests/unit/