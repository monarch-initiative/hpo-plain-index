from HPOIndexer.graph.Graph import Graph
from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie

from typing import List, Optional, Dict
from HPOIndexer.SolrWorker import SolrWorker
from multiprocessing import Lock
import argparse


class SolrLoader():

    def __init__(self,
                 graph: Optional[Graph] = None,
                 owl_util: Optional[OWLUtil] = None,
                 curie_util: Optional[CurieUtil] = None,
                 solr: Optional[str] = None):
        self.graph = graph
        self.owl_util = owl_util
        self.curie_util = curie_util
        self.solr = solr

    def main(self):
        parser = argparse.ArgumentParser(
            description='Generates a solr index of plain language '
                        'terms in the HPO and their grouping classes ',
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            '--solr', '-s', type=str, required=False,
            default="http://solr:8983/solr/hpo-pl/",
            help='Path to solr client')

        args = parser.parse_args()

        self.solr = args.solr
        # hardcoded curie map
        curie_map = SolrLoader.get_default_curie_map()
        curie_util = CurieUtil(curie_map)
        self.graph = RDFGraph(curie_util)
        owl_util = OWLUtil(self.graph)


    def get_terms_with_lay_syns(
            self,
            root: Curie = Curie('HP:0000118'),
            lay_annotation: Curie = Curie(':layperson')) -> List[Curie]:
        synonyms = [] # list of dicts from
        # Get descendant graph from root SolrWorker.get_synonyms
        all_phenotypes = self.graph.get_descendants(root)
        # Get synonyms for each term
        for term in all_phenotypes:
            pass
        # Filter those with annotation (lay person)



    @staticmethod
    def get_default_curie_map():
        return {
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
            'BFO': 'http://purl.obolibrary.org/obo/BFO_'
        }

if __name__ == "__main__":
    loader = SolrLoader()
    loader.main()
