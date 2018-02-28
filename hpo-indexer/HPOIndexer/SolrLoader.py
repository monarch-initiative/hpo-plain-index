from HPOIndexer.graph.Graph import Graph
from HPOIndexer.graph.RDFGraph import RDFGraph
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie
from HPOIndexer.SolrWorker import SolrWorker


from typing import List, Optional
import multiprocessing
from multiprocessing import Lock, Process
import argparse
import logging
import requests

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)


class SolrLoader():

    def __init__(self,
                 graph: Optional[Graph] = None,
                 owl_util: Optional[OWLUtil] = None
                 ):
        self.graph = graph
        self.owl_util = owl_util

    def main(self):
        parser = argparse.ArgumentParser(
            description='Generates a solr index of plain language '
                        'terms in the HPO and their grouping classes ',
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            '--solr', '-s', type=str, required=False,
            default="http://solr:8983/solr/hpo-pl/",
            help='Path to solr client')

        parser.add_argument(
            '--processes', '-p', type=str, required=False,
            default=multiprocessing.cpu_count(),
            help='Number of processes to spawn')

        args = parser.parse_args()

        # hardcoded curie map
        curie_map = SolrLoader.get_default_curie_map()
        curie_util = CurieUtil(curie_map)
        self.graph = RDFGraph(curie_util)
        self.owl_util = OWLUtil(self.graph)

        # Hardcode get HPO owl file and upheno uberon import
        logger.info("Loading HPO and uberon_import.owl")
        self.graph.parse('http://purl.obolibrary.org/obo/hp.owl',
                         format='xml')
        self.graph.parse('http://purl.obolibrary.org/obo/upheno/imports/uberon_import.owl',
                         format='xml')
        logger.info("Finished loading ontologies")

        logger.info("Getting phenotypes with lay person synonyms")
        terms_w_lay_syns = self.get_terms_with_lay_syns()

        lock = Lock()
        procs = [] # use a pool?

        logger.info("Processing terms with lay "
                    "person synoynm(s)".format(len(terms_w_lay_syns)))

        # Split into chunks depending on args.processes
        for chunk in [terms_w_lay_syns[i::args.processes]
                      for i in range(args.processes)]:
            solr_worker = SolrWorker(chunk,
                                     self.graph,
                                     self.owl_util,
                                     curie_util,
                                     args.solr,
                                     lock
                                     )
            proc = Process(target=solr_worker.run)
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()

        logger.info("Finished processing terms with lay person synoynm(s)")

        logger.info("Optimizing solr")
        self._optimize_solr(args.solr)
        logger.info("Solr optimized")


    def get_terms_with_lay_syns(
            self,
            root: Curie = Curie('HP:0000118'),
            lay_annotation: Curie = Curie(':layperson')) -> List[Curie]:

        terms_w_synonym = []
        subclass_of = Curie('rdfs:subClassOf')

        # Get descendant graph from root SolrWorker.get_synonyms
        all_phenotypes = self.graph.get_descendants(root, subclass_of)

        # Get axioms for phenotype and check for lay person annotation
        for term in all_phenotypes:
            axioms = self.owl_util.get_axioms(term.id)
            for axiom in axioms:
                has_lay = False
                for k,v in axiom.parts.items():
                    if k == Curie('oboInOwl:hasSynonymType') \
                            and lay_annotation in v:
                        terms_w_synonym.append(term.id)
                        has_lay = True
                        break
                if has_lay is True:
                    break

        return terms_w_synonym

    def _optimize_solr(self, solr: str) -> None:
        """
        optimize solr core
        """
        path = solr + 'update'
        params = {
            'optimize': 'true',
            'wt': 'json'
        }

        solr_req = requests.get(path, params=params)
        solr_response = solr_req.json()

        if solr_response['responseHeader']['status'] != 0:
            raise ValueError("Failed to optimize solr core, "
                             "response: {}".format(solr_response))


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
            'BFO': 'http://purl.obolibrary.org/obo/BFO_',
            'IAO': 'http://purl.obolibrary.org/obo/IAO_'
        }

if __name__ == "__main__":
    loader = SolrLoader()
    loader.main()
