import inspect as insp
import datetime
from typing import TypeVar, Dict, Union, Callable
from faker import Faker
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy import (Column,ARRAY,BigInteger,BINARY,Boolean,CLOB,Date,DateTime,Enum,Float,Integer,Interval,JSON,LargeBinary,Numeric,SmallInteger,Unicode,UnicodeText,String,Time)
from sqlalchemy.sql.sqltypes import (BOOLEAN,VARCHAR,NullType,UUID,ARRAY,BIGINT,DATE,DATETIME,CHAR,DECIMAL,FLOAT,INTEGER,NCHAR,SMALLINT,TIMESTAMP,REAL,DOUBLE_PRECISION)
from typing import get_type_hints
from uuid import UUID as tUUID

GeneratorFunction = Callable[
    [Faker, Column], Column
]
GeneratorSpec = Union[str, GeneratorFunction]

DEFAULT_MAPPINGS: Dict[TypeEngine, GeneratorSpec] = {
    BigInteger: int,
    Boolean: bool,
    BOOLEAN: bool,
    Date: datetime,
    DateTime: datetime,
    Float: float,
    Integer: int,
    Interval: datetime.timedelta,
    JSON: dict,
    LargeBinary: "binary",
    Numeric: float,
    SmallInteger: int,
    String: str,
    CHAR:str,
    VARCHAR: str,
    Time: datetime.time,
    Unicode: str,
    UnicodeText: str,
    NullType:None,
    ARRAY:str,
    BIGINT:str,
    DATE:str,
    DATETIME:datetime,
    DECIMAL:float,
    FLOAT:float,
    INTEGER:int,
    NCHAR:str,
    CHAR:str,
    SMALLINT:int,
    TIMESTAMP:datetime,
    REAL:float,
    DOUBLE_PRECISION:float,
    UUID:tUUID
}

class TypeInterpreter:
    """Methods for discovering types of functions, classes, etc.
    """
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
    
    def _get_col_type(column:Column):
        """Convert SQLAlchemy Column type to python datatype
        TODO: replace with SQLModel
        :param column: Sqlalchemy col
        :type column: Column
        :return: a python type
        :rtype: Typevar
        """
        t = column.type
        if isinstance(t, TypeEngine):
            try:
                return t.python_type
            except NotImplementedError:
                pass
        try:
            if hasattr(t, 'data_type'):
                t=t.data_type
            return t._type_affinity().python_type
        except Exception:
            return None