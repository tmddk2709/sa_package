import pandas as pd
from sqlalchemy import create_engine


def get_engine(dbms:str, username:str, password:str, host:str, port:int, database:str):

    """
    Parameter
    ----------
    dbms : {"mysql", "postgres"}
    """

    assert dbms in ["mysql", "postgresql"], "available dbms values are mysql and postgresql only"

    if dbms == "mysql":
        scheme = "mysql+pymysql"
        
    elif dbms == "postgresql":
        scheme = f"postgresql"
        
    connection_url = f"{scheme}://{username}:{password}@{host}:{port}/{database}"
    
    engine = create_engine(url=connection_url)

    return engine


# def upload_df(df:)