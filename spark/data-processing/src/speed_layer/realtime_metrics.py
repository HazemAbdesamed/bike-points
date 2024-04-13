from pyspark.sql.functions import sum

def nb_available_bikes(df):
    return df.agg(sum("NbBikes")).first()[0]

def percentage_available_bikes(df):
    return round(
        df.agg(
        (sum("NbBikes") / sum("NbDocks") * 100)
    ).first()[0]
    , 2)

def nb_InUse_bikes(df):
    return df.agg(
        sum("NbEmptyDocks") - sum("NbBrokenDocks")
    ).first()[0]

def percentage_InUse_bikes(df):
    return round(
        df.agg(
        (sum("NbEmptyDocks") - sum("NbBrokenDocks") / sum("NbDocks") * 100)
    ).first()[0]
    , 2)

def nb_broken_docks(df):
    return df.agg(
        sum("NbBrokenDocks")
    ).first()[0]

def percentage_broken_docks(df):
    return round(
        df.select(
        (sum("NbBrokenDocks") / sum("NbDocks") * 100)
    ).first()[0]
    , 2)
