from HPOIndexer.graph.RDFGraph import RDFGraph
from rdflib.graph import URIRef, Literal
from HPOIndexer.model.models import Node
import os

synonym_ontology = os.path.join(os.path.dirname(__file__), 'resources/test-ontology.ttl')


class TestRDFGraph():

    def setup(self):
        curie_map = {
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'X': 'http://x.org/X_'
        }
        self.graph = RDFGraph(curie_map)
        self.graph.parse(synonym_ontology, format='ttl')

    def teardown(self):
        self.graph = None

    def test_get_closure(self):
        curie = 'X:finger'
        predicate = 'X:partOf'
        root = "X:torso"
        label_predicate = 'X:label'
        expected = {
            Node("X:finger", "finger"),
            Node("X:hand",   "hand"),
            Node("X:arm",    "arm"),
            Node("X:torso",  "torso"),
        }
        results = self.graph.get_closure(
            curie, predicate, root, label_predicate
        )
        results = set(results)
        assert results == expected

    def test_get_closure_no_rel(self):
        curie = 'X:finger'
        root = "X:torso"
        label_predicate = 'X:label'
        expected = {
            Node("X:finger", "finger"),
            Node("X:hand",   "hand"),
            Node("X:arm",    "arm"),
            Node("X:torso",  "torso"),
            Node("X:foot",   None),
        }
        results = self.graph.get_closure(
            node_id=curie, root=root, label=label_predicate
        )
        results = set(results)
        assert results == expected

    def test_get_closure_not_reflexive(self):
        curie = 'X:finger'
        root = "X:torso"
        label_predicate = 'X:label'
        expected = {
            Node("X:hand",   "hand"),
            Node("X:arm",    "arm"),
            Node("X:torso",  "torso"),
            Node("X:foot",   None),
        }
        results = self.graph.get_closure(
            node_id=curie, root=root, label=label_predicate, reflexive=False
        )
        results = set(results)
        assert results == expected

    def test_get_closure_no_root(self):
        curie = 'X:finger'
        predicate = 'X:partOf'
        label_predicate = 'X:label'
        expected = {
            Node("X:finger", "finger"),
            Node("X:hand",   "hand"),
            Node("X:arm",    "arm"),
            Node("X:torso",  "torso"),
            Node("X:body",   "body"),
        }
        results = self.graph.get_closure(
            node_id=curie, edge=predicate, label=label_predicate
        )
        results = set(results)
        assert results == expected

    def test_get_descendents(self):
        curie = 'X:torso'
        predicate = 'X:partOf'
        label_predicate = 'X:label'
        expected = {
            Node("X:finger", "finger"),
            Node("X:hand",   "hand"),
            Node("X:arm",    "arm")
        }

        results = self.graph.get_descendents(
            curie, predicate, label_predicate
        )

        results = set(results)
        assert results == expected

    def test_get_object_literals(self):
        curie = 'X:foo'
        predicate = 'X:hasExactSynonym'
        expected = {Literal("bar"), Literal("baz")}
        results = {obj for obj in self.graph.get_objects(curie, predicate)}
        assert results == expected

    def test_get_objects(self):
        curie = 'X:finger'
        predicate = 'X:partOf'
        expected = {URIRef('http://x.org/X_hand')}
        results = {obj for obj in self.graph.get_objects(curie, predicate)}
        assert results == expected

    def test_get_subjects(self):
        curie = 'X:hand'
        predicate = 'X:partOf'
        expected = {URIRef('http://x.org/X_finger')}
        results = {sub for sub in self.graph.get_subjects(curie, predicate)}
        assert results == expected

    def test_curie_to_iri(self):
        curie = 'HP:1234'
        iri = 'http://purl.obolibrary.org/obo/HP_1234'
        assert self.graph._curie_to_iri(curie) == iri

    def test_iri_to_curie(self):
        curie = 'HP:1234'
        iri = 'http://purl.obolibrary.org/obo/HP_1234'
        ns = 'HP'
        assert self.graph._iri_to_curie(iri, ns) == curie

    def test_iri_to_curie_no_ns(self):
        curie = 'HP:1234'
        iri = 'http://purl.obolibrary.org/obo/HP_1234'
        assert self.graph._iri_to_curie(iri) == curie
