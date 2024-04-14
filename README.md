# Cellini Object Data Mapper

*Cellini Object Data Mapper* is a python library, that maps python classes to RDF triples. 

It extends pydantic BaseModel and provides the ability to easily implement Web Ontolodies in a pythonic way.
Additionally it provides the ability to store and query the graph similar to SQLalchemy. The triple store,
in use is provided by pyoxigraph. 

See a quick example 

```python
from cellini.odm import *

class Person(RdfBaseModel):
    name:str
    age:Optional[int]

Person(name="John Doe", age=80).save()

for person in Person.objects.all():
    print(f"{person.name} has reached the age of {person.age}")

"John Doe has reached the age of 80"
```


Or another one that shows more advanced use

```python
from typing import List,Optional
from cellini.odm import *

class Person(RdfBaseModel):
    name:str

class Employee(Person):
    position:Optional[str]

class Owner(Person):
    pass

class Organization(RdfBaseModel):
    name:str
    employees:List[Employee]
    owner:Owner

org = Organization(
            name="An org",
            employees=[
                Employee(name="John Doe", position="cleaner"),
                Employee(name="Jane Doe", position="CEO"),
            ],
            owner=Owner(name="Some owner")
        )

for s, p, o in org.to_triples():
    print(s, p, o)
```

would result to following triples

```
<cellini:Organization:0d7aab80-df35-4cdf-b75c-0893c1551aeb> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Organization>
<cellini:Organization:0d7aab80-df35-4cdf-b75c-0893c1551aeb> <http://purl.org/dc/terms/identifier> "0d7aab80-df35-4cdf-b75c-0893c1551aeb"
<cellini:Organization:0d7aab80-df35-4cdf-b75c-0893c1551aeb> <https://cellini.io/ns/name> "An org"
<cellini:Organization:0d7aab80-df35-4cdf-b75c-0893c1551aeb> <https://cellini.io/ns/employees> <cellini-type:Bag:9010c97c-ba63-483c-b76f-eb1deb9a3037>
<cellini-type:Bag:9010c97c-ba63-483c-b76f-eb1deb9a3037> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag>
<cellini-type:Bag:9010c97c-ba63-483c-b76f-eb1deb9a3037> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <cellini:Employee:9346d71a-5ef8-4c50-8414-0dc776174a09>
<cellini:Employee:9346d71a-5ef8-4c50-8414-0dc776174a09> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Employee>
<cellini:Employee:9346d71a-5ef8-4c50-8414-0dc776174a09> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
<cellini:Employee:9346d71a-5ef8-4c50-8414-0dc776174a09> <http://purl.org/dc/terms/identifier> "9346d71a-5ef8-4c50-8414-0dc776174a09"
<cellini:Employee:9346d71a-5ef8-4c50-8414-0dc776174a09> <https://cellini.io/ns/name> "John Doe"
<cellini:Employee:9346d71a-5ef8-4c50-8414-0dc776174a09> <https://cellini.io/ns/position> "cleaner"
<cellini-type:Bag:9010c97c-ba63-483c-b76f-eb1deb9a3037> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <cellini:Employee:1589fe12-7d94-4c23-b08c-aaaa840eff01>
<cellini:Employee:1589fe12-7d94-4c23-b08c-aaaa840eff01> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Employee>
<cellini:Employee:1589fe12-7d94-4c23-b08c-aaaa840eff01> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
<cellini:Employee:1589fe12-7d94-4c23-b08c-aaaa840eff01> <http://purl.org/dc/terms/identifier> "1589fe12-7d94-4c23-b08c-aaaa840eff01"
<cellini:Employee:1589fe12-7d94-4c23-b08c-aaaa840eff01> <https://cellini.io/ns/name> "Jane Doe"
<cellini:Employee:1589fe12-7d94-4c23-b08c-aaaa840eff01> <https://cellini.io/ns/position> "CEO"
<cellini:Organization:0d7aab80-df35-4cdf-b75c-0893c1551aeb> <https://cellini.io/ns/owners> <cellini-type:Bag:9c35cce5-6fc2-475a-b1e6-88a0778d0f01>
<cellini-type:Bag:9c35cce5-6fc2-475a-b1e6-88a0778d0f01> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag>
<cellini-type:Bag:9c35cce5-6fc2-475a-b1e6-88a0778d0f01> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <cellini:Owner:dee36976-8816-4ea1-b935-eceac41d0899>
<cellini:Owner:dee36976-8816-4ea1-b935-eceac41d0899> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Owner>
<cellini:Owner:dee36976-8816-4ea1-b935-eceac41d0899> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
<cellini:Owner:dee36976-8816-4ea1-b935-eceac41d0899> <http://purl.org/dc/terms/identifier> "dee36976-8816-4ea1-b935-eceac41d0899"
<cellini:Owner:dee36976-8816-4ea1-b935-eceac41d0899> <https://cellini.io/ns/name> "Some owner"
<cellini:Owner:dee36976-8816-4ea1-b935-eceac41d0899> <https://cellini.io/ns/share> "100"^^<http://www.w3.org/2001/XMLSchema#integer>
```


---

## Coverage

| Name                        |    Stmts |     Miss |   Cover |
|---------------------------- | -------: | -------: | ------: |
| cellini/odm/\_\_init\_\_.py |        2 |        0 |    100% |
| cellini/odm/model.py        |       98 |        7 |     93% |
| cellini/odm/query.py        |       39 |        3 |     92% |
| cellini/odm/registry.py     |       78 |        8 |     90% |
| cellini/odm/utils.py        |       66 |       16 |     76% |
|                   **TOTAL** |  **283** |   **34** | **88%** |