from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.model.models import Axiom, Curie
from rdflib import Literal, BNode
import os

owl_ontology = os.path.join(os.path.dirname(__file__), 'resources/owl-ontology.ttl')


class TestOWLUtils():

    def setup(self):
        curie_map = {
            'X': 'http://x.org/X_',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'oboInOwl': 'http://www.geneontology.org/formats/oboInOwl#',
            'BFO': 'http://purl.obolibrary.org/obo/BFO_',
            'RO': 'http://purl.obolibrary.org/obo/RO_',
            'PATO': 'http://purl.obolibrary.org/obo/PATO_',
            'UBERON': 'http://purl.obolibrary.org/obo/UBERON_',
            'IAO': 'http://purl.obolibrary.org/obo/IAO_'
        }
        curie_util = CurieUtil(curie_map)
        graph = RDFGraph(curie_util)
        graph.parse(owl_ontology, format='ttl')
        self.graph = graph
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
                Curie('oboInOwl:hasSynonymType'): [Curie('X:layperson')]
            }
        )
        results = self.owl_util.get_axioms(source, property, target)
        assert len(results) == 1
        assert results[0] == expected

    def test_get_synonyms(self):
        curie = Curie('X:foo')
        synonym_types = [
            'X:hasExactSynonym',
            'X:hasNarrowSynonym'
        ]
        expected = {
            'X:hasExactSynonym': {Literal('bar'), Literal('baz')},
            'X:hasNarrowSynonym': [Literal('qux')]
        }
        results = self.owl_util.get_synonyms(curie, synonym_types)
        # Convert list to set since order is not guaranteed
        results['X:hasExactSynonym'] = set(results['X:hasExactSynonym'])
        assert results == expected

    def test_get_definition(self):
        curie = Curie('X:foo')
        expected = "definition for foo"
        results = self.owl_util.get_definition(curie)
        assert results == expected


    def test_process_some_values_from(self):
        self.owl_util.process_some_values_from()
        subject = Curie('X:foo')
        eq = Curie('owl:equivalentClass')
        bnode = self.graph.get_objects(subject, eq)
        bnodes = list(bnode)
        assert len(bnodes) == 1
        predicate = Curie('BFO:0000051')
        results = self.graph.get_objects(BNode(bnodes[0]), predicate)
        assert len(list(results)) == 4
