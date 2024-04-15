import uuid
from dataclasses import dataclass
from pyoxigraph  import NamedNode, Literal
from typing      import Any, Union
from datetime    import datetime, date
from pydantic    import AnyHttpUrl, AnyUrl, NonNegativeInt

@dataclass
class DCTERMS:
    identifier = NamedNode("http://purl.org/dc/terms/identifier")

@dataclass
class XSD:
    anyURI = NamedNode("http://www.w3.org/2001/XMLSchema#anyURI")
    date = NamedNode("http://www.w3.org/2001/XMLSchema#date")
    dateTime = NamedNode("http://www.w3.org/2001/XMLSchema#dateTime")
    float = NamedNode("http://www.w3.org/2001/XMLSchema#float")
    integer = NamedNode("http://www.w3.org/2001/XMLSchema#integer")
    nonPositiveInteger = NamedNode("http://www.w3.org/2001/XMLSchema#nonPositiveInteger")
    string = NamedNode("http://www.w3.org/2001/XMLSchema#string")
    boolean = NamedNode("http://www.w3.org/2001/XMLSchema#boolean")

@dataclass
class RDF:
    Bag = NamedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag")
    type = NamedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

class ObjectAlreadyExists(Exception):
    pass

class UnsupportedType(Exception):
    pass

def literal_python_to_rdf(value:Any, python_type:Any=None)->Union[None, NamedNode, Literal]:
    """ convert standard python types to rdf literals """
    if value == None:
        return None
    if python_type == None:
        python_type = type(value)
    # string
    if python_type in [str, uuid.UUID]:
        return Literal(f"{value}")
    # Urls
    if python_type in [AnyHttpUrl, AnyUrl]:
        return Literal(f"{value}", datatype=XSD.anyURI)
    # boolean
    elif python_type == bool:
        return Literal('true' if value else 'false', datatype=XSD.boolean)
    # intreger
    elif python_type in [int, NonNegativeInt]:
        return Literal(f"{value}", datatype=XSD.integer)
    # float
    elif python_type == float:
        return Literal(f"{value}", datatype=XSD.float)
    # datetime
    elif python_type == datetime:
        return Literal(value.isoformat(), datatype=XSD.dateTime)
    # date
    elif python_type == date:
        return Literal(value.isoformat(), datatype=XSD.date)

    raise UnsupportedType(f"! Unknown value type={python_type} for value={value}")

def literal_rdf_to_python(value:Union[NamedNode, Literal])->Any:
    """ convert rdf literals to python types """

    if isinstance(value, Literal):
        
        if value.datatype in [ XSD.string, XSD.anyURI ]:
            return value.value
        
        if value.datatype == XSD.boolean:
            if str(value.value) == 'false':
                return False
            elif str(value.value) == 'true':
                return True
            raise Exception(f'Could not parse value "{value}" to Python bool.')
        
        if value.datatype in [
                                XSD.integer, 
                                XSD.nonPositiveInteger,
                            ]:
            return int(value.value)

        if value.datatype in [ XSD.float, ]:
            return float(value.value)

        if value.datatype in [ XSD.dateTime, ]:
            return datetime.fromisoformat(value.value)

        if value.datatype in [ XSD.date, ]:
            return datetime.fromisoformat(value.value).date()

    raise UnsupportedType(f"! Unknown value type for value={value}")