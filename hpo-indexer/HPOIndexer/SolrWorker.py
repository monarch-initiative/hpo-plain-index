from HPOIndexer.graph.Graph import Graph
from HPOIndexer.util.OWLUtil import OWLUtil
from HPOIndexer.util.CurieUtil import CurieUtil
from HPOIndexer.model.models import Curie, PLDoc
from typing import List, Optional, Iterator, Iterable
from rdflib import Literal
from multiprocessing import Lock
import requests
import logging
import json

logger = logging.getLogger(__name__)


class SolrWorker():

    BATCH_SIZE = 1000

    PART_OF = Curie('BFO:0000050')
    SUBCLASS_OF = Curie('rdfs:subClassOf')
    PHENO_ROOT = Curie('HP:0000118')
    UBER_ROOT = Curie('UBERON:0001062')

    SYNONYMS = [
        'oboInOwl:hasExactSynonym',
        'oboInOwl:hasRelatedSynonym',
        'oboInOwl:hasNarrowSynonym',
        'oboInOwl:hasBroadSynonym'
    ]

    def __init__(self,
                 curie_list: Iterable[Curie],
                 graph: Graph,
                 owl_util: OWLUtil,
                 curie_util: CurieUtil,
                 solr: str,
                 lock: Optional[Lock] = None):
        self.curie_list = curie_list
        self.graph = graph
        self.owl_util = owl_util
        self.curie_util = curie_util
        self.solr = solr
        self.lock = lock # multiprocessing not implemented

    def run(self) -> None:
        logger.info("Thread processing {} HPO terms with"
                    " plain language synonyms".format(len(self.curie_list)))

        terms_processed = 0
        solr_doc_list = []

        for term in self.curie_list:
            if terms_processed % SolrWorker.BATCH_SIZE == 0 \
                    and terms_processed != 0:
                self.insert_into_solr(self.solr, solr_doc_list)
                logger.info("Inserted {} HPO terms with terms_processed".format(terms_processed))
                solr_doc_list = 0

            curie_id = term.id
            exact_synonym = None
            narrow_synonym = None
            broad_synonym = None
            related_synonym = None

            # Get plain language/lay person synonyms
            syn_dict = self.owl_util.get_synonyms(term, SolrWorker.SYNONYMS)

            for typ, syn_list in syn_dict.items():
                lay_synonyms = [syn for syn in syn_list
                                if self.is_synonym_lay(term, typ, syn)]
                if typ == 'oboInOwl:hasExactSynonym':
                    exact_synonym = lay_synonyms
                elif typ == 'oboInOwl:hasRelatedSynonym':
                    related_synonym = lay_synonyms
                elif typ == 'oboInOwl:hasNarrowSynonym':
                    narrow_synonym = lay_synonyms
                elif typ == 'oboInOwl:hasBroadSynonym':
                    related_synonym = lay_synonyms

            # Get phenotype closure
            phenotype_closure = []
            phenotype_closure_label = []
            for node in self.graph.get_closure(term,
                                               SolrWorker.SUBCLASS_OF,
                                               SolrWorker.PHENO_ROOT):
                phenotype_closure.append(node.id)
                phenotype_closure_label.append(node.label)

            # Get anatomy closure
            anatomy_closure = []
            anatomy_closure_label = []
            for anatomy in self.get_anatomy_terms(term):
                for node in self.graph.get_closure(anatomy,
                                                   SolrWorker.PART_OF,
                                                   SolrWorker.UBER_ROOT):
                    anatomy_closure.append(node.id)
                    anatomy_closure_label.append(node.label)

            doc = PLDoc(
                id=curie_id,
                exact_synonym=exact_synonym,
                related_synonym=related_synonym,
                narrow_synonym=narrow_synonym,
                broad_synonym=broad_synonym,
                phenotype_closure=phenotype_closure,
                phenotype_closure_label=phenotype_closure_label,
                anatomy_closure=anatomy_closure,
                anatomy_closure_label=anatomy_closure_label
            )
            solr_doc_list.append(json.loads(doc._asjson()))
            terms_processed += 1

        if len(solr_doc_list) > 0:
            self.insert_into_solr(self.solr, solr_doc_list)

        logger.info("Thread finished loading {} terms into solr".format(terms_processed))

    def insert_into_solr(self, solr: str, docs: List) -> None:
        """
        Insert doc list into solr core
        """
        path = solr + 'update'
        params = {
            'commit': 'true'
        }
        headers = {
            'Content-type': 'application/json'
        }

        if self.lock is not None:
            self.lock.acquire()
            try:
                solr_req = requests.post(path, params=params, data=json.dumps(docs), headers=headers)
                solr_response = solr_req.json()
            finally:
                self.lock.release()
        else:
            solr_req = requests.post(path, params=params, data=json.dumps(docs), headers=headers)
            solr_response = solr_req.json()

        if solr_response['responseHeader']['status'] != 0:
            raise ValueError("Failed to insert solr docs")

    def is_synonym_lay(self,
                       term: Curie,
                       typ: str,
                       synonym: str,
                       lay_annotation: Curie = Curie(':layperson')) -> bool:
        is_lay = False
        axioms = self.owl_util.get_axioms(term, Curie(typ), Literal(synonym))
        for axiom in axioms:
            for k, v in axiom.parts.items():
                if k == Curie('oboInOwl:hasSynonymType') \
                        and lay_annotation in v:
                    is_lay = True
        return is_lay


    def get_anatomy_terms(self, phenotype: Curie) -> Iterator[Curie]:
        """
        Note this is dependent on a specific curie map
        :param phenotype: list of phenotypes
        :return: Iterator return anatomy curies
        """
        anatomy_terms = []
        query = \
        """
            SELECT ?anatomy
            WHERE {{
                VALUES ?relation {{ RO:0000052 RO:0002314 }} 
                {0}  owl:equivalentClass [ a owl:Restriction ;
                    owl:onProperty BFO:0000051 ;
                    owl:someValuesFrom [ a owl:Class ;
                        owl:intersectionOf ( ?quality [ a owl:Restriction ;
                            owl:onProperty ?relation ;
                            owl:someValuesFrom ?anatomy ] [ a owl:Restriction ;
                            owl:onProperty RO:0002573 ;
                            owl:someValuesFrom PATO:0000460 ] ) ] ] .
            }}
        """.format(phenotype.id)

        query_result = self.graph.query(query)
        for res in query_result:
            yield self.curie_util.iri_to_curie(res[0])

        return anatomy_terms
