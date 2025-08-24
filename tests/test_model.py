import pytest
from fixtures import *
import pytest
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import declarative_base
from oopsies.faker_sqlalchemy import SqlAlchemyProvider
from faker import Faker
fake = Faker()
fake.add_provider(SqlAlchemyProvider)
metadata_obj = MetaData()

def test_model_instance(person_table):
    instance = fake.sqlalchemy_model(person_table)
    assert instance is not None
    assert hasattr(instance, "__table__") or hasattr(instance, "__mapper__")
    
def test_model_field_names(person_field_names, person_table):
    instance = fake.sqlalchemy_model(person_table)
    column_names = [c.key for c in inspect(instance).mapper.column_attrs]
    assert person_field_names == column_names