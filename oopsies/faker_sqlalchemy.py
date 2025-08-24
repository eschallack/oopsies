from typing import TypeVar, Type, Union, Callable
from oopsies.column_mapping_engine import rank
from faker import Faker
from faker.providers import BaseProvider
from sqlalchemy.orm import Mapper
try:
    from sqlalchemy.orm import DeclarativeMeta
except ImportError:
    from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy import inspect, Column
from oopsies.type_interpreter import TypeInterpreter, DEFAULT_MAPPINGS

ModelType = TypeVar("ModelType")
ColumnType = TypeVar("ColumnType", bound=TypeEngine)
PrimitiveJsonTypes = Union[str, int, bool, None]
GeneratorFunction = Callable[
    [Faker, Column], Column
]
GeneratorSpec = Union[str, GeneratorFunction]


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
           
    @classmethod
    def register_type_mapping(cls, type_, spec):
        cls.MAPPINGS[type_] = spec

    @classmethod
    def reset_type_mappings(cls):
        cls.MAPPINGS = {}
    
    def sqlalchemy_model(
            self, model: Type[ModelType], generate_primary_keys=False, generate_related=False, **overrides
    ) -> ModelType:
    
        assert isinstance(model, DeclarativeMeta)
        assert not (generate_primary_keys and generate_related), "`generate_primary_keys` and `generate_related` " \
                                                              "MUST NOT both be set to True"
        self.inspection: Mapper = inspect(model)
        self.faker_instance = Faker()
        self.method_map = TypeInterpreter.scan_base_class(Faker)
        values = {}
        for column in self.inspection.columns:
            if column.name in overrides:
                values[column.name] = overrides[column.name]
            elif not column.primary_key or generate_primary_keys:
                if not column.foreign_keys:
                    values[column.name] = self.sqlalchemy_column_value(column)

        # if generate_related:
        #     relationship_property: RelationshipProperty
        #     for key, relationship_property in self.inspection.relationships.items():
        #         values[key] = self.sqlalchemy_model(
        #             relationship_property.mapper.class_, 
        #             generate_primary_keys=generate_primary_keys, 
        #             generate_related=True
        #         )
        return model(**values)

    def sqlalchemy_column_value(self, column: Column) -> ColumnType:
        """Creates an instance of a type specified by ``column``.
        :param column: A SQLAlchemy ``Column``
        :return: Returns a value that may be assigned to ``Column`` attributes.
        """
        generator_spec, kwargs = self._find_generator_spec(column)
        if callable(generator_spec):
            return generator_spec(**kwargs)
        else:
            return None
        
    def _create_method_name_map_with_provider_name(self, methods:list[Callable]) -> None:
        self.method_name_map = {}
        for method in methods:
            classname=method.__self__.__class__.__name__.replace('Provider','')
            if classname != '':
                metaname=f"{method.__class__} {method.__name__}"
            else:
                metaname=method.__name__
            self.method_name_map[metaname]=method.__name__
            
    def _rank_method_column_cosine_similarity(self, methods:list[Callable], column:Column) -> list[Callable]:
        self._create_method_name_map_with_provider_name(methods)
        return rank(list(self.method_name_map.keys()),column.name)
    
    def _filter_methods_by_return_type(self, dtype) -> list[str|None]:
        method_list = []
        for k, v in self.method_map.items():
            if v == dtype:
                method_list.append(k)
        if not isinstance(method_list, list):
            return None
        return [method for method in method_list if isinstance(method, Callable)]
    
    def _find_generator_spec(self, column: Column):
        # first, we should handle values that are effectively enums.
        # we need to identify all types which effectively function like enums
        return_type = TypeInterpreter._get_col_type(column)
        methods=self._filter_methods_by_return_type(return_type)
        if len(methods) == 0:
            method=None
        elif len(methods) == 1:
            method=methods[0]
        else:
            ranks = self._rank_method_column_cosine_similarity(methods,column)
            method_name=self.method_name_map[ranks[0][0]]
            method = getattr(self.faker_instance, method_name)
        return method, {}