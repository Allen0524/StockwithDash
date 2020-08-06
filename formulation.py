#一些公式計算

from data import Data
import plotly.express as px
import plotly.graph_objects as go


def modifMonthtoSeason(s):
    if s.month == 1:
        s = s.strftime('%YQ%m')
    elif s.month == 4:
        s = s.replace(month=2)
        s = s.strftime('%YQ%m')
    elif s.month == 7:
        s = s.replace(month=3)
        s = s.strftime('%YQ%m')
    else:
        s = s.replace(month=4)
        s = s.strftime('%YQ%m')
    
    return s


def getPB(id):

    dataPB = Data()
    id = str(id)
    
    price = dataPB.get('收盤價', 1)[id].values[0]
    equity = dataPB.get('歸屬於母公司業主之權益合計', 1)[id].values[0]*1000
    capital = dataPB.get('普通股股本', 1)[id].values[0]*1000
    pb = price / (equity/(capital/10))
    
    return round(pb, 2)


def getOneSeasonEPS(strid):

    data = Data()
    length_eps = len(data.dates['incomeStatement'])
    oneSeasonEPS = data.get('基本每股盈餘合計', length_eps)[strid].to_frame()
    oneSeasonEPS = oneSeasonEPS.reset_index()
    oneSeasonEPS['date'] = oneSeasonEPS['date'].apply(modifMonthtoSeason)
    oneSeasonEPS.set_index('date', inplace=True)
    oneSeasonEPSfig = {
        'x': oneSeasonEPS.index,
        'y': oneSeasonEPS[strid],
        #'mode': 'bar',
        #'hovertemplate': "%{x}的EPS= %{y:$,}"
    }

    fig = px.line(oneSeasonEPSfig, x='x', y='y')
    fig.update_traces(mode="markers+lines", hovertemplate="%{x}的EPS= %{y:$,}")
    fig.update_layout(
        plot_bgcolor = '#36404A',
        paper_bgcolor = '#36404A',
        font_color = '#7FDBFF',
        xaxis = {'title':'季度'},
        yaxis = {'title':'元'}
    )

    return fig

def getMonthRevenue(strid):

    data = Data()
    length_revenue = len(data.dates['monthRevenue'])
    revenue = data.get('當月營收', length_revenue)[strid].to_frame()
    monthRevfig = {
        'x': revenue.index,
        'y': revenue[strid],
    }

    fig = px.line(monthRevfig, x='x', y='y')
    fig.update_traces(mode="markers+lines", hovertemplate="%{x}月營收= %{y:$,}")
    fig.update_layout(
        plot_bgcolor = '#36404A',
        paper_bgcolor = '#36404A',
        font_color = '#7FDBFF',
        xaxis = {'title':'月份'},
        yaxis = {'title':'千元'}
    )

    return fig

def getCashFlow(strid):

    data = Data()
    #---------現金流量表畫圖
    length_cashFlow = len(data.dates['cashFlowsSheet'])
    cashFlowOperating = data.get('營業活動之淨現金流入（流出）', length_cashFlow)[strid].to_frame()
    cashFlowOperating = cashFlowOperating.reset_index()
    cashFlowOperating['date'] = cashFlowOperating['date'].apply(modifMonthtoSeason)
    copyCashFlow = cashFlowOperating.copy()
    for i in range(1, len(cashFlowOperating)):
        cashFlowOperating.at[i, strid] = cashFlowOperating.at[i, strid] - copyCashFlow.at[i-1, strid]
    
    cashFlowOperating.set_index('date', inplace=True)

    #投資現金流
    length_investFlow = len(data.dates['cashFlowsSheet'])
    investFlowOperating = data.get('投資活動之淨現金流入（流出）', length_investFlow)[strid].to_frame()
    investFlowOperating = investFlowOperating.reset_index()
    investFlowOperating['date'] = investFlowOperating['date'].apply(modifMonthtoSeason)
    copyInvestFlow = investFlowOperating.copy()
    for i in range(1, len(investFlowOperating)):
        investFlowOperating.at[i, strid] = investFlowOperating.at[i, strid] - copyInvestFlow.at[i-1, strid]
    
    investFlowOperating.set_index('date', inplace=True)
    #End 投資現金流

    #籌資現金流
    length_funddraseFlow = len(data.dates['cashFlowsSheet'])
    fundraseFlowOperating = data.get('籌資活動之淨現金流入（流出）', length_funddraseFlow)[strid].to_frame()
    fundraseFlowOperating = fundraseFlowOperating.reset_index()
    fundraseFlowOperating['date'] = fundraseFlowOperating['date'].apply(modifMonthtoSeason)
    copyfundraseFlow = fundraseFlowOperating.copy()
    for i in range(1, len(fundraseFlowOperating)):
        fundraseFlowOperating.at[i, strid] = fundraseFlowOperating.at[i, strid] - copyfundraseFlow.at[i-1, strid]
    
    fundraseFlowOperating.set_index('date', inplace=True)
    #End 籌資現金流

    #淨現金流
    #淨現金流 = 營業現金流 - 投資現金流 + 籌資現金流
    netCashFlow = cashFlowOperating.copy()
    re_netCash = netCashFlow.reset_index()
    re_cash = cashFlowOperating.reset_index()
    re_invest = investFlowOperating.reset_index()
    re_fund = fundraseFlowOperating.reset_index()
    for i in range(0, len(cashFlowOperating)):
        if re_invest.at[i, strid] < 0:
            re_netCash.at[i, strid] = re_cash.at[i, strid] + re_invest.at[i, strid]
        else:
            re_netCash.at[i, strid] = re_cash.at[i, strid] - re_invest.at[i, strid]
    re_netCash.set_index('date', inplace=True)
    re_netCash = re_netCash.add(fundraseFlowOperating, axis=0)
    #End 淨現金流

    cashFlowOperatingfig = [{
        'x' : cashFlowOperating.index,
        'y' : cashFlowOperating[strid],
        'type':'line',
        'name':'營業現金流',
        'hovertemplate': "%{x}營業現金流= %{y:$,}"
    },{
        'x': investFlowOperating.index,
        'y':investFlowOperating[strid],
        'type':'line',
        'name':'投資現金流',
        'hovertemplate': "%{x}投資現金流= %{y:$,}"
    },{
        'x': fundraseFlowOperating.index,
        'y':fundraseFlowOperating[strid],
        'type':'line',
        'name':'籌資現金流',
        'hovertemplate': "%{x}籌資現金流= %{y:$,}"
    },{
        'x': re_netCash.index,
        'y':re_netCash[strid],
        'type':'line',
        'name':'淨現金流',
        'hovertemplate': "%{x}淨現金流= %{y:$,}"
    },
    ]
    #---------End  現金流量表畫圖

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=(cashFlowOperatingfig[0])['x'], y=(cashFlowOperatingfig[0])['y'], name='營業現金流', hovertemplate='%{x}營業現金流= %{y:$,}'))
    fig.add_trace(go.Scatter(x=(cashFlowOperatingfig[1])['x'], y=(cashFlowOperatingfig[1])['y'], name='投資現金流', hovertemplate="%{x}投資現金流= %{y:$,}"))
    fig.add_trace(go.Scatter(x=(cashFlowOperatingfig[2])['x'], y=(cashFlowOperatingfig[2])['y'], name='籌資現金流', hovertemplate='%{x}籌資現金流= %{y:$,}'))
    fig.add_trace(go.Scatter(x=(cashFlowOperatingfig[3])['x'], y=(cashFlowOperatingfig[3])['y'], name='淨現金流', hovertemplate='%{x}淨現金流= %{y:$,}'))
    fig.update_layout(
        plot_bgcolor = '#36404A',
        paper_bgcolor = '#36404A',
        font_color = '#7FDBFF',
        xaxis = {'title':'季度'},
        yaxis = {'title':'千元'}
    )
    return fig

def getIncomeTable(strid):

    data = Data()
    #-------損益表
    length_incomeTable = len(data.dates['incomeStatement'])
    incomeTable = data.get('營業收入合計', length_incomeTable)[strid].to_frame()
    incomeTable = incomeTable.reset_index()
    incomeTable['date'] = incomeTable['date'].apply(modifMonthtoSeason)
    copyIncomeTable = incomeTable.copy()


    #若為金控產業等要看淨收益
    rawData = data.get('營業收入合計', length_incomeTable)
    allnanlist = rawData.columns[rawData.isna().any()]
    if strid in allnanlist:
        incomeTable = data.get('淨收益', length_incomeTable)[strid].to_frame()
        if math.isnan(incomeTable[strid][0]):#有些產業則是叫收入合計6005、6024待處理
            incomeTable = data.get('收入合計', length_incomeTable)[strid].to_frame()
        incomeTable = incomeTable.reset_index()
        incomeTable['date'] = incomeTable['date'].apply(modifMonthtoSeason)
        copyIncomeTable = incomeTable.copy()
        counter1 = 0
        for i in incomeTable['date']:
            if i.find('Q04') != -1:#是第四季
                for j in range(counter1-1,counter1-3-1,-1):
                    incomeTable.at[counter1, strid] = incomeTable.at[counter1, strid] - copyIncomeTable.at[j, strid]
                counter1+=1    
            else:
                counter1+=1
    else:
        #檢查是否為第四季
        counter = 0
        for i in incomeTable['date']:
            if i.find('Q04') != -1:#是第四季
                for j in range(counter-1,counter-3-1,-1):
                    incomeTable.at[counter, strid] = incomeTable.at[counter, strid] - copyIncomeTable.at[j, strid]
                counter+=1    
            else:
                counter+=1
    
    incomeTable.set_index('date', inplace=True)

    #---------稅前淨利
    length_preTaxIncome = len(data.dates['incomeStatement'])
    preTaxIncome = data.get('繼續營業單位稅前淨利（淨損）', length_preTaxIncome)[strid].to_frame()
    preTaxIncome = preTaxIncome.reset_index()
    preTaxIncome['date'] = preTaxIncome['date'].apply(modifMonthtoSeason)
    copyPreTax = preTaxIncome.copy()

    counter_preTax = 0
    for i in preTaxIncome['date']:
        if counter_preTax%4 != 0:#不是第一季
            preTaxIncome.at[counter_preTax, strid] = preTaxIncome.at[counter_preTax, strid] - copyPreTax.at[counter_preTax-1, strid]
            counter_preTax+=1
        else:
            counter_preTax+=1
    
    preTaxIncome.set_index('date', inplace=True)

    #---------End稅前淨利

    incomeStatementfig = [{
        'x' : incomeTable.index,
        'y' : incomeTable[strid],
        'type':'line',
        'name':'營業收入',
        'hovertemplate': "%{x}營業收入= %{y:$,}"
    },{
        'x' : preTaxIncome.index,
        'y' : preTaxIncome[strid],
        'type':'line',
        'name':'稅前淨利',
        'hovertemplate': "%{x}稅前淨利= %{y:$,}"
    }]
    #-------End 損益表

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=(incomeStatementfig[0])['x'], y=(incomeStatementfig[0])['y'], name='營業收入', hovertemplate='%{x}營業收入= %{y:$,}'))
    fig.add_trace(go.Scatter(x=(incomeStatementfig[1])['x'], y=(incomeStatementfig[1])['y'], name='稅前淨利', hovertemplate="%{x}稅前淨利= %{y:$,}"))
    fig.update_layout(
        plot_bgcolor = '#36404A',
        paper_bgcolor = '#36404A',
        font_color = '#7FDBFF'
    )

    return fig