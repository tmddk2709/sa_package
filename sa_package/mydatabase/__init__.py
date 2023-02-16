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


def upload_df(dbms:str, engine, df, pk_list:list, scheme:str, table:str):

    """
    Parameter
    -----------
    dbms : {"mysql", "postgres"}

    engine

    df : pd.DataFrame()

    pk_list : list of str

    scheme : str

    table : str
    """

    copy_df = df.copy()
    
    # NaN 값 처리
    copy_df.fillna("", inplace=True)
    for col in copy_df.columns:
        if copy_df[col].dtypes in ['float64', 'int64', "Int64"]:
            copy_df[col] = copy_df[col].astype(str)    
            
    copy_df = copy_df.replace("<NA>", "")

    for col in copy_df.columns:
        copy_df[col] = copy_df[col].apply(lambda x: None if x == "" else str(x))

    if dbms == "mysql":
        cols = ', '.join('`{0}`'.format(c) for c in copy_df.columns)
        strings = ', '.join('%s' for i in copy_df.columns)
        update_values = ', '.join('`{0}`=VALUES(`{0}`)'.format(c) for c in copy_df.drop(columns=pk_list).columns)
        values = list(copy_df.itertuples(index=False, name=None))

        sql = "INSERT INTO `" + scheme + "`.`" + table + "` ({0}) VALUES({1}) ON DUPLICATE KEY UPDATE {2};".format(cols, strings, update_values)

    elif dbms == "postgres":
        cols = ', '.join('"{0}"'.format(c) for c in copy_df.columns)
        strings = ', '.join('%s' for i in copy_df.columns)
        pk_values = ', '.join('"{0}"'.format(c) for c in pk_list)
        update_values = ', '.join('"{0}"=EXCLUDED."{0}"'.format(c) for c in copy_df.drop(columns=pk_list).columns)
        values = list(copy_df.itertuples(index=False, name=None))

        sql = 'INSERT INTO ' + scheme + '."' + table + '" ({0}) VALUES({1}) ON CONFLICT ({2}) DO UPDATE SET {3};'.format(cols, strings, pk_values, update_values)
    
    else:
        raise ValueError("dbms 명이 잘못되었습니다")

    try:
        with engine.connect() as connection:
            connection.execute(sql, values)

        return True

    except Exception as e:
        print(e)
        return False
