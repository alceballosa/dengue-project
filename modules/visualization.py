import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd

path_base = "./local/data/"
df_municipios = pd.read_csv(path_base+"src_general/departments.csv", dtype={'COD_MUNICIPIO':str})

def municipality_codes_to_names(codigo):
    codigos = df_municipios["COD_MUNICIPIO"].values
    nombres = df_municipios["MUNICIPIO"].values
    dict_muns = {(codigos[i]):nombres[i].title() for i in range(len(codigos))}
    return dict_muns[codigo]

def plot_time_series(
    ax,
    dates_array,
    values_array,
    labels,
    colors,
    title,
    x_label,
    y_label,
    xlim=None,
    ylim=None,
    fulldates=False,
    axvline = None,
    area_plot = True,
):
    """
    Function to plot time series:

    dates: must be an array of datetime series for the x axis
    values: the array of y axis values to plot
    labels: the array of labels for each plot
    title: string that goes above the plot
    x_label: string that goes on the x-axis
    y_label: string that goes on the y-axis
    kind: the type of the graph
    fulldates: if the plot is going to receive full dates or just numbers.
    """
    years_locator = mdates.YearLocator()
    months_locator = mdates.MonthLocator()
    years_format = mdates.DateFormatter("%Y")
    sns.set_style("ticks")

    ax.ticklabel_format(axis="y", style="plain")
    if fulldates:
        ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
        ax.xaxis.set_major_locator(years_locator)
        ax.xaxis.set_major_formatter(years_format)
        ax.xaxis.set_minor_locator(months_locator)


    if xlim:
        ax.set_xlim(xlim)
    if area_plot:
        sns.lineplot(
            x=dates_array[0],
            y=values_array[0],
            label=labels[0],
            color=colors[0],
            ax=ax,
        )
        ax.fill_between(
            x=dates_array[0],
            y1=values_array[1],
            y2=values_array[2],
            color=colors[1],
            alpha=0.15,
            label=labels[1],
        )
    else:
        for i in range(len(dates_array)):
            sns.lineplot(
                x=dates_array[i],
                y=values_array[i],
                label=labels[i],
                color=colors[i],
                ax=ax,
            )
        # Min
    # rotation = 45
    # ax.setp(ax.get_xticklabels(), rotation=rotation)
    if axvline:
        ax.axvline(x=axvline, ls='--', label = "COVID-19 arrival date", color = "black")
    ax.set_xlabel(x_label, fontsize="12")
    ax.set_ylabel(y_label, fontsize="12")
    ax.set_title(title, fontsize="14")
    if ylim:
        ax.set_ylim(ylim)

    ax.legend(loc="upper left", frameon = False)
    sns.despine()


def plot_monthly_boxplot(
    ax,
    dates_array,
    values_array,
    title,
    x_label,
    y_label,
    ylim=None
):

    sns.set_style("ticks")
    ax.ticklabel_format(axis="y", style="plain")
    sns.boxplot(x=dates_array[0], y=values_array[0], ax=ax)
    ax.set_xlabel(x_label, fontsize="12")
    ax.set_ylabel(y_label, fontsize="12")
    ax.set_title(title, fontsize="14")
    if ylim:
        ax.set_ylim(ylim)

    sns.despine()

