from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.util.CurieUtil import CurieUtil
from rdflib import Literal
from HPOIndexer.model.models import Node, Curie
import os

synonym_ontology = os.path.join(os.path.dirname(__file__), 'resources/test-ontology.ttl')


class TestRDFGraph():
    """
    TO DO tests on BNodes
    """

    def setup(self):
        curie_map = {
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'X': 'http://x.org/X_'
        }
        curie_util = CurieUtil(curie_map)
        self.graph = RDFGraph(curie_util)
        self.graph.parse(synonym_ontology, format='ttl')

    def teardown(self):
        self.graph = None

    def test_get_closure(self):
        curie = Curie('X:finger')
        predicate = Curie('X:partOf')
        root = Curie('X:torso')
        label_predicate = Curie('X:label')
        expected = {
            Node(Curie('X:finger'), 'finger'),
            Node(Curie('X:hand'),   'hand'),
            Node(Curie('X:arm'),    'arm'),
            Node(Curie('X:torso'),  'torso'),
        }
        results = self.graph.get_closure(
            curie, predicate, root, label_predicate
        )
        results = set(results)
        assert results == expected

    def test_get_closure_no_rel(self):
        curie = Curie('X:finger')
        root = Curie('X:torso')
        label_predicate = Curie('X:label')
        expected = {
            Node(Curie('X:finger'), 'finger'),
            Node(Curie('X:hand'),   'hand'),
            Node(Curie('X:arm'),    'arm'),
            Node(Curie('X:torso'),  'torso'),
            Node(Curie('X:foot'),    None),
        }
        results = self.graph.get_closure(
            node=curie, root=root, label_predicate=label_predicate
        )
        results = set(results)
        assert results == expected

    def test_get_closure_not_reflexive(self):
        curie = Curie('X:finger')
        root = Curie('X:torso')
        label_predicate = Curie('X:label')
        expected = {
            Node(Curie('X:hand'),   'hand'),
            Node(Curie('X:arm'),    'arm'),
            Node(Curie('X:torso'),  'torso'),
            Node(Curie('X:foot'),    None),
        }
        results = self.graph.get_closure(
            node=curie, root=root, label_predicate=label_predicate, reflexive=False
        )
        results = set(results)
        assert results == expected

    def test_get_closure_no_root(self):
        curie = Curie('X:finger')
        predicate = Curie('X:partOf')
        label_predicate = Curie('X:label')
        expected = {
            Node(Curie('X:finger'), 'finger'),
            Node(Curie('X:hand'),   'hand'),
            Node(Curie('X:arm'),    'arm'),
            Node(Curie('X:torso'),  'torso'),
            Node(Curie('X:body'),   'body'),
        }
        results = self.graph.get_closure(
            node=curie, edge=predicate, label_predicate=label_predicate
        )
        results = set(results)
        assert results == expected

    def test_get_descendants(self):
        curie = Curie('X:torso')
        predicate = Curie('X:partOf')
        label_predicate = Curie('X:label')
        expected = {
            Node(Curie('X:finger'), 'finger'),
            Node(Curie('X:hand'),   'hand'),
            Node(Curie('X:arm'),    'arm')
        }

        results = self.graph.get_descendants(
            curie, predicate, label_predicate
        )

        results = set(results)
        assert results == expected

    def test_get_object_literals(self):
        curie = Curie('X:foo')
        predicate = Curie('X:hasExactSynonym')
        expected = {Literal('bar'), Literal('baz')}
        results = {obj for obj in self.graph.get_objects(curie, predicate)}
        assert results == expected

    def test_get_objects(self):
        curie = Curie('X:finger')
        predicate = Curie('X:partOf')
        expected = {Curie('X:hand')}
        results = {obj for obj in self.graph.get_objects(curie, predicate)}
        assert results == expected

    def test_get_subjects(self):
        curie = Curie('X:hand')
        predicate = Curie('X:partOf')
        expected = {Curie('X:finger')}
        results = {sub for sub in self.graph.get_subjects(curie, predicate)}
        assert results == expected

    def test_get_subjects_literal(self):
        literal = Literal('hand')
        predicate = Curie('X:label')
        expected = {Curie('X:hand')}
        results = {sub for sub in self.graph.get_subjects(literal, predicate)}
        assert results == expected

    def test_get_predicate_object(self):
        curie = Curie('X:hand')
        expected = {(Curie('X:label'), Literal('hand')),
                    (Curie('X:partOf'), Curie('X:arm')),
        }

        results = {(pred, obj) for (pred, obj) in self.graph.get_predicate_objects(curie)}
        assert results == expected

