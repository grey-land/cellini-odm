import sys
import unittest
import hashlib
from pyoxigraph import Triple, Literal, Store
from tempfile import TemporaryDirectory
from pydantic_core import core_schema
        
from cellini.odm import *
from cellini.odm.base import AbstractNamedNode, RdfRegistry
from cellini.odm.utils import RDF, XSD
from cellini.odm import *


class A_model(RdfBaseModel):
    number:int

    
class TestDefaultRegistry(unittest.TestCase):
    """
    test various naming functions
    """

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")
        registry._store = Store(path=TemporaryDirectory().name)
        registry.clear()
        registry.add(Bag)
        registry.add(A_model)

    def test_registry_default_uri_prefixes(self):
        self.assertEqual(registry.uri_prefix, "cellini:")
        self.assertEqual(Bag.__rdf_title__(), "cellini:Bag")
        self.assertEqual(A_model.__rdf_title__(), "cellini:A_model")
        self.assertTrue(A_model.__rdf_type__().value.startswith("https://cellini.io/ns/A_model"))

    def test_registry_custom_uri_prefixes(self):
        registry._uri_prefix = "http://example.com/"
        self.assertEqual(registry.uri_prefix, "http://example.com/")
        self.assertEqual(Bag.__rdf_title__(), "http://example.com/Bag")
        self.assertEqual(A_model.__rdf_title__(), "http://example.com/A_model")
        self.assertEqual(Bag.__rdf_title__(), "http://example.com/Bag")
        self.assertTrue(A_model(number=2).__rdf_uri__.value.startswith("http://example.com/A_model"))
        self.assertTrue(A_model.__rdf_type__().value.startswith("https://cellini.io/ns/A_model"))
        
        # Revert changes so tests can continue
        registry._uri_prefix  = RdfRegistry().uri_prefix



class TestCustomRdfType(unittest.TestCase):
    
    def test_registry_with_custom_rdf_type(self):
        
        class CustomStrType(str, AbstractNamedNode):

            @classmethod
            def __rdf_title__(cls) -> str:
                return "test:I-am-whatever-type"

            @property
            def identifier(self):
                return hashlib.md5(self.encode()).hexdigest()

            @classmethod
            def resolve_named_node(cls, node):
                for s, p, o in registry.query(f"DESCRIBE {node}"):
                    if s.value.startswith(cls.__rdf_title__()):
                        if p == RDF.type:
                            pass
                        else:
                            return o.value

            def to_triples(self, **kwargs):
                # yield Triple(self.__rdf_uri__, RDF.type, XSD.string)
                yield Triple(self.__rdf_uri__, XSD.string, Literal(self))

            @classmethod
            def __get_pydantic_core_schema__(cls, source_type, handler):
                return core_schema.no_info_after_validator_function(cls, handler(str))

        class StandardModel(RdfBaseModel):
            name:str
            many:list[str] = []
            custom:CustomStrType
        

        registry.add(CustomStrType)

        obj = StandardModel(name="test", custom=CustomStrType("hello world !"))
        obj.save()
        
        self.assertEqual(registry.uri_to_basemodel(obj.__rdf_uri__), StandardModel)

        res = StandardModel.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertEqual(obj.name, "test")
        self.assertIsInstance(obj.custom, CustomStrType)
        self.assertEqual(obj.custom, CustomStrType("hello world !"))
        self.assertEqual(obj.custom, "hello world !")
