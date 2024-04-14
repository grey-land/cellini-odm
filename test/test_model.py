import sys
from tempfile import TemporaryDirectory
import unittest
from typing import Optional, List
from datetime import datetime
from pydantic import Field
from pyoxigraph import *

from cellini.odm import *


def temp_clear_registry():
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")
    registry._store = Store(path=TemporaryDirectory().name)
    registry.clear()
    registry.add(Bag)

class Simple(RdfBaseModel):
    number:int
    phrase:str
    published:Optional[datetime] = Field(default_factory=datetime.now)

class Nested(RdfBaseModel):
    simple:Simple
    # optional:Optional[Simple]

class Complex(Simple):
    many:List[str] = Field(default_factory=list)

class DeepNested(RdfBaseModel):
    nested:Nested


class TestDefaultNamespace(RdfBaseModel):
    
    a_field:Optional[str] = Field(None)

class TestCustomNamespace(RdfBaseModel):

    @classmethod
    def __rdf_namespace__(cls) -> str:
        return "http://www.w3.org/ns/oa#"

    a_field:Optional[str] = Field(None)


    
class TestRdfBaseModel(unittest.TestCase):
    """
    test various naming functions
    """

    def setUp(self):
        temp_clear_registry()
        registry.clear()
        registry.add(Simple)
        registry.add(Nested)
        registry.add(DeepNested)

    def test_namespace_default_rdf_type(self):
        a = TestDefaultNamespace()
        self.assertEqual(TestDefaultNamespace.__rdf_type__().value, "https://cellini.io/ns/TestDefaultNamespace")
        self.assertEqual(a.__rdf_type__().value, "https://cellini.io/ns/TestDefaultNamespace")
        
    def test_namespace_custom_rdf_type(self):
        b = TestCustomNamespace()
        self.assertEqual(TestCustomNamespace.__rdf_type__().value, "http://www.w3.org/ns/oa#TestCustomNamespace")
        self.assertEqual(b.__rdf_type__().value, "http://www.w3.org/ns/oa#TestCustomNamespace")

    def test_namespace_default_predicate(self):
        p = TestDefaultNamespace._get_predicate_from_field('a_field')
        self.assertEqual(p.value, "https://cellini.io/ns/a_field")

    def test_namespace_custom_predicate(self):
        p = TestCustomNamespace._get_predicate_from_field('a_field')
        self.assertEqual(p.value, "http://www.w3.org/ns/oa#a_field")

    def test_namespace_default_rdf_types(self):
        rdftypes = list(TestDefaultNamespace.__rdf_types__())
        self.assertEqual(len(rdftypes), 1)
        self.assertEqual(rdftypes, [TestDefaultNamespace.__rdf_type__()])
    
    def test_namespace_custom_rdf_types(self):
        rdftypes = list(TestCustomNamespace.__rdf_types__())
        self.assertEqual(len(rdftypes), 1)
        self.assertEqual(rdftypes, [TestCustomNamespace.__rdf_type__()])

    def test_namespace_default_rdf_triples(self):
        for s,p,o in TestDefaultNamespace(a_field="test").to_triples():
            self.assertTrue(s.value.startswith("cellini:TestDefaultNamespace:"))
            self.assertTrue(not s.value.startswith("https://cellini.io/ns/TestDefaultNamespace"))

            if p.value == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                self.assertEqual(o.value, "https://cellini.io/ns/TestDefaultNamespace")
            if o.value == "test":
                self.assertEqual(p.value, "https://cellini.io/ns/a_field")

    def test_namespace_custom_rdf_triples(self):
        for s,p,o in TestCustomNamespace(a_field="test").to_triples():
            self.assertTrue(s.value.startswith("cellini:TestCustomNamespace:"))
            self.assertTrue(not s.value.startswith("http://www.w3.org/ns/oa#TestCustomNamespace"))

            if p.value == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                self.assertEqual(o.value, "http://www.w3.org/ns/oa#TestCustomNamespace")
            if o.value == "test":
                self.assertEqual(p.value, "http://www.w3.org/ns/oa#a_field")

    def test_namespace_default_rdf_uri(self):
        self.assertTrue(TestDefaultNamespace().__rdf_uri__.value.startswith("cellini:TestDefaultNamespace:"))

    def test_namespace_custom_rdf_uri(self):
        self.assertTrue(TestCustomNamespace().__rdf_uri__.value.startswith("cellini:TestCustomNamespace:"))







    def test_simple_class_defaults(self):
        obj = Simple(number=1, phrase="test")
        self.assertEqual(obj.__rdf_title__(), "Simple")
        self.assertEqual(obj.__rdf_type__().value, "https://cellini.io/ns/Simple")
        self.assertEqual(len(list(obj.__rdf_types__())), 1)

    def test_simple_class_triples(self):
        obj = Simple(number=1, phrase="test")
        self.assertEqual(len(list(obj.to_triples())), 5)
        for s, p, o in obj.to_triples():
            
            self.assertEqual(s, obj.__rdf_uri__)

            self.assertTrue(p.value in [
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                "http://purl.org/dc/terms/identifier",
                "https://cellini.io/ns/number",
                "https://cellini.io/ns/phrase",
                "https://cellini.io/ns/published",
            ])

            if p.value == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                self.assertEqual(o.value, "https://cellini.io/ns/Simple")
            elif p.value == "http://purl.org/dc/terms/identifier":
                self.assertEqual(o.value, f'{obj.identifier}')
            else:
                self.assertIsInstance(o, Literal)


    def test_nested_class_triples(self):
        obj = Nested(simple=Simple(number=1, phrase="test"))
        self.assertEqual(len(list(obj.to_triples(recursive=False))), 3)
        self.assertEqual(len(list(obj.to_triples())), 8)

    def test_nested_class_namednode(self):
        obj = Nested(simple=Simple(number=1, phrase="test"))
        for t in obj.to_triples():
            registry.graph.add(Quad(*t))

        a = Nested(simple=obj.simple.__rdf_uri__)
        self.assertEqual(a.simple.number, 1)
        self.assertEqual(a.simple.phrase, "test")
        self.assertEqual(a.simple.identifier, obj.simple.identifier)
        self.assertEqual(a.simple.published, obj.simple.published)

        

    
    def test_deepnested_class_triples(self):
        obj = DeepNested(nested=Nested(simple=Simple(number=1, phrase="test")))
        self.assertEqual(len(list(obj.to_triples(recursive=False))), 3)
        self.assertEqual(len(list(obj.to_triples())), 11)


    def test_deepnested_class_namednode_argument(self):
        obj = DeepNested(nested=Nested(simple=Simple(number=1, phrase="test")))

        for t in obj.to_triples():
            registry.graph.add(Quad(*t))

        a = DeepNested(nested=obj.nested.__rdf_uri__)
        self.assertEqual(a.nested.identifier, obj.nested.identifier)
        self.assertEqual(a.nested.simple.identifier, obj.nested.simple.identifier)
        self.assertEqual(a.nested.simple.published, obj.nested.simple.published)
        self.assertEqual(a.nested.simple.number, 1)
        self.assertEqual(a.nested.simple.phrase, "test")
        

    def test_deepnested_class_namednode(self):
        obj = DeepNested(
                    nested=Nested(
                        simple=Simple(number=2, phrase="sec")))

        for t in obj.to_triples():
            registry.graph.add(Quad(*t))
        
        a = registry.resolve_named_node(obj.__rdf_uri__)

        self.assertEqual(a.identifier, obj.identifier)
        self.assertEqual(a.nested.identifier, obj.nested.identifier)
        self.assertEqual(a.nested.simple.identifier, obj.nested.simple.identifier)
        self.assertEqual(a.nested.simple.published, obj.nested.simple.published)
        self.assertEqual(a.nested.simple.number, 2)
        self.assertEqual(a.nested.simple.phrase, "sec")


if __name__ == '__main__':
    unittest.main()