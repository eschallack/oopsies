import duckdb
import pandas as pd
from oopsies.engine import StrategyRegistry, OopsStrategy, registry
        
class Oops():
    df:pd.DataFrame
    oopsframe:pd.DataFrame = pd.DataFrame()
    info:pd.DataFrame = pd.DataFrame()
    _schema_info:pd.DataFrame
    _registry:StrategyRegistry=registry
    
    def __init__(self, 
                 table:str,
                 conn:duckdb.DuckDBPyConnection,
                 num_rows:int| None=None, 
                 percent:float=1,
                 align:str='top',
                 seq:bool=False) -> None:
        """ The entrypoint for making mistakes!

        :param table: The name of the duckdb table to mess up
        :type table: str
        :param conn: a duckdb connection
        :type conn: duckdb.DuckDBPyConnection
        :param num_rows: The number of rows to cause errors in, defaults to None
        :type num_rows: int | None, optional
        :param percent: the percentage of rows where mistakes should occur, defaults to 1
        :type percent: float, optional
        :param seq: row 1 has an error in column 1, row 2 has error in column 2, and so on. this sequence repeats for the num_rows specified.
        :type seq: bool, optional
        :param align: choose where the fixed rowset starts from - 'top' and 'bottom' are accepted values, defaults to 'top'
        :type align: str, optional
        """
        self.__setattr__('df',conn.query(f"select * from {table}").to_df())
        self.__setattr__('_schema_info',conn.query(f"PRAGMA table_info('{table}')").to_df())
        self._generate_bad_data()
    def __repr__(self):
        return repr(self.oopsframe)
    def __str__(self) -> str:
        return str(self.oopsframe)
    def _generate_bad_data(self):
        self.oopsframe = self.df.copy()
        
        # Prepare a list for each row to store its oopsies
        row_issues = [[] for _ in range(len(self.oopsframe))]

        for _, row in self._schema_info.iterrows():
            col = row['name']
            dtype = row['type']
            nullable = not row['notnull']
            strategy: OopsStrategy = self._registry.get(dtype, nullable)

            if strategy:
                original_col = self.oopsframe[col].copy()
                corrupted_col = strategy.apply(original_col)

                self.oopsframe[col] = corrupted_col
                for idx, (orig, corr) in enumerate(zip(original_col, corrupted_col)):
                    if orig != corr:
                        row_issues[idx].append({
                            "column": col,
                            "original_value": orig,
                            "corrupted_value": corr,
                            "issue": strategy.__class__.__name__,
                            "violates": "nullability" if not nullable else "datatype"
                        })
        self.oopsframe["_oops_info"] = row_issues
        self.info = pd.DataFrame([
            issue for row in row_issues for issue in row
        ])
    def register_oopsie(self):
        return
