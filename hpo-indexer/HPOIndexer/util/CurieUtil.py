from typing import List, Dict, Optional, Union, Tuple
from HPOIndexer.model.models import Curie
import re


class CurieUtil():
    """
    Utility for converting IRIs to Curies

    Advocate for not making this an interface and
    subsequent implementation, for simplicity
    only one should exist
    """

    def __init__(self, curie_map: Dict):
        if curie_map is not None:
            self.curie_map = curie_map
        else:
            # default map
            self.curie_map = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                'owl': 'http://www.w3.org/2002/07/owl#'
            }

    def curie_to_iri(self, curie: Curie) -> str:
        parts = curie.id.split(":")
        prefix = ""
        suffix = ""
        if len(parts) != 2:
            raise ValueError("Misformatted curie: {}".format(curie))
        else:
            prefix, suffix = parts

        return self.curie_map[prefix] + suffix

    def iri_to_curie(self, iri: str, namespace: Optional[str] = None) -> Curie:
        reference = ""
        curie = ""
        if namespace is not None:
            try:
                reference = self.curie_map[namespace]
            except KeyError as e:
                raise "Key not found in curie map: {}".format(namespace)
            curie = Curie(iri.replace(reference, namespace + ":"))
        else:
            '''
            Ideally need something like
            https://github.com/prefixcommons/curie-util/blob/master/
            src/main/java/org/prefixcommons/trie/Trie.java

            In the meantime, this hack should work for some obo ontologies
            '''
            parts = re.split(r'_|#', iri, 1)
            if len(parts) != 2:
                raise ValueError("Cannot resolve iri to curie: {}".format(iri))
            else:
                reference = parts[0]
                suffix = parts[1]
                namespace = [k for k, v in self.curie_map.items()
                             if v[:-1] == reference]
                if len(namespace) != 1:
                    raise KeyError("Cannot resolve iri"
                                   " to curie: {}".format(iri))
                curie = Curie("{}:{}".format(namespace[0], suffix))

        return curie