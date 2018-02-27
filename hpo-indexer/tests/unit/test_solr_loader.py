from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.SolrLoader import SolrLoader
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie
import os

hp_ontology = os.path.join(os.path.dirname(__file__), 'resources/hp-ontology.ttl')


class TestSolrLoader():

    def setup(self):
        curie_map = {
            '': 'http://purl.obolibrary.org/obo/hp.owl#',
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'obo': 'http://purl.obolibrary.org/obo/',
            'oboInOwl': 'http://www.geneontology.org/formats/oboInOwl#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'RO': 'http://purl.obolibrary.org/obo/RO_',
            'PATO': 'http://purl.obolibrary.org/obo/PATO_',
            'UBERON': 'http://purl.obolibrary.org/obo/UBERON_',
            'BFO': 'http://purl.obolibrary.org/obo/BFO_',
            'X': 'http://x.org/X_'
        }
        curie_util = CurieUtil(curie_map)
        graph = RDFGraph(curie_util)
        graph.parse(hp_ontology, format='ttl')
        owl_util = OWLUtil(graph)
        # See integration  tests for light testing with real solr instance
        solr = 'http://fake-solr.org'
        self.solr_loader = SolrLoader(graph, owl_util, curie_util, solr)

    def teardown(self):
        self.solr_loader = None

    def test_get_lay_syns(self):
        assert 1