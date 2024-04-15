# Cellini Object Data Mapper

> *a pythonic data mapper between pyoxigraph store and pydantic models*

Cellini Object Data Mapper extends [pydantic BaseModel](https://github.com/pydantic/pydantic) and makes it ease to work with [Web Ontologies](https://en.wikipedia.org/wiki/Web_Ontology_Language) in a pythonic way.
It provides the ability to store and query python objects in a triple store, similar to the way SQLalchemy works on sql databases.
The underline triple store in use is [pyoxigraph](https://github.com/oxigraph/oxigraph). 

It is written as part of "cellini" broader project but can work as a standalone library as well.

Here is a quick example 

```python
from typing import Optional
from cellini.odm import *

class Person(RdfBaseModel):
    name:str
    age:Optional[int]

Person(name="John Doe", age=80).save()

for person in Person.objects.all():
    print(f"{person.name} has reached the age of {person.age}")

# John Doe has reached the age of 80
```

Here is another more advanced example

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

# <cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Organization>
# <cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <http://purl.org/dc/terms/identifier> "fa20032a-2898-441f-bd9d-54cb5fe2bfa1"
# <cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <https://cellini.io/ns/name> "An org"
# <cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <https://cellini.io/ns/employees> <cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3>
# <cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag>
# <cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd>
# <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Employee>
# <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
# <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <http://purl.org/dc/terms/identifier> "fe589e2e-6086-4183-93fa-4e26a62dbfbd"
# <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <https://cellini.io/ns/name> "John Doe"
# <cellini:Employee:fe589e2e-6086-4183-93fa-4e26a62dbfbd> <https://cellini.io/ns/position> "cleaner"
# <cellini:Bag:ca01367e-68a9-4f91-b7d7-bd7b64868ed3> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61>
# <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Employee>
# <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
# <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <http://purl.org/dc/terms/identifier> "188ee538-4ede-465f-a8e5-663feb95ea61"
# <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <https://cellini.io/ns/name> "Jane Doe"
# <cellini:Employee:188ee538-4ede-465f-a8e5-663feb95ea61> <https://cellini.io/ns/position> "CEO"
# <cellini:Organization:fa20032a-2898-441f-bd9d-54cb5fe2bfa1> <https://cellini.io/ns/owner> <cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a>
# <cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Owner>
# <cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://cellini.io/ns/Person>
# <cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <http://purl.org/dc/terms/identifier> "7ba3ac44-f1d3-481b-80b6-83bca313fc7a"
# <cellini:Owner:7ba3ac44-f1d3-481b-80b6-83bca313fc7a> <https://cellini.io/ns/name> "Some owner"

org.save()

for employee in Organization.objects.get(org.identifier).employees:
    print(employee.name, "->", employee.position)

# John Doe -> cleaner
# Jane Doe -> CEO
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
