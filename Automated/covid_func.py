def CovidPlots():

    # Function to reproduce the interactive plots from:
    # https://hectoramirez.github.io/covid/COVID19.html
    # The code is explained in:
    # https://github.com/hectoramirez/Covid19

    import os
    import pandas as pd
    import datetime
    import plotly.express as px
    import plotly as plty
    import seaborn as sns
    #
    sns.set()
    sns.set_style("whitegrid")
    custom_style = {
        'grid.color': '0.8',
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
    }
    sns.set_style(custom_style)

    os.chdir('/Users/hramirez/GitHub/Covid19/Automated')

    # =========================================================================================  import

    WORLD_CONFIRMED_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    WORLD_DEATHS_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    WORLD_RECOVERED_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

    world_confirmed = pd.read_csv(WORLD_CONFIRMED_URL)
    world_deaths = pd.read_csv(WORLD_DEATHS_URL)
    world_recovered = pd.read_csv(WORLD_RECOVERED_URL)

    sets = [world_confirmed, world_deaths, world_recovered]

    # yesterday's date
    yesterday = world_confirmed.columns[-1]
    today_date = str(pd.to_datetime(yesterday).date() + datetime.timedelta(days=1))
    # print('\nAccording to the latest imput, the data was updated on ' + today_date + '.')

    # =========================================================================================  clean

    for i in range(3):
        sets[i].rename(columns={'Country/Region': 'Country', 'Province/State': 'State'}, inplace=True)
        sets[i][['State']] = sets[i][['State']].fillna('')
        sets[i].fillna(0, inplace=True)

    sets_grouped = []
    cases = ['confirmed cases', 'deaths', 'recovered cases']
    for i in range(3):
        sets_grouped.append(sets[i].groupby('Country').sum())
        # print('\nTop countries by {}:\n'.format(cases[i]))
        # print(sets_grouped[i][yesterday].sort_values(ascending=False).head(5))

    # =========================================================================================  top countries

    def bokehB(dataF, case):

        # Bokeh bar plots. The function takes a dataframe, datF, as the one provided by the raw data
        # (dates as columns, countries as rows). It first takes the last column as yesterday's date.

        from bokeh.io import output_file, save
        from bokeh.plotting import figure
        from bokeh.models import ColumnDataSource, HoverTool
        from bokeh.palettes import Spectral6
        from bokeh.transform import factor_cmap

        df = dataF.iloc[:, -1].sort_values(ascending=False).head(20).to_frame()
        df['totals'] = df.iloc[:, -1]

        # get continent names
        import country_converter as coco
        continent = coco.convert(names=df.index.to_list(), to='Continent')
        df['Continent'] = continent

        source = ColumnDataSource(df)

        select_tools = ['save']
        tooltips = [
            ('Country', '@Country'), ('Totals', '@totals{0,000}')
        ]

        p = figure(x_range=df.index.tolist(), plot_width=840, plot_height=600,
                   x_axis_label='Country',
                   y_axis_label='Totals',
                   title="Top Countries with {} as of ".format(case) + today_date,
                   tools=select_tools)

        p.vbar(x='Country', top='totals', width=0.9, alpha=0.5, source=source,
               legend_field="Continent",
               fill_color=factor_cmap('Continent', palette=Spectral6, factors=df.Continent))

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.xaxis.major_label_orientation = 1
        p.left[0].formatter.use_scientific = False

        p.add_tools(HoverTool(tooltips=tooltips))

        output_file('top_{}.html'.format(case))

        return save(p, 'top_{}.html'.format(case))

    def bokehB_mort(num=100):
        # Bokeh bar plots. The function already includes the confirmed and deaths dataframes,
        # and operates over them to calculate th mortality rate depending on num (number of
        # minimum deaths to consider for a country). The rest is equivalent to the BokehB()
        # function.

        from bokeh.io import output_file, save
        from bokeh.plotting import figure
        from bokeh.models import ColumnDataSource, HoverTool
        from bokeh.palettes import Spectral10
        from bokeh.transform import factor_cmap

        # top countries by deaths rate with at least num deaths
        top_death = sets_grouped[1][yesterday].sort_values(ascending=False)
        top_death = top_death[top_death > num]

        # Inner join to the confirmed set, compute mortality rate and take top 20
        df_mort = pd.concat([sets_grouped[0][yesterday], top_death], axis=1, join='inner')
        df_mort['top_mort'] = round(df_mort.iloc[:, 1] / df_mort.iloc[:, 0] * 100, 2)
        mort_rate = df_mort['top_mort'].sort_values(ascending=False).to_frame().head(20)

        # take yesterday's data
        df = mort_rate.iloc[:, -1].sort_values(ascending=False).head(20).to_frame()
        df['totals'] = df.iloc[:, -1]

        import country_converter as coco
        continent = coco.convert(names=df.index.to_list(), to='Continent')
        df['Continent'] = continent

        source = ColumnDataSource(df)

        select_tools = ['save']
        tooltips = [
            ('Country', '@Country'), ('Rate', '@totals{0.00}%')
        ]

        p = figure(x_range=df.index.tolist(), plot_width=840, plot_height=600,
                   x_axis_label='Country',
                   y_axis_label='Rate (%)',
                   title="Mortality rate of countries with at least {} deaths " \
                         "as of ".format(num) + today_date,
                   tools=select_tools)

        p.vbar(x='Country', top='totals', width=0.9, alpha=0.5, source=source,
               legend_field="Continent",
               fill_color=factor_cmap('Continent', palette=Spectral10, factors=df.Continent))

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.xaxis.major_label_orientation = 1
        p.left[0].formatter.use_scientific = False

        p.add_tools(HoverTool(tooltips=tooltips))

        output_file('top_mortality.html')

        return save(p, 'top_mortality.html')

    for i in range(3):
        bokehB(sets_grouped[i], cases[i])

    bokehB_mort(100)

    # =========================================================================================  daily cases

    # How many top countries?
    n_top = 10
    # Rolling over how many days?
    roll = 7
    # Since how many confirmed cases?
    conf = 100
    # Since how many deaths?
    death = 3

    def dailyC(df, n_cat, n_top=n_top):

        """ Daily cases """

        # n_cat = number of cases since we start counting
        # n_top = number of top countries to show

        # Choose top countries
        top = df.sort_values(by=yesterday, ascending=False).iloc[:n_top, 2:].T
        top.head()

        # Compute daily cases
        daily = top.diff()

        top_countries = daily.columns
        dfs = []
        for i in top_countries:
            dfs.append(pd.DataFrame(daily[i][daily[i] >= n_cat].reset_index(drop=True)))
        df = pd.concat(dfs, axis=1, join='outer').rolling(roll).mean()

        return df

    def bokeh_plot(dataF, cat, n_cat, tickers, n_top=n_top):

        """ Constumizations for the Bokeh plots """
        # cat = {'confirmed', 'deaths', 'recoveries'}
        # n_cat = number of cases since we start counting
        # n_top = number of top countries to show
        # tickers = customized tickers for the logy axis. It is simpler to manually define
        # them than to compute them for each case.

        from bokeh.io import output_file
        from bokeh.plotting import figure, save
        from bokeh.models import HoverTool
        from bokeh.palettes import Category20

        # Specify the selection tools to be made available
        select_tools = ['box_zoom', 'pan', 'wheel_zoom', 'reset', 'crosshair', 'save']

        # Format the tooltip
        tooltips = [
            ('', '$name'),
            ('Days since', '$x{(0)}'),
            ('{}'.format(cat), '$y{(0)}')
        ]

        p = figure(y_axis_type="log", plot_width=840, plot_height=600,
                   x_axis_label='Number of days since {} daily {} first recorded'.format(n_cat, cat),
                   y_axis_label='',
                   title=
                   'Daily {} ({}-day rolling average) by number of days ' \
                   'since {} cases - top {} countries ' \
                   '(as of {})'.format(cat, roll, n_cat, n_top, today_date),
                   toolbar_location='right', tools=select_tools)

        for i in range(n_top):
            p.line(dataF.index[6:], dataF.iloc[6:, i], line_width=2, color=Category20[20][i], alpha=0.8,
                   legend_label=dataF.columns[i], name=dataF.columns[i])
            p.circle(dataF.index[6:], dataF.iloc[6:, i], color=Category20[20][i], fill_color='white',
                     size=3, alpha=0.8, legend_label=dataF.columns[i], name=dataF.columns[i])

        p.yaxis.ticker = tickers

        p.legend.location = 'top_right'
        p.legend.click_policy = 'hide'

        p.add_tools(HoverTool(tooltips=tooltips))

        output_file('Daily_{}.html'.format(cat))

        return save(p, 'Daily_{}.html'.format(cat))

    yticks_conf = [200, 500, 1000, 2000, 5000, 10000, 20000]
    bokeh_plot(dailyC(sets_grouped[0], conf), 'confirmed', conf, yticks_conf)

    yticks_death = [5, 10, 20, 50, 100, 200, 500, 1000, 2000]
    bokeh_plot(dailyC(sets_grouped[1], death), 'deaths', death, yticks_death)

    # =========================================================================================  geo visualizations

    fig = px.scatter_geo(world_confirmed,
                         lat="Lat", lon="Long", color=yesterday,
                         hover_name="Country", size=yesterday,
                         size_max=40,
                         template='plotly', projection="natural earth",
                         title="COVID-19 worldwide confirmed cases")

    plty.offline.plot(fig, filename='Geo_confirmed.html', auto_open=False)

    fig = px.scatter_geo(world_deaths,
                         lat="Lat", lon="Long", color=yesterday,
                         hover_name="Country", size=yesterday,
                         size_max=40,
                         template='plotly', projection="natural earth",
                         title="COVID-19 worldwide deaths")

    plty.offline.plot(fig, filename='Geo_deaths.html', auto_open=False)

    return


CovidPlots()