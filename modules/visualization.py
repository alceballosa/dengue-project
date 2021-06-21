import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from statsmodels.tsa.seasonal import seasonal_decompose

sns.set_style("ticks")
plt.rcParams["font.family"] = "Helvetica"
plt.rcParams.update({"font.size": 12})


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
    kind="lineplot",
    fulldates=False,
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

    if kind == "lineplot":
        sns.lineplot(
            x=dates_array[0],
            y=values_array[0],
            label=labels[0],
            color=colors[0],
            ax=ax,
        )

    rotation = 45
    #     ax.setp(ax.get_xticklabels(), rotation=rotation)
    if len(values_array) > 1:
        ax.fill_between(
            x=dates_array[0],
            y1=values_array[1],
            y2=values_array[2],
            color=colors[1],
            alpha=0.15,
            label=labels[1],
        )  # Min
    ax.set_xlabel(x_label, fontsize="12")
    ax.set_ylabel(y_label, fontsize="12")
    ax.set_title(title, fontsize="14")
    if ylim:
        ax.set_ylim(ylim)
    if xlim:
        ax.set_xlim(xlim)
    ax.legend()
    sns.despine()
