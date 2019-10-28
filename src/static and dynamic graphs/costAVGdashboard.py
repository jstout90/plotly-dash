import dash_table
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True
df = pd.read_excel("PATH TO EXCEL FILE")
df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

gesso = df[df['MACHINE'] == 'FILL COA']
mldr5 = df[df['MACHINE'] == 'MLDR 5']

site_options = df['SITE'].unique()

dynamic_df_start = df['DATE'].dt.date.iloc[-1]
dynamic_df_end = df['DATE'].dt.date.iloc[0]

mldr5_newest_date = mldr5['DATE'].dt.date.iloc[-1]
mldr5_oldest_date = mldr5['DATE'].dt.date.iloc[0]

gesso_newest_date = gesso['DATE'].dt.date.iloc[-1]
gesso_oldest_date = gesso['DATE'].dt.date.iloc[0]

app.layout = html.Div([
                        html.Div([
                            dcc.Tabs(
                                id="tabs-with-classes",
                                value='tab-1',
                                parent_className='custom-tabs',
                                className='custom-tabs-container',
                                children=[
                                    dcc.Tab(
                                        label='Static Graphs',
                                        value='tab-1',
                                        className='custom-tab',
                                        selected_className='custom-tab--selected'
                                    ),
                                    dcc.Tab(
                                        label='Dynamic Graphs',
                                        value='tab-2',
                                        className='custom-tab',
                                        selected_className='custom-tab--selected'
                                    ),
                                ]),
                            html.Div(id='tabs-content-classes')
                        ]),
                    ])


@app.callback(Output('tabs-content-classes', 'children'),
              [Input('tabs-with-classes', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Div([
                        html.Div([
                                        dcc.Graph(id='graph-one'),
                                        dcc.Markdown(f'''
                                        Showing date range of {mldr5_oldest_date} through {mldr5_newest_date}.
                                        ''', style={'textAlign': 'center'}),
                                        ], className="six columns"),
                        html.Div([
                                        dcc.Graph(id='graph-two'),
                                        dcc.Markdown(f'''
                                        Showing date range of {gesso_oldest_date} through {gesso_newest_date}.
                                        ''', style={'textAlign': 'center'}),
                                        ], className="six columns"),
                        html.Div([
                                        dcc.DatePickerRange(
                                                id='mldr5-picker-range',
                                                start_date=mldr5_oldest_date,
                                                end_date=mldr5_newest_date,
                                                initial_visible_month=mldr5_newest_date
                                                ),
                                        dcc.DatePickerRange(
                                                id='gesso-picker-range',
                                                start_date=gesso_oldest_date,
                                                end_date=gesso_newest_date,
                                                initial_visible_month=gesso_newest_date
                                                ),
                                        dcc.Interval(
                                            id='interval-component',
                                            interval=24*3600000,
                                            n_intervals=0
                                            ),
                                        ], style={'display': 'none'}, className="three columns")
                        ], className="row"),
                    ])
    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                            dcc.Graph(id='graph-three'),
                            ], className="twelve columns"),
            html.Div([

                        html.Div([
                                        dash_table.DataTable(id='table',
                                                                columns=[
                                                                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                                                                    ],
                                                                sort_action="native",
                                                                sort_mode="multi",
                                                                editable=True,
                                                                row_selectable="multi",
                                                                row_deletable=True,
                                                                page_action='native',
                                                                page_current= 0,
                                                                page_size= 30,
                                                                ),
                                        ], className="seven columns"),
                        html.Div([
                            dcc.Markdown('''Select Site.'''),
                            dcc.Dropdown(
                                    id='site-choice',
                                    options=[{'label': i, 'value': i} for i in site_options],
                                    ),
                            dcc.Markdown('''Select  Machine.'''),
                            dcc.Dropdown(
                                    id='machine-choice',
                                    ),
                            dcc.Markdown('''Select date range to change table.'''),
                            dcc.DatePickerRange(
                                    id='date-picker-range',
                                    start_date=dynamic_df_end,
                                    end_date=dynamic_df_start,
                                    initial_visible_month=dynamic_df_start
                                    ),
                            dcc.Markdown('''
                            * Table is interactable:
                                * Filter from highest to lowest
                                * Remove columns & rows
                                * Click to highlight
                                * Hold Shift and click to multi-highlight
                                * Only displays 30 rows
                                    * Click next button at the bottom to go to next page
                                                        '''),
                                ], className="three columns"),
                        ], className="row"),
                    ])


@app.callback(
    Output('machine-choice', 'options'),
    [Input('site-choice', 'value')])
def set_machine_site(available_options):
    site = df[df['SITE'] == available_options]
    machine_options = site['MACHINE'].unique()
    return [{'label': i, 'value': i} for i in machine_options]


@app.callback(Output('graph-one', 'figure'),
              [Input('mldr5-picker-range', 'start_date'),
              Input('mldr5-picker-range', 'end_date'),
              Input('interval-component', 'n_intervals')])
def update_graph_one(start_date, end_date, interval):
    new_list = []
    for x in range(0, 54):
        filtered_mldr5_iso = mldr5[mldr5['DATE'].dt.week == x]
        if not filtered_mldr5_iso.empty:
            pplHours = filtered_mldr5_iso['HRS'] * filtered_mldr5_iso['PEOPLE']
            costPerPersonHours = pplHours.sum()*35
            result = costPerPersonHours/filtered_mldr5_iso['PCS RAN'].sum()
            new_list.append(result)

    figure = {
        'data': [
            go.Bar(
                x=mldr5['DATE'].dt.week.unique(),
                y=new_list,
                name='ISO Week Average Cost',
                marker=dict(color='#F40005'),
                hoverinfo='y',
                text=["${0:0.2f}".format(i) for i in new_list],
                textposition='auto',
                ),
        ],
        'layout': go.Layout(
            title='Moulder 5',
            yaxis=dict(
                            title='Cost',
                            hoverformat='$,.2f'),
            xaxis={
                'title': 'ISO Weeks',
                },
            hovermode='closest',
            )
    }
    return figure


@app.callback(Output('graph-two', 'figure'),
              [Input('gesso-picker-range', 'start_date'),
              Input('gesso-picker-range', 'end_date'),
              Input('interval-component', 'n_intervals')])
def update_graph_two(start_date, end_date, interval):
    new_list = []
    for x in range(0, 54):
        filtered_gesso_iso = gesso[gesso['DATE'].dt.week == x]
        if not filtered_gesso_iso.empty:
            pplHours = filtered_gesso_iso['HRS'] * filtered_gesso_iso['PEOPLE']
            costPerPersonHours = pplHours.sum()*35
            result = costPerPersonHours/filtered_gesso_iso['PCS RAN'].sum()
            new_list.append(result)

    figure = {
        'data': [
            go.Bar(
                x=gesso['DATE'].dt.week.unique(),
                y=new_list,
                name='ISO Week Average Cost',
                marker=dict(color='#FFC100'),
                hoverinfo='y',
                text=["${0:0.2f}".format(i) for i in new_list],
                textposition='auto',
                ),
        ],
        'layout': go.Layout(
            title='Fill Coat',
            yaxis=dict(
                            title='Cost',
                            hoverformat='$,.2f'),
            xaxis={'title': 'ISO Weeks'},
            hovermode='closest',

                )
    }
    return figure


@app.callback(Output('graph-three', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date'),
              Input('machine-choice', 'value'),
              Input('site-choice', 'value')])
def update_graph_three(start_date, end_date, machine_choice, site_choice):
    new_list = []
    machine_picked = df[df['MACHINE'] == machine_choice]
    site_picked = machine_picked[machine_picked['SITE'] == site_choice]

    for x in range(0, 54):
        filtered_df = site_picked[site_picked['DATE'].dt.week == x]
        if not filtered_df.empty:
            pplHours = filtered_df['HRS'] * filtered_df['PEOPLE']
            costPerPersonHours = pplHours.sum()*35
            result = costPerPersonHours/filtered_df['PCS RAN'].sum()
            new_list.append(result)

    figure = {
        'data': [
            go.Scatter(
                x=site_picked['DATE'].dt.week.unique(),
                y=new_list,
                name='Cost Per Piece',
                marker=dict(color='#270fff'),
                hoverinfo='y',
                ),
        ],
        'layout': go.Layout(
            title=f'{machine_choice}',
            yaxis=dict(
                            title='Cost',
                            hoverformat='$.2f'),
            xaxis={
                'title': 'ISO Weeks',
                },
            hovermode='closest',

                )
    }
    return figure


@app.callback(Output('table', 'data'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date'),
              Input('machine-choice', 'value'),
              Input('site-choice', 'value')])
def update_table(start_date, end_date, machine_choice, site_choice):
    machine_picked = df[df['MACHINE'] == machine_choice]
    site_picked = machine_picked[machine_picked['SITE'] == site_choice]
    df2 = site_picked[(site_picked['DATE'] >= start_date) & (site_picked['DATE'] <= end_date)]
    data = df2.to_dict('rows')
    return data


if __name__ == '__main__':
    app.run_server(host='10.0.0.210', port=8050)
