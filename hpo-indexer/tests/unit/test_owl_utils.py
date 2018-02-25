from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.util.OWLUtil import OWLUtil

import os

synonym_ontology = os.path.join(os.path.dirname(__file__), 'resources/synonym-ontology.ttl')


class TestOWLUtils():

    def setup(self):
        curie_map = {
            'HP': 'http://purl.obolibrary.org/obo/HP_',
            'X': 'http://x.org/X_'
        }
        graph = RDFGraph(curie_map)
        self.owl_util = OWLUtil(graph)
        self.owl_util.graph.parse(synonym_ontology, format='ttl')

    def teardown(self):
        self.graph = None

