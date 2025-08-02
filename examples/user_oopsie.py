import duckdb
import oopsies
if __name__ == '__main__':
    con = duckdb.connect()
    con.execute("CREATE TABLE users (id INTEGER NOT NULL, name VARCHAR NOT NULL, balance DOUBLE, joined_on DATE NOT NULL);")
    con.execute("INSERT INTO users VALUES (1, 'Alice', 100.0, '2020-01-01'), (2, 'Bob', 200.0, '2020-02-01')")
    # print(con.query(f"PRAGMA table_info('users')").to_df())
    # Get schema info
    
    oopsframe = oopsies.Oops('users',con)
    print(oopsframe)
    print(oopsframe.info)