import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.express as px
import pandas as pd
import datetime
from data import Data
import sys
import os
import sqlite3
import dash_table
import math
import talib
import plotly.graph_objects as go
import pandas_datareader as pdr
from talib import abstract
import plotly.express as px
from  formulation import getPB, getOneSeasonEPS, getMonthRevenue, getCashFlow, getIncomeTable


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)


row = html.Div([
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["收盤價"], className="card-header fontStyle"),
                    html.Div([
                        html.H4(id='sPrice', className="card-title")
                    ], className="card-body")
                ], className="card text-white bg-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-2"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["EPS"], className="card-header fontStyle"),
                    html.Div([
                        html.H4(id='sEPS', className="card-title")
                    ], className="card-body")
                ], className="card text-white bg-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-2"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["本益比"], className="card-header fontStyle"),
                    html.Div([
                        html.H4(id='sPER', className="card-title")
                    ], className="card-body")
                ], className="card text-white bg-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-2"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["股價淨值比"], className="card-header fontStyle"),
                    html.Div([
                        html.H4(id='sPBR', className="card-title")
                    ], className="card-body")
                ], className="card text-white bg-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-2"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["成交股數"], className="card-header fontStyle"),
                    html.Div([
                        html.H4(id='sNumber', className="card-title")
                    ], className="card-body")
                ], className="card text-white bg-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-2"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["收盤日"], className="card-header fontStyle"),
                    html.Div([
                        html.H4(id='sClose', className="card-title")
                    ], className="card-body")
                ], className="card text-white bg-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-2")
], className="row", style={"padding-top":"20px", "padding-left":"10px"})


row1 = html.Div([
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["每月營收"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='monthRevenue-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-6"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["單季EPS"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='oneSeasonEPS-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-6"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["現金流量表"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='cashFlowOperating-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-6"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["損益表"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='incomeStatement-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-6")
], className="row")


row2 = html.Div([
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["K線"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='k-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-12"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["RSI & KD"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='RSI-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-12"),
    html.Div([
        html.Div([
            html.Div(children=[
                    html.Div(["SMA & 股價"], className="card-header fontStyle"),
                    html.Div([
                        dcc.Graph(
                            id='SMA-fig', figure={}
                        )
                    ], className="card-body")
                ], className="card border-secondary mb-3")
        ], className="bs-component")
    ], className="col-lg-12")
], className="row")


app.layout = html.Div([
    html.Nav([
        html.H2(children="stock ^.^  ", className='fontStyle'),
        html.Div([
            html.Ul([
                html.Li([
                    html.H3(id='sName', children="", className='fontStyle')
                ], className="nav-item active")
            ], className="navbar-nav mr-auto"),
            html.Form([
                dcc.Input(id='sId-Input', value='2330', type='number', placeholder='StockId', className="form-control mr-sm-2"),
                html.Button(id='sId-Btn', children="search", n_clicks=0, className="btn btn-secondary my-2 my-sm-0")
            ], className="form-inline my-2 my-lg-0")
        ], className="collapse navbar-collapse")

    ], className="navbar navbar-expand-lg navbar-dark bg-primary"),
    html.Div([
        row,
        row1,
        row2
    ], className="container"),
], style={'background':"#323B44"})



@app.callback(
    [Output('sName', 'children'),
    Output('sPrice', 'children'),
    Output('sNumber', 'children'),
    Output('sPER', 'children'),
    Output('sPBR', 'children'),
    Output('sEPS', 'children'),
    Output('sClose', 'children'),
    Output('monthRevenue-fig', 'figure'),
    Output('oneSeasonEPS-fig', 'figure'),
    Output('cashFlowOperating-fig', 'figure'),
    Output('incomeStatement-fig', 'figure'),
    Output('k-fig', 'figure'),
    Output('RSI-fig', 'figure'),
    Output('SMA-fig', 'figure')],
    [Input('sId-Btn', 'n_clicks')],
    [State('sId-Input', 'value')]
)
def update_basic_info(n_clicks, input_value):
    
    data = Data()
    conn = sqlite3.connect('dataBase.db')
    strid = str(input_value)

    sPrice = data.get('收盤價', 1)[strid].values[0]
    try:
        sName = data.get('公司名稱', 1)[strid]
    except:
        sName = data.get('公司名稱', -1)[strid].values[0]
    sNumber = format(data.get('成交股數', 1)[strid].values[0], ',')
    sPER = data.get('本益比', 1)[strid].values[0]
    sClose = data.dates['price'].iloc[-1].name.strftime("%Y/%m/%d")
    sPBR = getPB(strid)
    sEPS = data.get('基本每股盈餘合計', 1)[strid].values[0]

    #基本圖figure
    revenueFig = getMonthRevenue(strid)
    epsFigure = getOneSeasonEPS(strid)
    chasflowFigure = getCashFlow(strid)
    incometableFigure = getIncomeTable(strid)

    #技術圖
    date = '2019-01-01'
    df = pdr.DataReader(str(strid)+'.TW', 'yahoo', start=date)
    fig = go.Figure(data=go.Candlestick(x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close']))
    fig.update_layout(xaxis_rangeslider_visible=False)

    alldf = pdr.DataReader(str(strid)+'.TW', 'yahoo', start=date)
    alldf = alldf.rename(columns={'High':'high', 'Low':'low', 'OPen':'open', 'Close':'close'})

    #RSI
    RSI = abstract.RSI(alldf)
    rsifig = px.line(RSI)

    #STOCH
    STOCH = abstract.STOCH(alldf)
    stochfig = px.line(STOCH)

    #SMA
    SMA = abstract.SMA(alldf)
    SMAfig = px.line(SMA)
    
    return sName, sPrice, sNumber, sPER, sPBR, sEPS, sClose, revenueFig, epsFigure, chasflowFigure, incometableFigure, fig, stochfig, SMAfig


if __name__ == "__main__":
    app.run_server(debug=True)