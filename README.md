# dbfaker
dbfaker is a library for quickly generating test data for any database in python. Create a sqlalchemy class for your table, and get high quality test data generated on the fly.

Planned features:

- Infers complex types automatically, no need to specify! For example, say you have a table:
CREATE TABLE Person(
    BusinessEntityID INT NOT NULL,
    Title varchar(8) NULL,
    FirstName "Name" NOT NULL,
    MiddleName "Name" NULL,
    LastName "Name" NOT NULL,
    Suffix varchar(10) NULL
  )





*All example tables are from the Adventureworks 2014 Database*