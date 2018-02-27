from HPOIndexer.graph.Graph import Graph
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.model.models import Curie
from typing import List, Optional, Dict
from multiprocessing import Lock


class SolrWorker():

    def __init__(self, graph:Graph,
                 owl_util: OWLUtil,
                 solr: str,
                 lock: Optional[Lock] = None):
        self.graph = graph
        self.owl_util = owl_util
        self.solr = solr
        self.lock = lock # multiprocessing not implemented

    def get_synonyms(self,
                     curie: Curie,
                     synonym_types: List[str]) -> Dict[str, List[str]]:
        """
        :param curie: curie formatted id
        :param synonym_types: Optional list of synonym predicates
        :return: Returns a dict with the structure:
        {
            "X:someType": ["foo","bar"],
            "X:someOtherType": ["baz"]
        }
        """
        synonym_object = {}

        for synonym_type in synonym_types:
            synonym_object[synonym_type] = \
                [str(synonym)
                 for synonym in self.graph.get_objects(curie, Curie(synonym_type))]

        return synonym_object

    def run(self):
        pass
