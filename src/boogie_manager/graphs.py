# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd


def pie_chart(df, col_name, save_path=None, label_mapper=None, title=None):

    """
    pie_chart : makes a pie chart of a certain column in the data frame, showing
                which percentage of the total collection (in terms of playing time) 
                is accounted for by each unique value in that column

    :input df           : (DataFrame) the dataframe with music data
    :input col_name     : (str) the column to graph
    :input save_path    : (str) file path to save the generated image; must end in .png.
                          If None, the image is not saved to disk
    :input label_mapper : (dict) dictionary mapping values in 'col_name' to labels in the
                          graph legend. If None, the values themselves are used as labels
    :input title        : (str) title to put on the graph legend. If None, the column name
                          itself is used as a title
    """

    gb4pie = df[[col_name, 'length']].groupby(col_name)
    sums4pie = gb4pie.sum()['length']
    if label_mapper is not None:
        new_index = [label_mapper[idx] for idx in sums4pie.index]
        sums4pie.index = new_index
    fig, ax = plt.subplots() 
    ax.pie(sums4pie.values, startangle=90, labels=None, counterclock=False, autopct='%1.1f%%', pctdistance=1.07, radius=1.5)
    if title is None:
        title = col_name
    ax.legend(loc='center left', bbox_to_anchor=[1.25, 0.5], labels=sums4pie.index, title=title)
    total_hours = int(df['length'].sum() / 3600.0)
    ax.text(x=1.25, y=0.25, s='Total {0} hours of music'.format(total_hours), transform=ax.transAxes)
    plt.tight_layout()
    fig.set_size_inches(12, 9)
    if save_path is not None:
        fig.savefig(save_path, dpi=120, format='png', bbox_inches='tight')


def graph_vs_year(df, col_name, save_path=None, label_mapper=None, title=None):

    """
    graph_vs_year : makes a stacked bar graph of two columns of the dataframe, one of which
                    is 'year'. Release years will be plotted on the horizontal axis, with one
                    bar for each year. The vertical axis shows how much music (in hours) there
                    is in the collection from each year. Each year's bar is subdivided by the 
                    values in the selected column (e.g. genre)

    :input df           : (DataFrame) the dataframe with music data
    :input col_name     : (str) the column to graph, other than 'year'
    :input save_path    : (str) file path to save the generated image; must end in .png.
                          If None, the image is not saved to disk
    :input label_mapper : (dict) dictionary mapping values in 'col_name' to labels in the
                          graph legend. If None, the values themselves are used as labels
    :input title        : (str) title to put on the graph legend. If None, the column name
                          itself is used as a title
    """

    # Convert the year tags (stored as strings) to integers so Matplotlib understands to
    # plot them as a series of numbers
    df['year'] = df['year'].astype(str).astype(int)

    startyear = min(df['year'])
    endyear = max(df['year'])
    years = list(range(startyear, endyear + 1))
    year_ticks = [year for year in years if year % 10 == 0]

    gb_main = df[['year', col_name, 'length']].groupby(['year', col_name])
    sums_main = gb_main.sum()['length']
    groupdf_main = pd.DataFrame(index=years, columns=sorted(list(set(df[col_name]))))
    for year in years:
        for value in groupdf_main.columns:
            if (year, value) in gb_main.groups:
                groupdf_main.loc[year, value] = sums_main.loc[(year, value)] / 3600.0
            else:
                groupdf_main.loc[year, value] = 0.0

    fig, ax = plt.subplots()
    bottomlist = [0 for i in range(len(groupdf_main))]
    bars = []
    for value in groupdf_main.columns:
        bars.append(ax.bar(groupdf_main.index, groupdf_main[value], bottom=bottomlist))
        for i in range(len(groupdf_main)):
            bottomlist[i] += groupdf_main[value].iloc[i]
    fig.set_size_inches(16, 9)
    if label_mapper is not None:
        new_columns = [label_mapper[idx] for idx in groupdf_main.columns]
        groupdf_main.columns = new_columns
    ax.set_xlim([startyear - 1, endyear + 1])
    yearmax = groupdf_main.sum(axis=1).max()
    ax.set_ylim([0, int(yearmax * 1.1)])
    ax.set_xlabel('Release year')
    ax.set_ylabel('Music [hours]')
    ax.set_xticks(year_ticks)
    ax.grid(axis='x')
    if title is None:
        title = col_name
    ax.legend(loc='upper left', handles=bars, labels=list(groupdf_main.columns), title=title)
    plt.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=120, format='png', bbox_inches='tight')


def top_x(df, col_name, cutoff=25, save_path=None):

    """
    top_x : makes a bar graph of the most occurring values in one column of a dataframe

    :input df           : (DataFrame) the dataframe with music data
    :input col_name     : (str) the column to graph
    :input cutoff       : (int) the number of values to plot
    :input save_path    : (str) file path to save the generated image; must end in .png.
                          If None, the image is not saved to disk
    """

    gb = df[[col_name, 'length']].groupby(col_name)
    sums = gb.sum()['length'].copy() / 3600
    sums.sort_values(inplace=True, ascending=False)
    fig, ax = plt.subplots()
    sums[:cutoff].plot.bar(ax)
    ax.set_xlabel('')
    ax.set_ylabel('Music (hours)')
    # Adjust the bar label font size to the number of bars
    # (more bars -> smaller fonts)
    plt.xticks(rotation=45, ha='right', fontsize=min(10, 200/cutoff))
    plt.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=120, format='png', bbox_inches='tight')

