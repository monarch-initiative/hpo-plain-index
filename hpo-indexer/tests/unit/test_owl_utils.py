from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.model.models import Axiom, Curie
from rdflib import Literal, XSD
import os

owl_ontology = os.path.join(os.path.dirname(__file__), 'resources/owl-ontology.ttl')


class TestOWLUtils():

    def setup(self):
        curie_map = {
            'X': 'http://x.org/X_',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'oboInOwl': 'http://www.geneontology.org/formats/oboInOwl#'
        }
        curie_util = CurieUtil(curie_map)
        graph = RDFGraph(curie_util)
        graph.parse(owl_ontology, format='ttl')
        self.owl_util = OWLUtil(graph)

    def teardown(self):
        self.graph = None

    def test_get_axioms_1(self):
        source = Curie('X:foo')
        property = Curie('X:hasExactSynonym')
        target = Literal('bar')
        expected = Axiom(
            id=Curie('X:synonymAxiom'),
            source=source,
            property=property,
            target=target,
            parts={
                Curie('rdf:type'): [Curie('owl:Axiom')],
                Curie('oboInOwl:hasSynonymType'): [Curie('X:layperson')],
            }
        )
        results = self.owl_util.get_axioms(source, property, target)
        assert len(results) == 1
        assert results[0] == expected

