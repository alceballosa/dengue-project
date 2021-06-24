
from statsmodels.tsa.seasonal import seasonal_decompose

def within_maximum_range(val, max_val, thres = 0.020):
    val = abs(val)
    max_val = abs(max_val)
    diff = abs(val-max_val)
    if diff < thres:
        return True
    else:
        return False
    
def normalize_timeseries(df, mode = "MES", cols_to_normalize = []):
    df_norm = df[cols_to_normalize].copy()
    if mode == "NO":
        return df_norm, None, None
    elif mode == "MES":
        df_norm["MES"] = df_norm.index.month
        promedios_mensuales = df_norm.groupby("MES").mean()
        desv_esta_mensuales = df_norm.groupby("MES").std()
        prom = promedios_mensuales.values[:,0:]
        std = desv_esta_mensuales.values[:,0:]
        for i in range(len(df)):
            mes = int(df_norm.iloc[i,:].MES - 1)
            for j, col in enumerate(df_norm.columns[:-2]):
                df_norm.iloc[i,j] = (df_norm.iloc[i,j]-prom[mes,j])/std[mes,j]
        return df_norm, promedios_mensuales, desv_esta_mensuales
    elif mode == "SEASONAL_DECOMPOSE":
        df_norm = df[cols_to_normalize].copy()
        for col in cols_to_normalize[:-2]:
            decomposed = seasonal_decompose(df[col].dropna(),model='additive', period = 52)
            df_norm[col] = decomposed.resid+decomposed.trend
        df_norm = df_norm.dropna()
        return df_norm, None, None
    
def lagged_corr(df, weeks, var, window):
    return df[str(var)].shift(periods=weeks).iloc[weeks:].corr(df['DENGUE_PER_100K'].iloc[weeks:], min_periods=window, method = "pearson")    

