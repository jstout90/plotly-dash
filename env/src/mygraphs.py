import dash_table
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pyodbc
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = dash.Dash()
conn = pyodbc.connect(
                        r'Driver={SQL Server};'
                        r'SERVER=DATABASE_NAME;'
                        r'Database=DATABASE;'
                        r'Trusted_Connection=yes;'
                        r'uid=USERNAME;'
                        r'pwd=PASSWORD;'
                        )
todays_date = datetime.today()
last_week = datetime.today() - relativedelta(days=7)

df = pd.read_sql_query("""
                                        SQL COMMAND GOES HERE
                                        """, conn)


app.layout = html.Div([
    html.Div([
                html.Div([
                                html.H2('Progressive Machine', style={'textAlign': 'center'}),
                                dcc.Graph(id='graph-one'),
                                dcc.Graph(id='graph-two'),
                                dcc.Graph(id='graph-three'),
                                ], className="six columns"),

                html.Div([
                                html.H3('Report', style={'textAlign': 'center'}),
                                dash_table.DataTable(id='table',
                                                        columns=[
                                                            {"name": i, "id": i} for i in df.columns
                                                            ]),
                                ], className="three columns"),
                html.Div([
                                html.H3('Select Date Range'),
                                dcc.DatePickerRange(
                                        id='date-picker-range',
                                        start_date=last_week,
                                        end_date=todays_date,
                                        initial_visible_month=todays_date
                                        ),
                                dcc.Graph(id='pie-one'),
                                dcc.Graph(id='pie-two'),
                                dcc.Graph(id='pie-three'),
                                dcc.Graph(id='pie-four'),
                                ], className="three columns")
                ], className="row"),
            ])


@app.callback(Output('pie-one', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_pie_one(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    s = df2['SCRAP PCS'].astype(int)
    new_df = df2.loc[s.idxmax()]
    new_df['PROD DATE'] = pd.to_datetime(new_df['PROD DATE'], format='%Y%m%d')

    figure = {
        'data': [
            go.Pie(
                labels=['Good Pieces', 'Scrap Pieces'],
                values=[new_df['GOOD PCS RAN'], new_df['SCRAP PCS']],
                hoverinfo='label+percent', textinfo='value',
                textfont=dict(size=20),
                marker={'colors': ['#12B0F8', '#f2070b']},
                ),
        ],
        'layout': go.Layout(
            title='Highest Scrap Day {}'.format(new_df['PROD DATE']),
                )
    }
    return figure


@app.callback(Output('pie-two', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_pie_two(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    s = df2['SCRAP PCS'].astype(int)
    new_df = df2.loc[s.idxmax()]
    figure = {
        'data': [
            go.Pie(
                labels=['Setups', 'Scrap Pieces'],
                values=[new_df['SETUPS'], new_df['SCRAP PCS']],
                hoverinfo='label+percent', textinfo='value',
                textfont=dict(size=20),
                marker={'colors': ['#8a13f2', '#f2070b']}
                ),
        ],
        'layout': go.Layout(
            title='Scrap Compared to Setups',
                )
    }
    return figure


@app.callback(Output('pie-three', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_pie_three(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    s = df2['SCRAP PCS'].astype(int)
    new_df = df2.loc[s.idxmax()]
    figure = {
        'data': [
            go.Pie(
                labels=['Hours Scheduled', 'Scrap Pieces'],
                values=[new_df['HOURS SCHED'], new_df['SCRAP PCS']],
                hoverinfo='label+percent', textinfo='value',
                textfont=dict(size=20),
                marker={'colors': ['#14fc4e', '#f2070b']}
                ),
        ],
        'layout': go.Layout(
            title='Scrap Compared to Hours Scheduled',
                )
    }
    return figure


@app.callback(Output('pie-four', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_pie_four(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    s = df2['SCRAP PCS'].astype(int)
    new_df = df2.loc[s.idxmax()]
    figure = {
        'data': [
            go.Pie(
                labels=['People', 'Scrap Pieces'],
                values=[new_df['PEOPLE'], new_df['SCRAP PCS']],
                hoverinfo='label+percent', textinfo='value',
                textfont=dict(size=20),
                marker={'colors': ['#f7710a', '#f2070b']},
                ),
        ],
        'layout': go.Layout(
            title='Scrap Compared to People',
                )
    }
    return figure


@app.callback(Output('table', 'data'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    data = df2.to_dict("rows")
    return data


@app.callback(Output('graph-one', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    figure = {
        'data': [
            go.Bar(
                x=df2['PROD DATE'],
                y=df2['GOOD PCS RAN'],
                name='Good Pieces Ran',
                marker=dict(color='#12B0F8'),
                hoverinfo='y',
                ),
            go.Bar(
                x=df2['PROD DATE'],
                y=df2['SCRAP PCS'],
                name='Scrap Pieces',
                marker=dict(color='#f2070b'),
                hoverinfo='y',
                )
        ],
        'layout': go.Layout(
            title='Good Pieces vs Scrap Pieces',
            yaxis=dict(
                            title='Good Pieces vs Scrap Pieces'),
            xaxis={'title': 'Production Date'},
            hovermode='closest',
                )
    }
    return figure


@app.callback(Output('graph-two', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_graph_two(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    figure = {
        'data': [
            go.Bar(
                x=df2['PROD DATE'],
                y=df2['HOURS SCHED'],
                name='Hours Scheduled',
                marker=dict(color='#14fc4e'),
                hoverinfo='y',
                ),
            go.Bar(
                x=df2['PROD DATE'],
                y=df2['SETUPS'],
                name='Setups',
                marker=dict(color='#8a13f2'),
                hoverinfo='y',
                ),
        ],
        'layout': go.Layout(
            title='Hours Scheduled vs Total Setups',
            yaxis=dict(
                        title='Hours Scheduled vs Total Setups'),

            xaxis={'title': 'Production Date'},
            hovermode='closest',

                )
    }
    return figure


@app.callback(Output('graph-three', 'figure'),
              [Input('date-picker-range', 'start_date'),
              Input('date-picker-range', 'end_date')])
def update_graph_three(start_date, end_date):
    df2 = df[(df['PROD DATE'] >= start_date) & (df['PROD DATE'] <= end_date)]
    figure = {
        'data': [
            go.Bar(
                x=df2['PROD DATE'],
                y=df2['HOURS SCHED'],
                name='Hours Scheduled',
                marker=dict(color='#14fc4e'),
                hoverinfo='y',
                ),
            go.Bar(
                x=df2['PROD DATE'],
                y=df2['PEOPLE'],
                name='People',
                marker=dict(color='#f7710a'),
                hoverinfo='y',
                ),

        ],
        'layout': go.Layout(
            title='Hours Scheduled vs Total People',
            yaxis=dict(
                        title='Hours Scheduled vs Total People'),
            xaxis={'title': 'Production Date'},
            hovermode='closest',

                )
    }

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
