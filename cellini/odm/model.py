"""
Functions related to conversion between pydantic models and rdf triples
"""
import uuid
from pydantic import Field, BaseModel, model_validator
from typing import Generator, Any
from pyoxigraph import *

from cellini.odm.utils import literal_rdf_to_python, RDF, DCTERMS
from cellini.odm.base  import AbstractNamedNode, registry
from cellini.odm.types import python_value_to_triples
from cellini.odm.query import Query


class UnresovableNode(Exception):
    pass


class RdfBaseModel(BaseModel, AbstractNamedNode):

    identifier:uuid.UUID = Field(default_factory=uuid.uuid4,
                                    predicate=DCTERMS.identifier.value,
                                    description="UUID identifier for any object")


    def __init_subclass__(cls, *args, **kwargs):
        """
        Helper function that runs when `RdfBaseModel` is subclassed and adds it
        in the registry (autoregistration).
        
        Then it adds a class property (objects) similar to SQLAlchemy to easily
        query the relevant subclass from rdf triple store.
        """
        registry.add(cls)
        cls.objects = Query(model_class=cls)

    @classmethod
    def __rdf_namespace__(cls)->str:
        return "https://cellini.io/ns/"

    @classmethod
    def __rdf_title__(cls)->str:
        return f"{ registry.uri_prefix }{ cls.model_json_schema()['title'] }"
    
    @classmethod
    def __rdf_type__(cls) -> NamedNode:
        return NamedNode(f"{ cls.__rdf_namespace__() }{ cls.model_json_schema()['title'] }")
    
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
        Returns field name for given predicate. 
        """
        for field_name in cls.model_fields.keys():
            if predicate in [ RDF.type ]:
                return None
            elif predicate == cls._get_predicate_from_field(field_name):
                return field_name
        raise ValueError(f'No field match given predicate {predicate}, for class {cls.__rdf_title__()}')

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

            # if value is empty, then we skip it and go to next field
            if python_value == None:
                continue

            # load predicate from field.
            predicate = self._get_predicate_from_field( field_name )

            # convert field's value to triples
            for triple in python_value_to_triples(subject, predicate, python_value, recursive=recursive):
                yield triple


    @classmethod
    def resolve_named_node(cls, uri:NamedNode):
        data = dict()

        # Request all triples relevant to given uri from triple store. 
        for s, p, o in registry.triple_store.query(f"DESCRIBE {uri}"):

            # get field from predicate 
            field_name = cls._get_field_name_from_predicate(p)
            
            # if we cant find a field corresponding to given predicate
            # then we continue to the next triple
            if not field_name:
                continue

            # At this stage we know that the triple refer to an actual field
            # So first we check if the field can be resolved (points to a model
            # in our registry)  
            if registry.uri_can_resolve(o):
                # if object points to a model in registry, then we return it
                # as is and will be resolved at a later stage
                data[field_name] = o
            
            # If object doesnt point to a model in our registry, we assume
            # that is a literal value so we try to convert it back to pythonic 
            # value
            else:
                data[field_name] = literal_rdf_to_python(o)

        return cls(**data)

    def save(self, recursive=True):
        if self.__class__.objects.exists(self):
            self.__class__.objects.delete(self)
        self.__class__.objects.create(self, recursive=recursive)

    def delete(self):
        self.__class__.objects.delete(self)
