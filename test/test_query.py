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

class Complex(RdfBaseModel):
    name:str
    many_list:List[str] = Field()
    simple:Simple

class TestQuery(unittest.TestCase):
    
    def setUp(self):
        temp_clear_registry()
        registry.add(Simple)
        registry.add(Complex)

    def test_simple_save(self):
        obj = Simple(number=1, phrase="test")
        obj.save()
        self.assertEqual(len(list(Simple.objects.all())), 1)
    
    def test_simple_get(self):
        obj = Simple(number=1, phrase="test")
        obj.save()
        res = Simple.objects.get(obj.identifier)
        self.assertEqual(res.identifier, obj.identifier)
        self.assertEqual(res.published, obj.published)
        self.assertEqual(res.number, 1)
        self.assertEqual(res.phrase, "test")

    def test_simple_filter(self):
        obj = Simple(number=1, phrase="test")
        obj.save()
        for res in Simple.objects.all():
            self.assertEqual(res.identifier, obj.identifier)
            self.assertEqual(res.published, obj.published)
            self.assertEqual(res.number, 1)
            self.assertEqual(res.phrase, "test")

        self.assertEqual(len(list(Simple.objects.filter(number=1))), 1)
        self.assertEqual(list(Simple.objects.filter(number=1))[0].identifier, obj.identifier)
        
        self.assertEqual(len(list(Simple.objects.filter(phrase="test"))), 1)
        self.assertEqual(list(Simple.objects.filter(phrase="test"))[0].identifier, obj.identifier)


    def test_complex_save(self):
        obj = Complex(
                    name="test-complex",
                    many_list=["a", "b"],
                    simple=Simple(number=1, phrase="test"))
        obj.save()
        self.assertEqual(len(list(Simple.objects.all())), 1)
        self.assertEqual(len(list(Complex.objects.all())), 1)
    
    def test_complex_get(self):
        obj = Complex(
                    name="test-complex",
                    many_list=["a", "b"],
                    simple=Simple(number=1, phrase="test"))
        obj.save()
        res = Complex.objects.get(obj.identifier)
        self.assertEqual(res.identifier, obj.identifier)
        self.assertEqual(res.simple.identifier, obj.simple.identifier)
        self.assertEqual(res.simple.published, obj.simple.published)
        self.assertEqual(res.simple.number, 1)
        self.assertEqual(res.simple.phrase, "test")
        self.assertEqual(res.name, "test-complex")
        self.assertIsInstance(res.many_list, list)
        self.assertEqual(res.many_list, ["a", "b"])

if __name__ == '__main__':
    unittest.main()