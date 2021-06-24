"""
fig, axes = plt.subplots(4,2, figsize=(12,12), dpi = 250)
axes = axes.flatten()
vars_to_plot = ["TEMPERATURE_MEAN","REL_HUMIDITY_MEAN","MEI","ONI","SST3.4","TNI","NTA","CAR"]
xlabels  = ["Mean temperature (°C)","Rel. humidity (%)", "MEI", "ONI", "SST3.4 (°C)", "TNI","NTA","CAR"]
colors = list(mcolors.get_named_colors_mapping().keys())[99:107]
for i,var in enumerate(vars_to_plot):
    sns.regplot(x = df[var], y = df["DENGUE"], ax = axes[i], color = colors[i])
    axes[i].set_title("Scatterplot of "+xlabels[i]+" vs Dengue cases in " + municipality)
    axes[i].set_ylabel("cases")
    axes[i].set_xlabel(xlabels[i])
plt.tight_layout()
"""

"""def obtener_conjunto_desfasado(datos,meses_desfase):
    dat_desfase = datos.copy().reset_index(drop=True)
    for i in range(len(dat_desfase)-meses_desfase):
        dat_desfase.loc[i,"DENGUE_UNPHASED"] = dat_desfase.loc[i+meses_desfase,"DENGUE"]
    quitar_filas = list(range(len(dat_desfase)-meses_desfase,len(dat_desfase)))
    dat_desfase= dat_desfase.drop(dat_desfase.index[quitar_filas])
    return dat_desfase
phases_confirmed

df_for_corr_2 = df_for_corr[cols_to_correlate]
phases = [obtener_conjunto_desfasado(df_for_corr_2, i).corr(method='pearson').iloc[:,-1:] for i in range(24)]
phases_confirmed = pd.concat(phases, axis = 1)

fig, ax = plt.subplots(1,1, figsize=(24,8), dpi = 150)
sns.heatmap(phases_confirmed, annot = True, ax = ax)
ax.set_xlabel("Lag in weeks with respect to Dengue cases")
ax.set_title("Lagged correlations heatmap ({})".format(municipality))
ax.set_ylabel("Covariate");
""";

"""
df_filt = df[(df["ANO"]>=2007) & (df["ANO"]<=2019)]
x_array = [df_filt["ANO"]]*4
y_array = [df_filt["TEMPERATURE_MEAN"], df_filt["TEMPERATURE_AMIN"],df_filt["TEMPERATURE_AMAX"] , df_filt["TEMPERATURE_RANGE"]]
labels_array = ["Mean Temp.", "Min. Temp.", "Max. Temp." , "Temp. Range"]
colors = ["forestgreen","darkblue","orangered","black"]
title = "Temperature over the years for " + municipality
ylabel = "°C"
xlabel = "Date"
plot_time_series(x_array, y_array, labels_array,colors,title,  xlabel,ylabel, "lineplot")
""";

"""x_array = [df.index]*3
y_array = [df["REL_HUMIDITY_MEAN"], df["REL_HUMIDITY_AMIN"],df["REL_HUMIDITY_AMAX"] ]
labels_array = ["Mean Rel. Hum.", "Min. Rel. Hum.", "Max. Rel. Hum."]
title = "Weekly humidity over the years for " + municipality
colors = ["forestgreen","darkblue","orangered"]
ylabel = "%"
xlabel = "Date"
plot_time_series(x_array, y_array, labels_array, colors,title,  xlabel,ylabel, "lineplot", fulldates = True)

x_array = [df_filt["ANO"]]*3
y_array = [df_filt["REL_HUMIDITY_MEAN"], df_filt["REL_HUMIDITY_AMIN"],df_filt["REL_HUMIDITY_AMAX"] ]
labels_array = ["Mean Rel. Hum.", "Min. Rel. Hum.", "Max. Rel. Hum."]
title = "Humidity over the years for " + municipality
ylabel = "%"
xlabel = "Date"
colors = ["forestgreen","darkblue","orangered"]
plot_time_series(x_array, y_array, labels_array, colors, title,  xlabel,ylabel, "lineplot", fulldates = False)
""";

"""
cols = ['PRECIPITATION', 'TEMPERATURE_MEAN', 'REL_HUMIDITY_MEAN', 'DENGUE']
titles = ["Boxplot of total monthly precipitation for ", 
          "Boxplot of monthly mean temperatures for ",
          "Boxplot of monthly relative humidities for ",
          "Boxplot of monthly Dengue cases for "]
ylables = ['mm', '°C', '%', 'cases']

fig, ax = plt.subplots(figsize=(12, 10), dpi = 150)

for i, col in enumerate(cols):
    plt.subplot(2,2, i+1)
    sns.boxplot(x=df.index.month, y=df[col]).set_title(titles[i] + municipality)
    plt.ylabel(ylables[i])
    plt.xlabel("Month")
    
    
df_corr_melt_sub = df_corr_melt[df_corr_melt['variable'].isin(('SST1+2', 'SST3','SST3.4'))]
fig, axs = plt.subplots(figsize = (12,5), dpi=150)
ax = sns.lineplot(x='lag_size', y='corr', data=df_corr_melt_sub, hue = 'variable').set_title('Lagged correlation between ocean variables and number of dengue cases')


df_corr_melt_sub = df_corr_melt[df_corr_melt['variable'].isin(('ONI', 'TNI'))]
fig, axs = plt.subplots(figsize = (12,5), dpi=150)
ax = sns.lineplot(x='lag_size', y='corr', data=df_corr_melt_sub, hue = 'variable').set_title('Lagged correlation between ocean variables and number of dengue cases')

df_corr_melt_sub = df_corr_melt[df_corr_melt['variable'].isin(("NTA","CAR"))]
fig, axs = plt.subplots(figsize = (12,5), dpi=150)
ax = sns.lineplot(x='lag_size', y='corr', data=df_corr_melt_sub, hue = 'variable').set_title('Lagged correlation between ocean variables and number of dengue cases')


df_corr_melt_sub3 = df_corr_melt[df_corr_melt['variable'] == 'DENGUE_PER_100K']
fig, axs = plt.subplots(figsize = (12,5), dpi=150)
ax = sns.lineplot(x='lag_size', y='corr', data=df_corr_melt_sub3, hue = 'variable').set_title('Number of dengue cases autocorrelation vs lag size in weeks')

df_corr_melt_sub2 = df_corr_melt[df_corr_melt['variable'].isin(('TEMPERATURE_MEAN', 'REL_HUMIDITY_MEAN', 'PRECIPITATION'))]
fig, axs = plt.subplots(figsize = (12,5), dpi=150)
ax = sns.lineplot(x='lag_size', y='corr', data=df_corr_melt_sub2, hue = 'variable').set_title('Lagged correlation between meteorological variables and number of dengue cases')
"""

df_yearly = pd.concat([dic_municipios[n]["df_lagged"] for n in municipios]).dropna()

df_yearly_means = df_yearly[["CITY","ANO","TEMPERATURE_MEAN","TEMPERATURE_RANGE","REL_HUMIDITY_MEAN", 'MEI','ONI', 'SST1+2', 'SST3', 'SST4', 'SST3.4', 'TNI', 'CAR','NTA', 'DENGUE_PER_100K']].groupby(["CITY","ANO"]).mean().reset_index()
df_yearly_sums = df_yearly[["CITY","ANO", 'SEMANA', 'PRECIPITATION','DRY_DAYS', 'DENGUE']].groupby(["CITY","ANO"]).sum().reset_index()
df_yearly = pd.merge(df_yearly_means,df_yearly_sums, how = "left", on = ["CITY","ANO"] )

fig, ax = plt.subplots(1,3, figsize=(15,5), dpi = dpi*1.5)
ax = ax.flatten()
variables = ["TEMPERATURE_MEAN","REL_HUMIDITY_MEAN","PRECIPITATION"]#, "ONI","SST1+2","CAR"]
variable_names = ["Mean temperature", "Mean relative humidity","Total precipitation"]#, "Oceanic Niño Index", "SST1+2", "Caribbean Index"]
for i, var in enumerate(variables):

    sns.scatterplot(x = df_yearly[var], y = df_yearly["DENGUE_PER_100K"], hue = df_yearly["CITY"], ax = ax[i])
    ax[i].set_xlabel(variable_names[i])
    ax[i].set_ylabel("Dengue cases per 100k people")
    ax[i].legend(loc="upper right")
    ax[i].set_title(variable_names[i]+" vs Dengue cases")
    #plt.suptitle("Climatic variables vs Dengue cases per year", fontsize="22")
    if i != 0:
        ax[i].legend().remove()
plt.tight_layout()