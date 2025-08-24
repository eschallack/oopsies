import inspect as insp
import datetime
from typing import Any, TypeVar, Type, Dict, Union, List, Callable
from oopsies.column_mapping_engine import rank
from faker import Faker
from faker.proxy import Faker as FakerProxy
from faker.providers import BaseProvider
from faker.providers.date_time import Provider as DateTimeProvider
from faker.providers.misc import Provider as MiscProvider
from faker.providers.python import Provider as PythonProvider
from sqlalchemy.orm import Mapper, RelationshipProperty
try:
    from sqlalchemy.orm import DeclarativeMeta
except ImportError:
    from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy import (inspect,Column,ARRAY,BigInteger,BINARY,Boolean,CLOB,Date,DateTime,Enum,Float,Integer,Interval,JSON,LargeBinary,Numeric,SmallInteger,Unicode,UnicodeText,String,Time)
from sqlalchemy.sql.sqltypes import (BOOLEAN,VARCHAR,NullType,UUID,ARRAY,BIGINT,DATE,DATETIME,CHAR,DECIMAL,FLOAT,INTEGER,NCHAR,SMALLINT,TIMESTAMP,REAL,DOUBLE_PRECISION)
from typing import get_type_hints
__version__ = "0.10.2208140"
__all__ = (
    "SqlAlchemyProvider",
)

ModelType = TypeVar("ModelType")
ColumnType = TypeVar("ColumnType", bound=TypeEngine)
PrimitiveJsonTypes = Union[str, int, bool, None]
GeneratorFunction = Callable[
    [Faker, Column], Column
]
GeneratorSpec = Union[str, GeneratorFunction]

def _generate_date(generator: DateTimeProvider, _: Any) -> datetime.date:
    return generator.date_time().date()
def _generate_date_time(generator: DateTimeProvider, _: Any) -> datetime.date:
    return generator.date_time()
def _generate_time(generator: DateTimeProvider, _: Any) -> datetime.time:
    return generator.date_time().time()
def _generate_uuid(generator: MiscProvider, _: Any) -> bytes:
    return generator.uuid4()
def _generate_null(generator: MiscProvider, _: Any) -> bytes:
    return None

DEFAULT_MAPPINGS: Dict[TypeEngine, GeneratorSpec] = {
    BigInteger: int,
    Boolean: bool,
    BOOLEAN: bool,
    Date: datetime,
    DateTime: datetime,
    Float: float,
    Integer: int,
    Interval: "time_delta",
    JSON: dict,
    LargeBinary: "binary",
    Numeric: float,
    SmallInteger: int,
    String: str,
    VARCHAR: str,
    Time: _generate_time,
    Unicode: str,
    UnicodeText: str,
    NullType:_generate_null,
    ARRAY:str,
    BIGINT:str,
    DATE:str,
    DATETIME:_generate_date_time,
    CHAR:str,
    DECIMAL:float,
    FLOAT:float,
    INTEGER:int,
    NCHAR:str,
    CHAR:str,
    SMALLINT:int,
    TIMESTAMP:_generate_date_time,
    REAL:float,
    DOUBLE_PRECISION:float,
    UUID:_generate_uuid
}
class TypeInterpreter:
    def scan_base_class(cls):
        """Scan a base class for all methods and capture their return types."""
        instance = cls()
        results = {}
        exclude_attrs = ['add_provider']
        for attr in dir(instance):
            if attr.startswith("_") or attr in exclude_attrs:
                continue
            try:
                member = getattr(instance, attr)
            except TypeError:
                continue
            if insp.isfunction(member) or insp.ismethod(member):
                try:
                    hints = get_type_hints(member)
                    ret_type = hints.get("return", insp.signature(member).return_annotation)
                except Exception:
                    ret_type = insp.signature(member).return_annotation
                if ret_type is insp._empty:
                    ret_type = None
               
                results[member] = ret_type
        return results