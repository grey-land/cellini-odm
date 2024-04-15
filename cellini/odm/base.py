from abc import ABC, abstractmethod
from pyoxigraph import NamedNode, Triple, Store, Literal
from typing import Generator, Union
from cellini.odm.utils import UnsupportedType

class AbstractNamedNode(ABC):
    """
    Main Abstract class refer to an RDF Named Node. 
    
    It is expected to be either the subject or the object of rdf triple(s) and never predicate. 
    """

    @classmethod
    def __rdf_title__(cls)->str:
        """__rdf_title__
        return the class identifier as string.
        """
        return f"{ registry.uri_prefix }{ cls.__name__ }"

    @property
    def __rdf_uri__(self)->NamedNode:
        """
        Returns the unique uri points to the class instance.

        This field is used as subject for all triples that describes a class instance.
        When we resolve it (using resolve_named_node above) should give back the instance.s 
        """
        if not hasattr(self, 'identifier'):
            raise NotImplementedError(f"AbstractNamedNode subclass should provide `identifier` property. {self.__class__} is missing `identifier`")
        return NamedNode(f"{ self.__rdf_title__() }:{ self.identifier }")


    @abstractmethod
    def to_triples(self, recursive=True)->Generator[Triple, None, None]:
        """to_triples
        serializes class instance to list of RDF triples    
        """


    @classmethod
    @abstractmethod
    def resolve_named_node(cls, node:NamedNode):
        """resolve_named_node
        given an rdf subject (usually a uri), resolve it and return
        the class instance.

        Reverse functionality of above `to_triples` function.
            
        Usually it will request the graph store, loads all triples 
        corresponding to the class instance, and use them to 
        "de-serialize" and get back the actual object.
        """


class RdfRegistry(set):

    """Registry
    
    A global registry holds list of AbstractNamedNode models.

    """
    def __init__(self, path=None, uri_prefix="cellini:"):
        self._store = Store(path)
        self._uri_prefix = uri_prefix

    @property
    def uri_prefix(self):
        return self._uri_prefix

    @property
    def triple_store(self):
        return self._store

    @property
    def query(self):
        return self.triple_store.query

    def set_triple_store(self, path:None):
        self._store = Store(path)

    def get_basemodel(self, title:str)->AbstractNamedNode:
        for basemodel in self:
            if basemodel.__rdf_title__() == title:
                return basemodel
        raise ValueError(f"Model '{title}' is not included in Registry")

    def uri_can_resolve(self, uri:Union[str, NamedNode])->bool:
        """Checks whether given uri points to a registered AbstractNamedNode.
        """
        if isinstance(uri, NamedNode) or isinstance(uri, Literal):
            uri = uri.value
        for basemodel in self:
            if uri.startswith(basemodel.__rdf_title__()):
                return True
        return False

    def uri_to_basemodel(self, uri:Union[str, NamedNode])->AbstractNamedNode:
        """Reverses the given uri and returns the corresponding AbstractNamedNode.
        """
        if isinstance(uri, NamedNode):
            uri = uri.value
        for basemodel in self:
            if uri.startswith(basemodel.__rdf_title__()):
                return basemodel

        raise ValueError(f'Model for {uri} is not included in Registry')

    def resolve_named_node(self, uri:NamedNode):
        """
        Loads triples for given rdf namednode and convert it 
        back to basemodel
        """
        basemodel = self.uri_to_basemodel(uri)
        return basemodel.resolve_named_node(uri)

    def add(self, obj:AbstractNamedNode):
        """
        Overwrite add method to allow only unique `AbstractNamedNode`s to
        be added to registry.  
        """
        if not issubclass(obj, AbstractNamedNode):
            raise UnsupportedType(f"Registry accepts only subclasses of `AbstractNamedNode`, but {obj} given")
        else:
            if obj not in self:
                super().add(obj)


registry = RdfRegistry()
