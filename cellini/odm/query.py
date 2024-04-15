

import uuid
from typing import Generator, Union, TYPE_CHECKING
from pyoxigraph import *

from cellini.odm.utils import literal_python_to_rdf, RDF, DCTERMS
from cellini.odm.base  import registry

class Query(object):

    def __init__(self, model_class:'RdfBaseModel') -> None:
        self.model_class = model_class

    @property
    def query(self):
        return registry.triple_store.query
    
    def create(self, obj:'RdfBaseModel', **kwargs):
        for s,p,o in obj.to_triples(**kwargs):
            registry.triple_store.add(Quad(s, p, o))
    
    def exists(self, obj:'RdfBaseModel')->bool:
        return self.query(f"ASK {{ ?s  { DCTERMS.identifier } { literal_python_to_rdf(obj.identifier) } }}")

    def delete(self, obj:'RdfBaseModel'):
        for s, p, o in self.query(f"DESCRIBE {obj.__rdf_uri__}"):
            registry.triple_store.remove(Quad(s, p, o))

    def filter(self, **kwargs)->Generator['RdfBaseModel', None, None]:
        filters = []
        
        for k, v in kwargs.items():
            predicate = self.model_class._get_predicate_from_field(k)    
            value = literal_python_to_rdf(v)
            filters.append(f"?s {predicate} {value}")
        
        filter_clause = f"FILTER EXISTS {{ {';'.join(filters)} }}"

        for q in self.query(f"""SELECT DISTINCT ?s WHERE {{
            ?s { RDF.type } { self.model_class.__rdf_type__() } .
            {filter_clause}
        }}"""):
            yield self.resolve(q['s'])

    def all(self)->Generator['RdfBaseModel', None, None]:
        return self.filter()

    def get(self, identifier:Union[str, uuid.UUID])->'RdfBaseModel':
        return registry.resolve_named_node(NamedNode(f"{ self.model_class.__rdf_title__() }:{ identifier }"))

    def resolve(self, uri:NamedNode)->'RdfBaseModel':
        return registry.resolve_named_node(uri)
 


if TYPE_CHECKING:
    from cellini.odm.model import RdfBaseModel 
