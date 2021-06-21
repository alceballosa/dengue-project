import glob
import itertools
import os
from datetime import datetime
from itertools import chain

import chart_studio.plotly as py
import matplotlib.pyplot as plt
import missingno as msno
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge
from xgboost import XGBRegressor

WEEKS_YEAR = {2019: 52, 2020: 53, 2021: 12}


#####################
# GENERAL FUNCTIONS #
#####################
def re_assert_cod_datatypes(df):
    dtypes = {
        "COD_DPTO": "object",
        "COD_MUNICIPIO": "object",
        "SEMANA": "object",
        "ANO": "object",
        "DENGUE": "UInt16",
        "DENGUE GRAVE": "UInt16",
        "MORTALIDAD POR DENGUE": "UInt8",
        "CODIGOESTACION": "object",
    }
    for col in df.columns:
        if col in dtypes.keys():
            df[col] = df[col].astype(dtypes[col])
            if col == "SEMANA" or col == "COD_DPTO":
                df[col] = df[col].apply(lambda x: str(int(x)).zfill(2))
    return df


def get_sivigila_calendar():
    date = pd.to_datetime("2006-01-01")
    week = 1
    weeks = []
    year = 2006
    sivigila_53_years = [2008, 2014, 2020]
    day = 1
    while year < 2022:
        if week == 53:
            if not (year in sivigila_53_years):
                year += 1
                week = 1

        elif week > 53:
            year += 1
            week = 1
        # if day == 1:
        #    year = date.year
        weeks.append((date, year, week))
        day += 1
        if day == 8:
            week += 1
            day = 1
        date += pd.DateOffset(days=1)
    columns = ["FECHA", "ANO", "SEMANA"]
    df_weeks = pd.DataFrame(weeks, columns=columns)
    df_weeks = df_weeks.set_index("FECHA")
    df_weeks = re_assert_cod_datatypes(df_weeks)
    return df_weeks


####################
# DENGUE FUNCTIONS #
####################


def unify_column_names_dengue(columns):
    new_columns = []
    for col in columns:
        if "evento" == col.lower():
            new_columns.append("NOMBRE")
        elif "cod_e" in col.lower():
            new_columns.append("COD_EVE")
        elif "cod_d" in col.lower():
            new_columns.append("COD_DPTO")
        elif "cod_m" in col.lower():
            new_columns.append("COD_MUNICIPIO")
        elif "dato" in col.lower() or "conteo" in col.lower():
            new_columns.append("TOTAL_CASOS")
        else:
            new_columns.append(col.upper())
    return new_columns


def get_dengue_weeks_from_rutinaria(filename, codes, sheet_num, year):
    df = pd.read_excel(filename, sheet_name=sheet_num)
    df.columns = unify_column_names_dengue(list(df.columns))
    df["ANO"] = year
    df = df[~df["COD_DPTO"].isin([0, 1])]
    df = df[df.COD_EVE.isin(codes)]
    df_pivoted = df.pivot_table(
        values="TOTAL_CASOS",
        columns="NOMBRE",
        index=["ANO", "COD_DPTO", "COD_MUNICIPIO", "SEMANA"],
    ).reset_index()

    return df_pivoted


def read_all_rutinarias(codes=[210, 220, 580]):
    dfs = []
    for year in range(2007, 2019):
        print("Doing year ", year)
        filename = "local/data/src_general/rutinarias_dengue/rutinaria_{}.xlsx".format(
            year
        )
        df = get_dengue_weeks_from_rutinaria(filename, codes, sheet_num=3, year=year)
        df = re_assert_cod_datatypes(df)

        dfs.append(df)
    df = pd.concat(dfs)
    df.columns.name = None
    return re_assert_cod_datatypes(df)


def get_time_series_from_municipio_subset(subset_mun, event_col_n, cod_eve, year):
    try:
        series_index = get_index_from_col_and_string(
            subset_mun, subset_mun.columns[event_col_n], cod_eve
        )
        series = list(subset_mun.loc[series_index, :][6:])
    except Exception as e:
        series = [0] * WEEKS_YEAR[year]
    return series


def get_index_from_col_and_string(df, col, string):
    return df[df.loc[:, col] == string].index[0]


def dataframe_from_dengue_series(series, value_name, year):
    cols = ["ANO", "COD_DPTO", "COD_MUNICIPIO"] + [
        str(i) for i in range(1, WEEKS_YEAR[year] + 1)
    ]

    df = pd.DataFrame(series).transpose()
    df.columns = cols
    df = pd.melt(
        df,
        id_vars=["ANO", "COD_DPTO", "COD_MUNICIPIO"],
        var_name="SEMANA",
        value_name=value_name,
    )
    return df


####################
# CITIES FUNCTIONS #
####################


def get_composite_city_code(x):
    composite_code = str(x["COD_DPTO"]).zfill(2) + str(x["COD_MUNICIPIO"]).zfill(3)
    x["COD_MUNICIPIO"] = composite_code
    return x


def combine_cities_and_weeks(df_weeks, df_cities):
    dfs_week_city = []
    for city in df_cities.iterrows():
        df_week_city = df_weeks.copy()
        df_week_city["COD_MUNICIPIO"] = city[1][1]
        df_week_city["COD_DPTO"] = city[1][0]
        dfs_week_city.append(df_week_city)
    res = pd.concat(dfs_week_city, axis=0)
    return res


def combine_cities_weeks_and_dengue(df_weeks_cities, df_dengue):
    den_columns = [
        "ANO",
        "SEMANA",
        "COD_DPTO",
        "COD_MUNICIPIO",
        "DENGUE",
        "DENGUE GRAVE",
        "MORTALIDAD POR DENGUE",
    ]
    res = pd.merge(
        left=df_weeks_cities.reset_index(),
        right=df_dengue[den_columns],
        how="left",
        on=["ANO", "SEMANA", "COD_MUNICIPIO"],
        suffixes=("", "_y"),
    )

    res = res.drop(res.filter(regex="_y$").columns.tolist(), axis=1)
    res = res.set_index("FECHA")
    return res


def read_csv_IDEAM(filenames, sep=r";|,"):
    """
    This function receives a list of .csv files downloaded from
    http://dhime.ideam.gov.co/atencionciudadano/
    and combines information into a single pandas dataframe by keeping only the date
    and the relevant data column.

    -filenames: list of one or more filenames of .csv files.
    -codigo_estacion: the code of the station we are interested in.
    -sep: the kind of separation used for pd.read_csv, it is good to try and
            switch between ; and , if there is any trouble since
            not all files downloaded from IDEAM have the same separator.

    returns: a dataframe with the datetime column as it index, and the V
    """
    dfs = []
    for filename in filenames:
        dfs.append(
            pd.read_csv(
                filename,
                sep,
                dtype={"Calificador": "object", "Latitud": "object"},
                engine="python",
            )
        )
    if len(dfs) > 0:
        df = pd.concat(dfs, axis=0).reset_index(drop=True)
    else:
        df = dfs[0]
    return df


def get_variable_IDEAM(df, possible_var_names, standard_var_name, codigo_estacion=None):
    df = df[df["Etiqueta"].isin(possible_var_names)].reset_index(drop=True)
    # value_name = df.loc[0, "Etiqueta"]
    if codigo_estacion:
        df = df[(df["CodigoEstacion"] == codigo_estacion)]
    df = df[["CodigoEstacion", "Fecha", "Valor"]]
    df.columns = ["CodigoEstacion", "DATE", standard_var_name]
    df.index = pd.to_datetime(df["DATE"], dayfirst=False)
    df = df.drop_duplicates()
    del df["DATE"]
    return df


def filter_entries_by_column_index_values(df, column_name, min_val=None, max_val=None):
    if min_val and max_val:
        df = df[(df[column_name] >= min_val) & (df[column_name] <= max_val)]
        return df
    elif not min_val:
        df = df[(df[column_name] <= max_val)]
        return df
    elif not max_val:
        df = df[(df[column_name] >= min_val)]
        return df
    else:
        return df


def combine_IDEAM_stations(df_all, stations_priority):
    df_st = df_all[df_all["CodigoEstacion"] == stations_priority[0]]
    if len(df_all) == 1:
        return df_st
    for station in stations_priority[1:]:
        df_st_add = df_all[df_all["CodigoEstacion"] == station]
        df_st_add = df_st_add[(~df_st_add.index.isin(df_st.index))]
        df_st = pd.concat([df_st, df_st_add])
    del df_st["CodigoEstacion"]
    return df_st


def aggregate_data(
    df,
    agg_type="daily",
    aggregations=[np.mean, np.max, np.min, "count"],
    min_count=None,
):
    if agg_type == "daily":
        df_aggregated = df.groupby([df.index.date]).agg(aggregations)
        df_aggregated.columns = ["_".join(x).upper() for x in df_aggregated.columns]
        if min_count:
            df_aggregated = df_aggregated[(df_aggregated.iloc[:, -1] >= min_count)]
        df_aggregated.index = pd.to_datetime(df_aggregated.index)
    return df_aggregated.iloc[:, :-1]


def drop_duplicates_by_date_station(df):
    df = df.reset_index()
    df = df.drop_duplicates(subset=["DATE", "CodigoEstacion"])
    df = df.set_index("DATE")
    return df


def highlight_max(s):
    """
    highlight the maximum in a Series coral.
    """
    is_max = s == s.max()
    return ["background-color: coral" if v else "" for v in is_max]


def imput_data_with_closest_and_mean(df_daily):
    df_monthly_averages = df_daily[
        [
            "PRECIPITATION",
            "TEMPERATURE_MEAN",
            "TEMPERATURE_AMAX",
            "TEMPERATURE_AMIN",
            "REL_HUMIDITY_MEAN",
            "REL_HUMIDITY_AMAX",
            "REL_HUMIDITY_AMIN",
        ]
    ]
    df_monthly_averages = df_monthly_averages.groupby(
        df_monthly_averages.index.month
    ).mean()
    df_to_interpolate = df_daily[
        [
            "PRECIPITATION",
            "TEMPERATURE_MEAN",
            "TEMPERATURE_AMAX",
            "TEMPERATURE_AMIN",
            "REL_HUMIDITY_MEAN",
            "REL_HUMIDITY_AMAX",
            "REL_HUMIDITY_AMIN",
        ]
    ].isna()
    df_daily_interp = df_daily.interpolate(method="nearest")
    for col in df_monthly_averages:
        for idx in df_daily_interp.index:
            value = df_to_interpolate.loc[idx, col]
            if value == True:
                month = idx.month
                df_daily_interp.loc[idx, col] = (
                    df_monthly_averages.loc[month, col] + df_daily_interp.loc[idx, col]
                ) / 2
    return df_daily_interp


def imput_with_mean_of_week(df_weekly):
    df_weekly_averages = df_weekly[
        [
            "SEMANA",
            "PRECIPITATION",
            "TEMPERATURE_MEAN",
            "TEMPERATURE_AMAX",
            "TEMPERATURE_AMIN",
            "REL_HUMIDITY_MEAN",
            "REL_HUMIDITY_AMAX",
            "REL_HUMIDITY_AMIN",
        ]
    ]
    df_weekly_averages = df_weekly_averages.groupby("SEMANA").mean()
    df_to_interpolate = df_weekly[
        [
            "SEMANA",
            "PRECIPITATION",
            "TEMPERATURE_MEAN",
            "TEMPERATURE_AMAX",
            "TEMPERATURE_AMIN",
            "REL_HUMIDITY_MEAN",
            "REL_HUMIDITY_AMAX",
            "REL_HUMIDITY_AMIN",
        ]
    ].isna()
    df_weekly_imputed = df_weekly.copy()
    for col in df_weekly_averages.columns[1:]:
        for idx in df_weekly_imputed.index:
            value = df_to_interpolate.loc[idx, col]
            if value == True:
                week = df_weekly_imputed.loc[idx, "SEMANA"]
                df_weekly_imputed.loc[idx, col] = df_weekly_averages.loc[week, col]
    return df_weekly_imputed


def imput_data_with_sklearn_imputer(df_daily):

    df_daily_interp = df_daily.copy()
    df_daily_interp["MES"] = df_daily_interp.index.month
    imputer = IterativeImputer(estimator=BayesianRidge(), random_state=1)
    imputer.fit(df_daily_interp.values)
    imputted_vals = imputer.transform(df_daily_interp.values)
    df_daily_interp.loc[:, :] = imputted_vals
    return df_daily_interp


def imput_with_wind_mean_of_week(df_weekly):
    imput_cols = [
        "ANO",
        "SEMANA",
        "PRECIPITATION",
        "TEMPERATURE_MEAN",
        "TEMPERATURE_AMAX",
        "TEMPERATURE_AMIN",
        "REL_HUMIDITY_MEAN",
        "REL_HUMIDITY_AMAX",
        "REL_HUMIDITY_AMIN",
    ]
    windowed_weekly_averages = {}
    for year in df_weekly["ANO"].unique():
        windowed_weekly_averages[year] = (
            df_weekly[imput_cols]
            .query(f"ANO >= {year-1} & ANO <= {year+1}")
            .groupby("SEMANA")
            .mean()
        )
    df_to_imput = df_weekly[imput_cols].isna()
    df_weekly_imputed = df_weekly.copy()
    for col in imput_cols[2:]:
        for idx in df_weekly_imputed.index:
            value = df_to_imput.loc[idx, col]
            if value:
                week = df_weekly_imputed.loc[idx, "SEMANA"]
                year = df_weekly_imputed.loc[idx, "ANO"]
                df_weekly_imputed.loc[idx, col] = windowed_weekly_averages[year].loc[
                    week, col
                ]
    return df_weekly_imputed

def municipality_name_to_filename(name):
    name = name.lower()
    name = name.replace(" ","_")
    name = name.replace("á","a")
    name = name.replace("ó","o")
    name = name.replace("í","i")
    name = name.replace("ú","u")
    return name
