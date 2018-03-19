from HPOIndexer.model.models import PLDoc
import os
import json

TESTDATA = os.path.join(os.path.dirname(__file__), 'resources/testDoc.json')


def test_json_encode():
    """
    Test that using a NamedTuple and
    json.dumps(NamedTuple._asdict()) encodes
    the expected json object
    """
    reference_doc = json.load(open(TESTDATA))
    test_doc = PLDoc(
        id='HP:0000464',
        exact_synonym=['Abnormality of the neck'],
        label='Abnormality of the neck',
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

    test_json = test_doc._asjson(sort_keys=True)
    assert test_json == json.dumps(reference_doc, sort_keys=True)
