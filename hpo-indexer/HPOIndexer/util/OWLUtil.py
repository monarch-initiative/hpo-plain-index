from HPOIndexer.graph.Graph import Graph
from HPOIndexer.model.models import Axiom, Curie
from typing import List, Union, Dict, Iterable, Optional
from rdflib.term import Literal
import logging

logger = logging.getLogger(__name__)


class OWLUtil():
    """
    Utility for interacting with OWL graphs
    """
    ANNOTATED_SOURCE = 'owl:annotatedSource'
    ANNOTATED_PROPERTY = 'owl:annotatedProperty'
    ANNOTATED_TARGET = 'owl:annotatedTarget'
    DEFINITION = Curie('IAO:0000115')

    def __init__(self, graph: Graph):
        self.graph = graph

    def get_axioms(self,
                   source: Curie = None,
                   property: Curie = None,
                   target: Union[Curie, Literal] = None
                   ) -> List[Axiom]:
        """
        Returns a list of owl axioms given one or more
        owl:annotatedSource, owl:annotatedProperty,
        owl:annotatedTarget

        In the current implementation we do not check that
        the axiom is of rdf:type owl:Axiom

        :param source: Optional[URIRef], predicate of triple
                       X:someAxiom owl:annotatedSource X:source
        :param property: Optional[URIRef], predicate of triple
                         X:someAxiom owl:annotatedProperty X:source
        :param target: Optional[Union[URIRef,Literal]], predicate of triple
                       X:someAxiom owl:annotatedTarget X:source
        :return: List of Axioms
        """
        if source is None and target is None and property is None:
            raise ValueError("Method requires either source, "
                             "target, or property")

        arg_len = sum([1 for arg in [source,target,property]
                       if arg is not None])

        # Get the intersection of axioms
        axiom_dict = {}
        axiom_curie_list = []
        axioms = []

        source_predicate = Curie(OWLUtil.ANNOTATED_SOURCE)
        property_predicate = Curie(OWLUtil.ANNOTATED_PROPERTY)
        target_predicate = Curie(OWLUtil.ANNOTATED_TARGET)

        if source is not None:
            for src in self.graph.get_subjects(source, source_predicate):
                if src in axiom_dict:
                    axiom_dict[src] += 1
                else:
                    axiom_dict[src] = 1
        if target is not None:
            for targ in self.graph.get_subjects(target, target_predicate):
                if targ in axiom_dict:
                    axiom_dict[targ] += 1
                else:
                    axiom_dict[targ] = 1
        if property is not None:
            for prop in self.graph.get_subjects(property, property_predicate):
                if prop in axiom_dict:
                    axiom_dict[prop] += 1
                else:
                    axiom_dict[prop] = 1

        # Get the intersection of axioms given the input args
        for axiom_iri, intsect in axiom_dict.items():
            if intsect == arg_len:
                axiom_curie_list.append(axiom_iri)

        # For each axiom, get list of predicate object pairs (as a Tuple)
        for axiom_curie in axiom_curie_list:
            pred_object = {}
            pred_object[source_predicate] = [None]
            pred_object[property_predicate] = [None]
            pred_object[target_predicate] = [None]

            for predicate, obj in self.graph.get_predicate_objects(axiom_curie):
                if predicate in pred_object:
                    pred_object[predicate].append(obj)
                else:
                    pred_object[predicate] = [obj]

            source = pred_object[source_predicate][1]
            target = pred_object[target_predicate][1]
            property = pred_object[property_predicate][1]
            pred_object.pop(source_predicate, None)
            pred_object.pop(target_predicate, None)
            pred_object.pop(property_predicate, None)

            axiom = Axiom(
                id=axiom_curie,
                source=source,
                target=target,
                property=property,
                parts=pred_object
            )
            axioms.append(axiom)

        return axioms

    def get_synonyms(self,
                     curie: Curie,
                     synonym_types: Iterable[str]) -> Dict[str, List[str]]:
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
                [synonym
                 for synonym in self.graph.get_objects(curie, Curie(synonym_type))]

        return synonym_object

    def get_definition(self, curie: Curie) -> Optional[str]:
        """
        :param curie: curie formatted id
        :return: definition, returns first if multiple
        """
        def_list = [definition
                    for definition in self.graph.get_objects(curie, OWLUtil.DEFINITION)]

        if len(def_list) > 1:
            logger.warning("More than one definition for {}, using first".format(curie))

        return def_list[0].value if len(def_list) > 0 else None

    def process_some_values_from(self) -> None:
        """
        Based on Scigraphs processSomeValuesFrom,
        https://github.com/SciGraph/SciGraph/blob/96e098b/SciGraph-core/
        src/main/java/io/scigraph/owlapi/OwlPostprocessor.java#L71

        Creates inferred edges, from the pattern:
        ?restriction rdf:type owl:Restriction
        ?restriction owl:onProperty ?property
        ?restriction owl:someValuesFrom ?onClass

        infers:
        ?restriction ?property ?onClass

        :return: None
        """

        for restriction in self.graph.get_subjects(Curie('owl:Restriction'),
                                                   Curie('rdf:type')):
            on_property = Curie('owl:onProperty')
            some_values_from = Curie('owl:someValuesFrom')
            prop = self.graph.get_objects(restriction, on_property)
            cls = self.graph.get_objects(restriction, some_values_from)
            props = list(prop)
            classes = list(cls)
            target_class = classes[0]
            prop = props[0]

            if len(props) > 1:
                raise ValueError
            if len(classes) > 1:
                raise ValueError

            self.graph.add_triple(restriction, prop, target_class)

            # Process intersection paths:
            # owl:intersectionOf rdf:first ?class|restriction
            # owl:intersectionOf rdf:rest rdf:first ?class|restriction
            # owl:intersectionOf rdf:rest rdf:rest rdf:first ?class|restriction

            # Path to nils
            # Until owl:intersectionOf rdf:rest* rdf:nil

            # Create the triple:
            # ?restriction ?property (eg has_part) ?class/restriction

            property_chain = [Curie('owl:intersectionOf'), Curie('rdf:first')]
            nil_chain = [Curie('owl:intersectionOf'), Curie('rdf:rest')]
            continue2next_restriction = False

            for obj in self.graph.get_objects(target_class, property_chain):
                self.graph.add_triple(restriction, prop, obj)

            for obj in self.graph.get_objects(target_class, nil_chain):
                if obj == Curie('rdf:nil'):
                    continue2next_restriction = True

            if continue2next_restriction:
                continue

            max_iterations = 50
            iterations = 0
            break_while = False

            while iterations < max_iterations:
                property_chain[1:1] = [Curie('rdf:rest')]
                nil_chain.append(Curie('rdf:rest'))
                obj_iterator = self.graph.get_objects(target_class, property_chain)
                nil_iterator = self.graph.get_objects(target_class, nil_chain)
                obj_list = list(obj_iterator)
                nil_list = list(nil_iterator)

                if len(obj_list) == 0 and len(nil_list) == 0:
                    break

                else:
                    for obj in obj_list:
                        self.graph.add_triple(restriction, prop, obj)

                    for obj in nil_list:
                        if obj == Curie('rdf:nil'):
                            break_while = True

                if break_while:
                    break
                iterations += 1
