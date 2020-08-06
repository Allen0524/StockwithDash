import sqlite3
import pandas as pd
import os
import datetime

class Data():
    def __init__(self):
        
        self.conn = sqlite3.connect('dataBase.db')
        cursor = self.conn.execute('SELECT tbl_name FROM sqlite_master WHERE type = "table"')
        
        # 找到所有的table名稱
        table_names = [t[0] for t in list(cursor)]
        
        # 找到所有的column名稱，對應到的table名稱
        self.col2table = {} #dict型態
        for tname in table_names:
            
            # 獲取所有column名稱
            c = self.conn.execute('PRAGMA table_info('+tname+');')
            for cname in [i[1] for i in list(c)]:
                
                # 將column名稱對應到的table名稱assign到self.col2table中
                self.col2table[cname] = tname
                
        
        self.date = datetime.datetime.now().date()
        
        
        # 假如self.cache是true的話，
        # 使用data.get的資料，會被儲存在self.data中，之後再呼叫data.get時，就不需要從資料庫裡面找，
        # 直接調用self.data中的資料即可
        self.cache = False
        self.data = {}
        
        
        # 先將每個table的所有日期都拿出來
        self.dates = {}
        
        # 對於每個table，都將所有資料的日期取出
        for tname in table_names:
            c = self.conn.execute('PRAGMA table_info('+tname+');')
            cnames = [i[1] for i in list(c)]
            if 'date' in cnames:
                if tname == 'price':
                    # 假如table是股價的話，則觀察這三檔股票的日期即可（不用所有股票日期都觀察，節省速度）
                    s1 = ("SELECT DISTINCT date FROM %s where stock_id='0050'"%('price'))
                    s2 = ("SELECT DISTINCT date FROM %s where stock_id='1101'"%('price'))
                    s3 = ("SELECT DISTINCT date FROM %s where stock_id='2330'"%('price'))
                    
                    # 將日期抓出來並排序整理，放到self.dates中
                    df = (pd.read_sql(s1, self.conn).append(pd.read_sql(s2, self.conn)).append(pd.read_sql(s3, self.conn)).drop_duplicates('date').sort_values('date'))
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                    self.dates[tname] = df
                else:
                    # 將日期抓出來並排序整理，放到self.dates中
                    s = ("""SELECT DISTINCT date FROM '%s'"""%(tname))
                    self.dates[tname] = pd.read_sql(s, self.conn, parse_dates=['date'], index_col=['date']).sort_index()
                    
    def get(self, name, n):
        
        if name not in self.col2table or n == 0:
            print('Data: **ERROR: cannot find', name, 'in database')
            return pd.DataFrame()
        
        # 找出欲爬取的時間段（startdate, enddate）
        df = self.dates[self.col2table[name]].loc[:self.date].iloc[-n:]
        try:
            startdate = df.index[-1]
            enddate = df.index[0]
        except:
            print('Data: **WARRN: data cannot be retrieve completely:', name)
            enddate = df.iloc[0]
        
        # 假如該時間段已經在self.data中，則直接從self.data中拿取並回傳即可
        if name in self.data and self.contain_date(name, enddate, startdate):
            return self.date[name][enddate:startdate]
        
        # 從資料庫中拿取所需的資料
        s = ("""SELECT stock_id, date, [%s] FROM %s WHERE date BETWEEN '%s' AND '%s'"""%(name, 
            self.col2table[name], str(enddate.strftime('%Y-%m-%d')), 
            str((self.date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))))
        ret = pd.read_sql(s, self.conn, parse_dates=['date']).pivot(index='date', columns='stock_id')[name]
        
        
        # 將這些資料存入cache，以便將來要使用時，不需要從資料庫額外調出來
        if self.cache:
            self.data[name] = ret
        
        return ret
    
    
    
    # 確認該資料區間段是否已經存在self.data
    def contain_date(self, name, startdate, enddate):
        if name not in self.data:
            return False
        if self.data[name].index[0] <= startdate <= enddate <= self.data[name].index[-1]:
            return True
        
        return False
        