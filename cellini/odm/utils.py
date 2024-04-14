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

    # base64Binary = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#base64Binary")
    # bounded = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#bounded")
    # byte = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#byte")
    # cardinality = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#cardinality")
    # dateTimeStamp = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#dateTimeStamp")
    # day = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#day")
    # dayTimeDuration = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#dayTimeDuration")
    # decimal = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#decimal")
    # double = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#double")
    # duration = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#duration")
    # enumeration = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#enumeration")
    # explicitTimezone = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#explicitTimezone")
    # fractionDigits = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#fractionDigits")
    # gDay = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#gDay")
    # gMonth = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#gMonth")
    # gMonthDay = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#gMonthDay")
    # gYear = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#gYear")
    # gYearMonth = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#gYearMonth")
    # hexBinary = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#hexBinary")
    # hour = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#hour")
    # int = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#int")
    
    # language = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#language")
    # length = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#length")
    # long = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#long")
    # maxExclusive = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#maxExclusive")
    # maxInclusive = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#maxInclusive")
    # maxLength = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#maxLength")
    # minExclusive = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#minExclusive")
    # minInclusive = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#minInclusive")
    # minLength = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#minLength")
    # minute = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#minute")
    # month = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#month")
    # negativeInteger = NamedNode("http://www.w3.org/2001/XMLSchema#negativeInteger")
    # nonNegativeInteger = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#nonNegativeInteger")
    # normalizedString = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#normalizedString")
    # numeric = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#numeric")
    # ordered = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#ordered")
    # pattern = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#pattern")
    # positiveInteger = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#positiveInteger")
    # second = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#second")
    # short = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#short")
    # time = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#time")
    # timezoneOffset = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#timezoneOffset")
    # token = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#token")
    # totalDigits = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#totalDigits")
    # unsignedByte = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#unsignedByte")
    # unsignedInt = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#unsignedInt")
    # unsignedLong = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#unsignedLong")
    # unsignedShort = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#unsignedShort")
    # whiteSpace = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#whiteSpace")
    # year = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#year")
    # yearMonthDuration = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#yearMonthDuration")




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