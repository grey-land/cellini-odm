# Cellini Object Data Mapper

*Cellini Object Data Mapper* is a python library, that maps python classes to RDF triples. 

It extends pydantic BaseModel and provides the ability to easily implement Web Ontolodies in a pythonic way.
Additionally it provides the ability to store and query the graph similar to SQLalchemy. The triple store,
in use is provided by pyoxigraph. 

See a quick example 

```python
from typing import Optional
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
<cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Organization>
<cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <http://purl.org/dc/terms/identifier> "fa20032a-2898-441f-bd9d-54cb5fe2bfa1"
<cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <https://cellini.io/ns/name> "An org"
<cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <https://cellini.io/ns/employees> <cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3>
<cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag>
<cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd>
<cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Employee>
<cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
<cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <http://purl.org/dc/terms/identifier> "fe589e2e-6086-4183-93fa-4e26a62dbfbd"
<cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <https://cellini.io/ns/name> "John Doe"
<cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <https://cellini.io/ns/position> "cleaner"
<cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61>
<cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Employee>
<cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
<cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <http://purl.org/dc/terms/identifier> "188ee538-4ede-465f-a8e5-663feb95ea61"
<cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <https://cellini.io/ns/name> "Jane Doe"
<cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <https://cellini.io/ns/position> "CEO"
<cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <https://cellini.io/ns/owner> <cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a>
<cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Owner>
<cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
<cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <http://purl.org/dc/terms/identifier> "7ba3ac44-f1d3-481b-80b6-83bca313fc7a"
<cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <https://cellini.io/ns/name> "Some owner"
```


---

## Coverage

| Name                        |    Stmts |     Miss |   Cover |
|---------------------------- | -------: | -------: | ------: |
| cellini/odm/\_\_init\_\_.py |        4 |        0 |    100% |
| cellini/odm/base.py         |       61 |        9 |     85% |
| cellini/odm/model.py        |       92 |        7 |     92% |
| cellini/odm/query.py        |       36 |        3 |     92% |
| cellini/odm/types.py        |       54 |        3 |     94% |
| cellini/odm/utils.py        |       66 |       16 |     76% |
|                   **TOTAL** |  **313** |   **38** | **88%** |
