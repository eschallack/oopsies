import pytest
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import declarative_base
from oopsies.faker_sqlalchemy import SqlAlchemyProvider
from faker import Faker
fake = Faker()
fake.add_provider(SqlAlchemyProvider)
metadata_obj = MetaData()


@pytest.fixture(scope='package')
def engine():
    return create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/Adventureworks")

@pytest.fixture
def person_table(engine):
    """Return a single fake Person instance (not committed to a real DB)."""
    Base = declarative_base()
    person = Table(
        "person",
        metadata_obj,
        autoload_with=engine,
        schema='person'
    )
    class Person(Base):
        __table__ = person
        Base
    return Person

@pytest.fixture
def person_field_names():
    return ["businessentityid",
    "persontype",
    "namestyle",
    "title",
    "firstname",
    "middlename",
    "lastname",
    "suffix",
    "emailpromotion",
    "additionalcontactinfo",
    "demographics",
    "rowguid",
    "modifieddate"]
