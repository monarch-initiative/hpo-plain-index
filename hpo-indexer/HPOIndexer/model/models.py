from typing import List, NamedTuple, Optional
import json

class PLDoc(NamedTuple):
    """
    Named tuple for storing a solr document for HPO
    terms with plain language synonyms
    """
    id: str
    exact_synonym: Optional[List[str]] = None
    narrow_synonym: Optional[List[str]] = None
    broad_synonym: Optional[List[str]] = None
    related_synonym: Optional[List[str]] = None
    phenotype_closure: Optional[List[str]] = None
    phenotype_closure_label: Optional[List[str]] = None
    anatomy_closure: Optional[List[str]] = None
    anatomy_closure_label: Optional[List[str]] = None

    def _asjson(self, **kwargs) -> str:
        """
        Serialize tuple to a JSON formatted string

        :param kwargs: pass through to json.dumps()
        :return: JSON formatted string
        """
        return json.dumps(self._asdict(), **kwargs)

class Node(NamedTuple):
    id: str
    label: Optional[str] = None
