from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.SolrWorker import SolrWorker
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie
import os

hp_ontology = os.path.join(os.path.dirname(__file__), 'resources/hp-ontology.ttl')


class TestSolrWorker():

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
        fake_list = []
        curie_util = CurieUtil(curie_map)
        graph = RDFGraph(curie_util)
        graph.parse(hp_ontology, format='ttl')
        owl_util = OWLUtil(graph)
        # See integration  tests for light testing with real solr instance
        solr = 'http://fake-solr.org'
        self.solr_worker = SolrWorker(
            fake_list, graph, owl_util, curie_util, solr)

    def teardown(self):
        self.solr_worker = None

    def test_get_anatomy_adheres_in(self):
        phenotype = Curie('HP:0000046')
        results = self.solr_worker.get_anatomy_terms(phenotype)
        result = list(results)
        assert len(result) == 1
        assert str(result[0]) == "UBERON:0001300"

    def test_get_anatomy_adheres_in_part_of(self):
        phenotype = Curie('HP:0000047')
        results = self.solr_worker.get_anatomy_terms(phenotype)
        result = list(results)
        assert len(result) == 1
        assert str(result[0]) == "UBERON:0001301"

    def test_get_anatomy_different_rel(self):
        phenotype = Curie('HP:0000048')
        results = self.solr_worker.get_anatomy_terms(phenotype)
        result = list(results)
        assert len(result) == 0

    def test_is_syn_lay(self):
        term = Curie('HP:1')
        syn_type = 'oboInOwl:hasExactSynonym'
        syn = 'HP1'
        is_lay = self.solr_worker.is_synonym_lay(term, syn_type, syn)
        assert is_lay == True