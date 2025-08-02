# oopsies
Oopsies! A library for creating trackable data quality issues on pandas dataframes in python. 

There's a mountain of libraries out there for validating data, but not invalid data for testing! One of the greatest painpoints for data engineers and etl developers is creating data to test new code with. Oftentimes, I find myself manually messing up data in order to test error handling. Therefore, I want a repeatable, trackable way to create "bad data", and automatically ensure my test cases cover that data.

Planned features:

- Dataclass to bad data: make data have issues relevant to your requirements. This will be a duckdb table, which will be fed into the bad data engine to mess up your data.

        import oopsies
        import pydantic

        class User():
            id: int not null
            name: nvarchar(35) encoding ascii not null check constrain <> ''
            joined_on: date('yyyy-mm-dd') not null
            balance: float not null
        
        df = pd.read_csv('user.csv')
        oopsframe = oopsies.Oops(df, User)
        oopsframe

this returns the freshly mangled dataframe. But what issues were created? We can get the "oops info" with oopsframe.info

[{
    "column":"id"
    "definition": User.id
    "issue": "Null",
    "violates": "Not Null",
    "value": None
},
{"column": "name",
"
}]

or add it to it's own "info" column to the oopsframe like this:

oopsframe = oopsies.Oops(df, User, info=True)


By default, all rows and all fields of your data will now include issues, but this can be adjusted. To mess up a random 50% of your rows:

    oopsframe = oopsies.Oops(df, User, percent=.5)

or 5 rows at the top or bottom of the dataset:

    oopsframe = oopsies.Oops(df, User, num_rows=5, align='top')

sequentially mess up 1 field per row like this:

    oopsframe = oopsies.Oops(df, User, seq=True, align='bottom')

