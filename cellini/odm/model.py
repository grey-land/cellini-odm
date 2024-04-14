"""
Functions related to conversion between pydantic models and rdf triples
"""
import uuid
from pydantic import Field, BaseModel, model_validator
from typing import Generator, Any
from pyoxigraph import *

from cellini.odm.utils    import literal_rdf_to_python, RDF, DCTERMS
from cellini.odm.registry import registry, python_value_to_triples
from cellini.odm.query    import Query


class UnresovableNode(Exception):
    pass


class RdfBaseModel(BaseModel):
    """

    ...
    
    During de-serialization from rdf triples to pydantic we convert triples literal values (str,
    int, date, ... ) directly and for complex objects we return the named-node type 
    (pyxoigraph.NamedNode) instead. Then when Pydantic builds the object reaches here
    that where we further resolve the next value. 

    """

    identifier:uuid.UUID = Field(default_factory=uuid.uuid4,
                                    predicate=DCTERMS.identifier.value,
                                    description="UUID identifier for any object")


    def __init_subclass__(cls, *args, **kwargs):
        """
        """
        if cls not in registry:
            registry.add(cls)
        cls.objects = Query(model_class=cls)

    @classmethod
    def __rdf_namespace__(cls)->str:
        return "https://cellini.io/ns/"

    @classmethod
    def __rdf_title_prefix__(cls)->str:
        return ""

    @classmethod
    def __rdf_title__(cls)->str:
        return f"{ cls.__rdf_title_prefix__() }{ cls.model_json_schema()['title'] }"
    
    @classmethod
    def __rdf_type__(cls) -> NamedNode:
        return NamedNode(f"{ cls.__rdf_namespace__() }{ cls.__rdf_title__() }")
    
    @classmethod
    def __rdf_types__(cls) -> Generator[NamedNode, None, None]:
        yield cls.__rdf_type__()

    @classmethod
    def __rdf_types__(cls) -> Generator[NamedNode, None, None]:
        for cl in cls.mro():
            if cl == RdfBaseModel:
                break
            yield cl.__rdf_type__()

    @model_validator(mode='before')
    @classmethod
    def resolve_named_nodes(cls, data: Any) -> Any:
        if isinstance(data, NamedNode):
            return registry.resolve_named_node(data)
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, NamedNode):
                    data[k] = registry.resolve_named_node(v)
        return data

    @classmethod
    def _get_predicate_from_field(cls, field_name:str)->NamedNode:
        """
        Returns predicate for given field name. 
        """
        predicate = None
        field_info = cls.model_fields[field_name]
        if field_info and field_info.json_schema_extra:
            predicate = field_info.json_schema_extra.get('predicate')
        if not predicate:
            predicate = NamedNode(f"{ cls.__rdf_namespace__() }{ field_name }")
        if isinstance(predicate, str):
            return NamedNode(predicate)
        if isinstance(predicate, NamedNode):
            return predicate
        raise ValueError(f"Unexpected field predicate type {type(predicate)} for field {cls.__rdf_title__()}.{field_name}")

    @classmethod
    def _get_field_name_from_predicate(cls, predicate:NamedNode)->Field:
        """
        Returns field for given predicate. 
        """
        for field_name in cls.model_fields.keys():
            if predicate in [ RDF.type ]:
                return None
            elif predicate == cls._get_predicate_from_field(field_name):
                return field_name
        raise ValueError(f'No field match given predicate {predicate}, for class {cls.__rdf_title__()}')

    @property
    def __rdf_uri__(self)->NamedNode:
        """
        Returns the uri of the model.

        This field is used as subject for all triples.
        """
        return NamedNode(f"cellini:{ self.__rdf_title__() }:{ self.identifier }")


    def to_triples(self, recursive=True)->Generator[Triple, None, None]:
        """ 
        Serialize model to list of triples
        """
        
        # every triple will use __rdf_uri__ as subject  
        subject = self.__rdf_uri__

        # First map current and parent classes to rdf:type triples
        for rdf_type in self.__rdf_types__():
            yield Triple(subject, RDF.type, rdf_type)

        # Loop through all pydantic fields 
        for field_name in self.model_fields.keys():

            # load actual field value
            python_value = getattr(self, field_name)

            # if value is empty, then we skip any triples
            if python_value == None:
                continue

            # load predicate from field.
            predicate = self._get_predicate_from_field( field_name )

            # convert python to triples
            for triple in python_value_to_triples(subject, predicate, python_value, recursive=recursive):
                yield triple


    @classmethod
    def resolve_named_node(cls, uri:NamedNode):
        data = dict()

        for s, p, o in registry.graph.query(f"DESCRIBE {uri}"):

            # get field from predicate 
            field_name = cls._get_field_name_from_predicate(p)
            
            if not field_name:
                continue
            
            # if o.value.startswith("cellini-type:Bag"):
            #     data[field_name] = Bag.resolve_named_node(o) 

            elif o.value.startswith("cellini"):
                data[field_name] = o

            else: 
                data[field_name] = literal_rdf_to_python(o)

        return cls(**data)


    def save(self, recursive=True):
        if self.__class__.objects.exists(self):
            self.__class__.objects.delete(self)
        self.__class__.objects.create(self, recursive=recursive)

    def delete(self):
        self.__class__.objects.delete(self)
