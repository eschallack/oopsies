"""`SQLAlchemy Faker <https://faker-sqlalchemy.readthedocs.io/en/latest/>`_ is a provider for the
`Faker <https://github.com/joke2k/faker>`_ library that helps populate `SQLAlchemy ORM <https://www.sqlalchemy.org/>`_
models with dummy data. Creating a new instance of a model can be as simple as calling
``fake.sqlalchemy_model(SomeModel)``.


Installation
------------

The recommend way to install SQLAlchemy Faker is with ``pip``::

    pip install faker_sqlalchemy

Example
-------

Say you have some model declared using SQLAlchemy's ORM.

>>> class SomeModel(Base):
...     __tablename__ = "some_model"
...
...     id = Column(Integer, primary_key=True)
...
...     value = Column(String)

And, you want to easily generate some data,

>>> from faker_sqlalchemy import SqlAlchemyProvider
>>>
>>> fake = Faker()
>>> fake.add_provider(SqlAlchemyProvider)
>>>
>>> instance = fake.sqlalchemy_model(SomeModel)

Use ``instance`` as desired.

>>> print(instance.value)
RNvnAvOpyEVAoNGnVZQU

Supported Versions
------------------

Currently SQLAlchemy versions 1.3 and 1.4 are supported. Support for SQLAlchemy 2.0 will be added when it is released.

Faker versions ``>=8`` are currently supported, though it should be noted that the testing matrix isn't exhaustive. If
bugs come up with a particular version of faker beyond version 8.0, submit a ticket to add support.

Python versions ``>=3.7`` are currently supported. If python 3.6 support is desired, submit a ticket to add support. Support
for Python 3.11 will be added when it is officially supported by SQLAlchemy. Currently, this is waiting on greenlet
releasing support for python 3.11.
"""
import inspect as insp
import datetime
from typing import Any, TypeVar, Type, Dict, Union, List, Callable
from column_mapping_engine import rank
from faker import Faker
from faker.providers import BaseProvider
from faker.providers.date_time import Provider as DateTimeProvider
from faker.providers.misc import Provider as MiscProvider
from faker.providers.python import Provider as PythonProvider
import faker.proxy
from sqlalchemy.orm import Mapper, RelationshipProperty
try:
    from sqlalchemy.orm import DeclarativeMeta
except ImportError:
    from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy import (
    inspect,
    Column,
    ARRAY,
    BigInteger,
    BINARY,
    Boolean,
    CLOB,
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    Interval,
    JSON,
    LargeBinary,
    Numeric,
    SmallInteger,
    Unicode,
    UnicodeText,
    String,
    Time
)
from sqlalchemy.sql.sqltypes import (
    BOOLEAN,
    VARCHAR)
from faker import Generator

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


def _generate_json(generator: PythonProvider, _: Any) -> Dict[str, Union[str, int, bool, List[PrimitiveJsonTypes], Dict[str, PrimitiveJsonTypes]]]:
    return generator.pydict(
        10,
        True,
        [
            str,
            int,
            bool,
        ],
    )
def _generate_small_bytes(generator: MiscProvider, _: Any) -> bytes:
    return generator.binary(100)
def _generate_uuid(generator: MiscProvider, _: Any) -> bytes:
    return generator.uuid4()
def _generate_null(generator: MiscProvider, _: Any) -> bytes:
    return None
from sqlalchemy.sql.sqltypes import (
    BOOLEAN,
    VARCHAR,
    NullType,
    UUID,
    ARRAY,
    BIGINT,
    DATE,
    DATETIME,
    CHAR,
    DECIMAL,
    FLOAT,
    INTEGER,
    NCHAR,
    SMALLINT,
    TIMESTAMP,
    REAL,
    DOUBLE_PRECISION
    )
from typing import get_type_hints


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

class SqlAlchemyProvider(BaseProvider):
    """Generates instances of models declared with SQLAlchemy's ORM's declarative_base.

    Model instances are generated based on their column types. Generators for custom
    column types may be registered with :meth:`register_type_mapping()`.

    Methods:

    * :meth:`sqlalchemy_model`: Generates an instance of the given model.
    * :meth:`register_type_mapping`: Tell providers which generator to use
      for ``type``.
    """
    MAPPINGS = DEFAULT_MAPPINGS.copy()

    generator: BaseProvider

    MAPPINGS = {}  # assume you fill this with DEFAULT_MAPPINGS elsewhere

    generator: Faker

    def get_all_return_types(self, cls):
        """Collect return type annotations for all functions in a class."""
        results = {}
        for name, member in insp.getmembers(cls, predicate=insp.isfunction):
            try:
                hints = get_type_hints(member)
                ret_type = hints.get("return", insp.signature(member).return_annotation)
            except Exception:
                ret_type = insp.signature(member).return_annotation
            if ret_type is insp._empty:
                ret_type = None
            results[name] = ret_type
        return results
    
    def get_type_to_faker_methods_recordset(self) -> list[Any]:
        """Gets All provider methods from faker proxy, and returns a recordset of {type1:[methodname1,etc]...}

        :return: _description_
        :rtype: list[Any]
        """
        if not hasattr(self, 'faker_methods'):
            self.faker_methods=self.scan_base_class(Faker)
        return [{dt:[k for k, v in self.faker_methods.items() if v == dt]} for dt in list(set(self.faker_methods.values())) if dt and dt not in [Callable]]
           
    @classmethod
    def register_type_mapping(cls, type_, spec):
        cls.MAPPINGS[type_] = spec

    @classmethod
    def reset_type_mappings(cls):
        cls.MAPPINGS = {}

    def scan_base_class(self, cls):
        """Scan the Faker proxy for all provider methods and capture their return types."""
        instance = cls()
        results = {}
        for attr in dir(instance):
            if attr.startswith("_"):
                continue
            try:
                member = getattr(instance, attr)
            except TypeError:
                continue
            if insp.isfunction(member) or insp.ismethod(member):
                print('yay')
                try:
                    hints = get_type_hints(member)
                    ret_type = hints.get("return", insp.signature(member).return_annotation)
                    print(ret_type)
                except Exception:
                    ret_type = insp.signature(member).return_annotation
                if ret_type is insp._empty:
                    ret_type = None
               
                results[member] = ret_type
        return results
    
    def sqlalchemy_model(
            self, model: Type[ModelType], generate_primary_keys=False, generate_related=False, **overrides
    ) -> ModelType:
    
        assert isinstance(model, DeclarativeMeta)
        assert not (generate_primary_keys and generate_related), "`generate_primary_keys` and `generate_related` " \
                                                                 "MUST NOT both be set to True"
        self.inspection: Mapper = inspect(model)
        self.method_map =self.scan_base_class(Faker)

        values = {}
        for column in self.inspection.columns:
            if column.name in overrides:
                values[column.name] = overrides[column.name]
            elif not column.primary_key or generate_primary_keys:
                if not column.foreign_keys:
                    values[column.name] = self.sqlalchemy_column_value(column)

        if generate_related:
            relationship_property: RelationshipProperty
            for key, relationship_property in self.inspection.relationships.items():
                values[key] = self.sqlalchemy_model(
                    relationship_property.mapper.class_, 
                    generate_primary_keys=generate_primary_keys, 
                    generate_related=True
                )

        return model(**values)

    def sqlalchemy_column_value(self, column: Column) -> ColumnType:
        """Creates an instance of a type specified by ``column``.

        :param column: A SQLAlchemy ``Column``
        :return: Returns a value that may be assigned to ``Column`` attributes.
        """

        generator_spec = self._find_generator_spec(column)

        if callable(generator_spec):
            return generator_spec(self.generator, column)
        else:
            return self._find_generator(generator_spec)()
    def _get_col_type(self, column:Column):
        if hasattr(column.type, 'python_type'):
            if column.type.python_type:
                dtype=column.type.python_type
        
        elif hasattr(column.type, 'data_type'):
            if column.type.data_type:
                dtype=column.type.data_type
        else:
            dtype=column.type
        return dtype
    def _get_method_meta(self, method:Callable):
        return {""}
    def _find_generator_spec(self, column: Column):
        dtype = self._get_col_type(column)
        method_list = []
        for k, v in self.method_map.items():
            if v == dtype:
                method_list.append(k)
        if not isinstance(method_list, list):
            return None
        method_list = [method for method in method_list if isinstance(method, Callable)]
        if len(method_list) == 0:
            return None
        elif len(method_list) == 1:
            return method_list[0]
        else:
            method_name_map = {}
            
            for v in method_list:
                classname=v.__self__.__class__.__name__.replace('Provider','')
                if classname != '':
                    name=f"{v.__class__} {v.__name__}"
                else:
                    name=v.__name__
                method_name_map[name]=v
            ranks=rank(list(method_name_map.keys()),column.name)
            if ranks[1] < 0.75:
                pass
            print(method_name_map)
        # raise ValueError(f"Unmapped column type found for column: {column}")

    def _find_generator(self, generator_spec):
        if hasattr(self.generator, generator_spec):
            return getattr(self.generator, generator_spec)
        else:
            return getattr(self, generator_spec)
if __name__ == '__main__':
    from sqlalchemy import create_engine, MetaData, Table
    from sqlalchemy.orm import registry
    fake = Faker()
    fake.add_provider(SqlAlchemyProvider)
    # Connect to the foreign DB
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/Adventureworks")

    metadata_obj = MetaData()

    person = Table(
        "person",
        metadata_obj,
        autoload_with=engine,
        schema='person'
    )
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()
    class Person(Base):
        __table__ = person
        Base
    instance = fake.sqlalchemy_model(Person)
    v = instance.value
    print(v)