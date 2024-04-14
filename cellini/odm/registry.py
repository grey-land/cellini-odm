import uuid
from typing             import Union, Optional, TYPE_CHECKING, Generator, Any
from pyoxigraph         import Store, NamedNode, Triple, Literal
from cellini.odm.utils  import literal_rdf_to_python, literal_python_to_rdf, UnsupportedType, RDF


class RdfRegistry(set):

    """Registry
    
    A global registry holds list of defined RdfBaseModel models.

    """
    def __init__(self, store=None):
        self._store = Store(store)

    @property
    def graph(self):
        return self._store

    def get_basemodel(self, title:str)->'RdfBaseModel':
        for basemodel in self:
            if basemodel.__rdf_title__() == title:
                return basemodel
        raise ValueError(f"Model '{title}' is not included in Registry")
    
    def uri_to_basemodel(self, uri:Union[str, NamedNode])->'RdfBaseModel':
        """Reverses the given uri and returns the corresponding RdfBaseModel.
        """
        if isinstance(uri, NamedNode):
            uri = uri.value
        
        assert len(uri.split(':')) == 3

        if uri.split(':')[0] in ['cellini', 'cellini-type']:
            for basemodel in self:
                if basemodel.__rdf_title__() == uri.split(':')[1]:
                    return basemodel

        raise ValueError(f'Model for {uri} is not included in Registry')

    def resolve_named_node(self, uri:NamedNode):
        """
        Loads triples for given rdf namednode and convert it 
        back to basemodel
        """
        
        basemodel = self.uri_to_basemodel(uri)
        return basemodel.resolve_named_node(uri)


registry = RdfRegistry()


def python_value_to_triples(subject:NamedNode, predicate:NamedNode, python_value:Any, recursive=True)->Generator[Triple, None, None]:
    # If the field value is a list then is wrapped as 
    # rdf:Bag implementation
    if type(python_value) is list:

        bag = Bag(python_value)
        
        # first we return the triple representing the field,
        # that points to Bag node.  
        yield Triple(subject, predicate, bag.node)
        
        # then we return Bag node's triples that contains
        # the actual list items.
        if recursive:
            for triple in bag.to_triples(recursive=recursive):
                yield triple

    # if the value class is included in registry
    # then it should be an RdfBaseModel model, 
    # so we use its autogenerated uri
    elif type(python_value) in registry:
        yield Triple(subject, predicate, python_value.__rdf_uri__)
        if recursive:
            for t in python_value.to_triples():
                yield t

    # otherwise the field is expected to point to 
    # literal value so we convert it. 
    else:
        value = literal_python_to_rdf(python_value)
        if value:
            yield Triple(subject, predicate, value)




class Bag(list):

    """
    Bag is a python List type that implements rdf:Bag specification.

    As long as rdf schema doesnt support Ordered Lists natively, 
    rdf:Bag class is used to fill this gap.

    [see](https://www.w3.org/2007/02/turtle/primer/#figure14)
    """

    def __init__(self, *arg, node:Optional[NamedNode]=None):
        if not isinstance(node, NamedNode):
            node = NamedNode(f"cellini-type:Bag:{uuid.uuid4()}")
        self.node = node
        super().__init__(*arg)

    @classmethod
    def __rdf_title__(cls):
        return cls.__name__

    def to_triples(self, recursive=True):
        yield Triple(self.node, RDF.type, RDF.Bag)
        i = 1
        for item in self:
            for triple in python_value_to_triples(
                            self.node, 
                            NamedNode(f"http://www.w3.org/1999/02/22-rdf-syntax-ns#_{i}"),
                            item,
                            recursive=recursive):
                yield triple
            i += 1

    @classmethod
    def resolve_named_node(cls, node:NamedNode):

        data = cls(node=node)

        for s, p, o in registry.graph.query(f"DESCRIBE {node}"):

            if p == RDF.type:
                if o != RDF.Bag:
                    raise ValueError(f"Expected RDF.Bag type but got {o}")
                continue
            
            idx = int(p.value.split('_')[1])
            if isinstance(o, Literal):
                value = literal_rdf_to_python(o)
            elif isinstance(o, NamedNode):
                value = registry.resolve_named_node(o)
            else:
                raise UnsupportedType(f"Unexpected triple type recieved {type(o)} (value={o})")            

            data.insert(idx, value)

        return data

registry.add(Bag)


if TYPE_CHECKING:
    from cellini.odm.model import RdfBaseModel 
