import pandas as pd
import numpy as np
import redis
import glob
import os


# Open a connection to Redis
rcache = redis.StrictRedis(host='localhost', port=6379, db=0)


def translate_values(df, column_name, old_value, new_value):
    new_col = df[column_name].replace(old_value, new_value)
    return new_col


TRANSLATION_TABLE = {
    'Agency size': [
        ('Small agencies', 'Small agencies')
    ]
}


def build_all_data_df(source_dir='../data/raw'):
    """ Loads the raw CSV data into a dataframe """
    if rcache.exists('raw_df'):
        raw_df = pd.read_msgpack(rcache.get('raw_df'))
    else:
        input_files = glob.glob(os.path.join(source_dir, 'financial_year_*.*'))
        raw_df = pd.DataFrame()
        for inf in input_files:
            if inf.endswith('.xlsx'):
                df = pd.read_excel(inf, encoding='ISO-8859-1')
                df['Financial year'] = inf.split('.xlsx')[0].split('year_')[1]
            elif inf.endswith('.csv'):
                df = pd.read_csv(inf, encoding='ISO-8859-1')
                df['Financial year'] = inf.split('.csv')[0].split('year_')[1]
            raw_df = pd.concat([raw_df, df])
            raw_df = clean_raw_dataframe(raw_df)
        rcache.set('raw_df', raw_df.to_msgpack(compress='zlib'))
    return raw_df


def clean_raw_dataframe(raw_df):
    # Remove leading and trailing spaces in column names
    raw_df = raw_df.rename(columns=lambda x: x.strip())
    for colname in ['Total cost', 'Primary unit rate']:
        if raw_df[colname].dtype != float:
            # Clean up this column so that the values can be parsed as float
            raw_df[colname] = raw_df[colname].str.replace(',', '')
            raw_df[colname] = raw_df[colname].str.replace(' -   ', '')
            raw_df[colname] = raw_df[colname].replace(r'^\s*$', np.nan, regex=True)
            raw_df[colname] = raw_df[colname].astype(float)

    # Translate values
    for col, trans_rows in TRANSLATION_TABLE.items():
        for old, new in trans_rows:
            raw_df[col] = translate_values(raw_df, col, old, new)

    return raw_df

def build_wog_overview1_df(raw_df, use_cache=True):
    """ Generates the dataframe for the WoG overview graph """
    sdf = raw_df.loc[:,['Agency name', 'Service classification', 'Service name', 'Service type', 'Total cost', 'Total ASL', 'Financial year', 'Agency size']]
    sdf.dropna(how='any', inplace=True)
    sdf = sdf.groupby(['Agency name', 'Service classification', 'Service name', 'Service type', 'Financial year', 'Agency size']).aggregate({'Total cost': 'sum', 'Total ASL': 'sum'})
    sdf.reset_index(inplace=True)
    sdf.rename(columns={'Financial year': 'Financial Year', 'Total cost': 'Sum of Total', 'Total ASL': 'Sum of ASL'}, inplace=True)

    if use_cache:
        if not rcache.exists('wog_overview_1'):
            rcache.set('wog_overview_1', sdf.to_msgpack(compress='zlib'))

    return sdf


def build_wog_overview2_df(raw_df, use_cache=True):
    """ Generates the dataframe for the WoG overview graph """
    columns = ['Agency name', 'Financial year', 'Service classification',
        'Service name', 'Service type', 'Cost category', 'Primary unit of measure', 'Primary service volume', 'Primary unit rate', 'Agency size', 'Total cost', 'Total ASL']
    sdf = raw_df.loc[:, columns]
    sdf.dropna(how='any', inplace=True)
    sdf.rename(columns={'Financial year': 'Financial Year'}, inplace=True)

    if use_cache:
        if not rcache.exists('wog_overview_2'):
            rcache.set('wog_overview_2', sdf.to_msgpack(compress='zlib'))

    return sdf


def build_dataframes():
    raw_df = build_all_data_df()
    build_wog_overview1_df(raw_df)
    build_wog_overview2_df(raw_df)