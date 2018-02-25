from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.SolrWorker import SolrWorker
from HPOIndexer.util.OWLUtil import OWLUtil
import os

synonym_ontology = os.path.join(os.path.dirname(__file__), 'resources/synonym-ontology.ttl')


class TestSolrWorker():

    def setup(self):
        curie_map = {
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'X': 'http://x.org/X_'
        }
        graph = RDFGraph(curie_map)
        graph.parse(synonym_ontology, format='ttl')
        owl_util = OWLUtil(graph)
        # See integration  tests for light testing with real solr instance
        solr = 'http://fake-solr.org'
        self.solr_worker = SolrWorker(graph, owl_util, solr)

    def teardown(self):
        self.solr_worker = None

    def test_get_synonyms(self):
        curie = 'X:foo'
        synonym_types = [
            'X:hasExactSynonym',
            'X:hasNarrowSynonym'
        ]
        expected = {
            'X:hasExactSynonym': {'bar', 'baz'},
            'X:hasNarrowSynonym': ['qux']
        }
        results = self.solr_worker.get_synonyms(curie, synonym_types)
        # Convert list to set since order is not guaranteed
        results['X:hasExactSynonym'] = set(results['X:hasExactSynonym'])
        assert results == expected
