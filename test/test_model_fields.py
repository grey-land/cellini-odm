import sys
from tempfile import TemporaryDirectory
import unittest
from typing import Optional, List, Union
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


class TestSimpleStr(RdfBaseModel):
    name:str

class TestSimpleInt(RdfBaseModel):
    number:int

class TestNestedList(RdfBaseModel):
    complex:List[List[str]]

class TestModelNestedList(RdfBaseModel):
    complex:List[List[TestSimpleStr]]

class TestComplexList(RdfBaseModel):
    many:List[str] = Field(default_factory=list)
    many_model:List[TestSimpleStr] = Field(default_factory=list)
    many_union_model:Union[
            List[TestSimpleStr],
            List[TestSimpleInt],
        ] = Field(default_factory=list)

class TestComplexUnion(RdfBaseModel):
    complex:Union[
        None,
        List[TestSimpleStr],
        List[str],
        TestSimpleInt,
        int,
        str,
    ]

class TestComplexListUnion(RdfBaseModel):
    complex:List[
                Union[
                    # None,
                    List[TestSimpleStr],
                    List[str],
                    TestSimpleInt,
                    int,
                    str,
                ]
            ]

class TestListFieldClass(unittest.TestCase):
    
    def setUp(self):
        temp_clear_registry()
        registry.add(TestSimpleStr)
        registry.add(TestSimpleInt)
        # registry.add(TestSimpleStrList)
        # registry.add(TestSimpleIntList)
        registry.add(TestComplexList)

    def test_complex_list_fields(self):
        obj=TestComplexList()
        obj.save()
        self.assertEqual(len(list(TestComplexList.objects.all())), 1)
        a = TestComplexList.objects.get(obj.identifier)
        self.assertEqual(a.many, list())
        self.assertEqual(a.many_model, list())
        # self.assertEqual(a.many_union_model, list())
    
    def test_complex_list_values(self):
        first  = TestSimpleStr(name="first")
        second = TestSimpleStr(name="second")
        first.save()
        second.save()

        obj=TestComplexList(
            many=["first", "second"],
            many_model=[
                first, second,
                # TestSimpleStr(name="first"),
                # TestSimpleStr(name="second"),
            ]
        )
        obj.save()
        self.assertEqual(len(list(TestSimpleStr.objects.all())), 2)
        self.assertEqual(len(list(TestComplexList.objects.all())), 1)
        a = TestComplexList.objects.get(obj.identifier)
        self.assertEqual(a.identifier, obj.identifier)
        self.assertEqual(len(a.many), 2)
        self.assertEqual(len(a.many_model), 2)
        self.assertEqual(a.many, ["first", "second"])
        self.assertEqual(a.many_model[0].identifier, obj.many_model[0].identifier)
        self.assertEqual(a.many_model[1].identifier, obj.many_model[1].identifier)

    def test_complex_list_inline_values(self):
        obj=TestComplexList(
            many=["first", "second"],
            many_model=[
                TestSimpleStr(name="first"),
                TestSimpleStr(name="second"),
            ],
            many_union_model=[
                TestSimpleInt(number=1),
            ]
        )
        obj.save()
        self.assertEqual(len(list(TestComplexList.objects.all())), 1)
        a = TestComplexList.objects.get(obj.identifier)
        self.assertEqual(a.identifier, obj.identifier)
        self.assertEqual(len(a.many), 2)
        self.assertEqual(len(a.many_model), 2)
        self.assertEqual(a.many, ["first", "second"])
        self.assertEqual(a.many_model[0].identifier, obj.many_model[0].identifier)
        self.assertEqual(a.many_model[1].identifier, obj.many_model[1].identifier)
        self.assertIsInstance(a.many_union_model, list)
        self.assertEqual(len(a.many_union_model), 1)
        self.assertEqual(a.many_union_model[0].identifier, obj.many_union_model[0].identifier)
        self.assertEqual(a.many_union_model[0].number, 1)

    def test_complex_list_union(self):
        obj_int=TestComplexList(
            many_union_model=[
                TestSimpleInt(number=1),
            ]
        )
        obj_str=TestComplexList(
            many_union_model=[
                TestSimpleStr(name="one"),
            ]
        )

        obj_int.save()
        obj_str.save()
        self.assertEqual(len(list(TestComplexList.objects.all())), 2)
        
        a = TestComplexList.objects.get(obj_int.identifier)
        self.assertEqual(a.identifier, obj_int.identifier)
        self.assertIsInstance(a.many_union_model, list)
        self.assertEqual(len(a.many_union_model), 1)
        self.assertEqual(a.many_union_model[0].identifier, obj_int.many_union_model[0].identifier)
        self.assertEqual(a.many_union_model[0].number, 1)

        b = TestComplexList.objects.get(obj_str.identifier)
        self.assertEqual(b.identifier, obj_str.identifier)
        self.assertIsInstance(b.many_union_model, list)
        self.assertEqual(len(a.many_union_model), 1)
        self.assertEqual(b.many_union_model[0].identifier, obj_str.many_union_model[0].identifier)
        self.assertEqual(b.many_union_model[0].name, "one")


class TestNestedListString(unittest.TestCase):

    def setUp(self):
        temp_clear_registry()
        registry.add(TestNestedList)
    
    def test_nested_list_field_1(self):
        obj = TestNestedList(complex=[ ["a","b"], ["c", "d", "e"] ])
        obj.save()
        n = TestNestedList.objects.get(obj.identifier)
        self.assertEqual(n.identifier, obj.identifier)
        self.assertEqual(n.complex, [ ["a","b"], ["c", "d", "e"] ])


class TestModelNestedListClass(unittest.TestCase):

    def setUp(self):
        temp_clear_registry()
        registry.add(TestSimpleStr)
        registry.add(TestModelNestedList)

    def test_complex_list_union_3(self):
        obj = TestModelNestedList(complex=[
            [
                TestSimpleStr(name="one")
            ],
            [
                TestSimpleStr(name="two"),
                TestSimpleStr(name="three"),
            ]
        ])
        obj.save()
        res = TestModelNestedList.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, list)
        self.assertEqual(res.complex, obj.complex)

class TestUnionFieldClass(unittest.TestCase):

    def setUp(self):
        temp_clear_registry()
        registry.add(TestSimpleStr)
        registry.add(TestSimpleInt)
        registry.add(TestComplexUnion)
    
    def test_complex_union_1(self):
        obj = TestComplexUnion(complex="string")
        obj.save()
        res = TestComplexUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, str)
        self.assertEqual(res.complex, "string")

    def test_complex_union_2(self):
        obj = TestComplexUnion(complex=["string"])
        obj.save()
        res = TestComplexUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, list)
        self.assertEqual(res.complex, ["string"])

    def test_complex_union_3(self):
        obj = TestComplexUnion(complex=1)
        obj.save()
        res = TestComplexUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, int)
        self.assertEqual(res.complex, 1)

    def test_complex_union_4(self):
        obj = TestComplexUnion(complex=TestSimpleInt(number=1))
        obj.save()
        res = TestComplexUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, TestSimpleInt)
        self.assertEqual(res.complex.number, 1)

    def test_complex_union_4(self):
        obj = TestComplexUnion(complex=[TestSimpleStr(name="one")])
        obj.save()
        res = TestComplexUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, list)
        self.assertIsInstance(res.complex[0], TestSimpleStr)
        self.assertEqual(res.complex[0].identifier, res.complex[0].identifier)
        self.assertEqual(res.complex[0].name, "one")




class TestListUnionFieldClass(unittest.TestCase):

    def setUp(self):
        temp_clear_registry()
        registry.add(TestSimpleStr)
        registry.add(TestSimpleInt)
        registry.add(TestComplexListUnion)
    
    def test_complex_list_union_1(self):
        obj = TestComplexListUnion(complex=["string"])
        obj.save()
        res = TestComplexListUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, list)
        self.assertEqual(res.complex, ["string"])

    def test_complex_list_union_2(self):
        obj = TestComplexListUnion(complex=[1])
        obj.save()
        res = TestComplexListUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, list)
        self.assertEqual(res.complex, [1])

    def test_complex_list_union_3(self):
        obj = TestComplexListUnion(complex=[[TestSimpleStr(name="one")]])
        obj.save()
        res = TestComplexListUnion.objects.get(obj.identifier)
        self.assertEqual(obj.identifier, res.identifier)
        self.assertIsInstance(res.complex, list)
        self.assertEqual(res.complex, obj.complex)


    # class TestComplexListUnion(RdfBaseModel):
    #     complex:List[
    #                 Union[
    #                     # None,
    #                     List[TestSimpleStr],
    #                     List[str],
    #                     TestSimpleInt,
    #                     int,
    #                 ]
    #             ]

if __name__ == '__main__':
    unittest.main()
