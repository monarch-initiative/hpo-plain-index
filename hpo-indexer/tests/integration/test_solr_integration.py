import json
import requests
import os
from HPOIndexer.model.models import PLDoc


TESTDATA = os.path.join(os.path.dirname(__file__), 'resources/testDoc.json')


def test_ping(solr_core):
    """
    Tests if solr core is up and responding to requests
    """
    path = solr_core + 'admin/ping'
    params = {
        'wt': 'json'
    }
    solr_req = requests.get(path, params)
    solr_response = solr_req.json()
    assert solr_response['status'] == "OK"


def test_insert(solr_core):
    """
    Test insert of sample json doc
    """
    path = solr_core + 'update'
    params = {
        'commit': 'true'
    }
    headers = {
        'Content-type': 'application/json'
    }

    data = json.load(open(TESTDATA))
    solr_req = requests.post(path, params=params, data=json.dumps(data), headers=headers)
    solr_response = solr_req.json()

    assert solr_response['responseHeader']['status'] == 0


def test_filter_query(solr_core):
    """
    Test query
    """
    path = solr_core + "select"
    params = {
        'wt': 'json',
        'q': '*:*',
        'fq': 'id:"HP:0000464"',
        'fl': '*'
    }
    solr_req = requests.get(path, params)
    solr_response = solr_req.json()

    assert solr_response['response']['docs'][0]['id'] == 'HP:0000464'

def test_text_query(solr_core):
    """
    Test query
    """
    path = solr_core + "select"
    params = {
        'defType': 'edismax',
        'wt': 'json',
        'q': 'Abnormality of',
        'qf': 'exact_synonym_std^1',
        'fl': '*'
    }
    solr_req = requests.get(path, params)
    solr_response = solr_req.json()

    assert solr_response['response']['docs'][0]['exact_synonym']\
           == ['Abnormality of the neck']


def test_insert_using_api(solr_core):
    """
    Test insert using PLDoc API (named tuple)
    """
    path = solr_core + 'update'
    params = {
        'commit': 'true'
    }
    headers = {
        'Content-type': 'application/json'
    }

    test_doc = PLDoc(
        id='HP:1234',
        exact_synonym=['Abnormality of the neck'],
        phenotype_closure=[
            'HP:0000464',
            'HP:0000152',
            'HP:0000118'
        ],
        phenotype_closure_label=[
            'Abnormality of the neck',
            'Abnormality of head or neck',
            'Phenotypic abnormality'
        ]
    )
    test_list = []
    test_list.append(json.loads(test_doc._asjson()))

    solr_req = requests.post(path, params=params, data=json.dumps(test_list), headers=headers)
    solr_response = solr_req.json()

    assert solr_response['responseHeader']['status'] == 0