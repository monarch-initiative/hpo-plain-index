from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie


class TestCurieUtil():

    def setup(self):
        curie_map = {
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'owl': 'http://www.w3.org/2002/07/owl#'
        }
        self.curie_util = CurieUtil(curie_map)

    def teardown(self):
        self.graph = None

    def test_curie_to_iri(self):
        curie = Curie('HP:1234')
        iri = 'http://purl.obolibrary.org/obo/HP_1234'
        assert self.curie_util.curie_to_iri(curie) == iri

    def test_iri_to_curie(self):
        curie = Curie('HP:1234')
        iri = 'http://purl.obolibrary.org/obo/HP_1234'
        ns = 'HP'
        assert self.curie_util.iri_to_curie(iri, ns) == curie

    def test_iri_to_curie_no_ns(self):
        curie = Curie('HP:1234')
        iri = 'http://purl.obolibrary.org/obo/HP_1234'
        assert self.curie_util.iri_to_curie(iri) == curie

    def test_iri_to_curie_owl(self):
        curie = Curie('owl:1234')
        iri = 'http://www.w3.org/2002/07/owl#1234'
        assert self.curie_util.iri_to_curie(iri) == curie