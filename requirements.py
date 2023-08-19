import requests
import bs4 as bs
import pickle
def save_tickers():
    # Send a GET request to a wiki page 
    # containing the S%P 500 tickers
    response = requests.get(
        'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        )
    
    # The GET request is saved in response. 
    # A GET request is a representation of the
    # wiki page
    
    # Use BeautifulSoup object to read the
    # response using an 'lxml' parser
    soup = bs.BeautifulSoup(
        response.text, # GET request
        'lxml'         # parser
        )
    
    '''
    <***table class="wikitable sortable"***id="constituents">

    <tbody><tr>
    <th><a href="/wiki/Ticker_symbol" title="Ticker symbol">Symbol</a>
    </th>
    <th>Security</th>
    <th><a href="/wiki/Global_Industry_Classification_Standard" 
            title="Global Industry Classification Standard">*GICS*
                </a> Sector</th>
    <th>GICS Sub-Industry</th>
    <th>Headquarters Location</th>
    <th>Date added</th>
    <th><a href="/wiki/Central_Index_Key" title="Central Index Key">CIK</a></th>
    <th>Founded
    </th></tr>
    '''
    
    # There are two table structures with class 'wikitable sortable'. 
    # Each of these contain the table row (tr) and table data (td)
    # with the needed company tickers. 
    
    # Create a BeautifulSoup object with each 
    # <table class="wikitable sortable" id="constituents">
    # in the Wiki page
    table = soup.find(
        'table',
        {'class': 'wikitable sortable'}
        )
    
    '''
    Each row 
    <tr>
        <th><a href="/wiki/Ticker_symbol" title="Ticker symbol">Symbol</a>
        </th>
        ...
    </tr>

    starts counting at 1, 2, 3, 4, ...
    Therefore the first row is Row 1 and we loop through 
    each one using this label
    '''
    
    # Save the tickers
    tickers = []
    for row in table.findAll('tr')[1:]:
        '''
        <tr>
            <td><a ...>TSLA</a></td>            [0]
            <td><a...</td>                      [1]
            <td>Consumer Discretionary</td>     [2]
            <td>Automobile Manufacturers</td>   ...
            <td><a exas</a></td>
            <td>2020-12-21</td>
            <td>0001318605</td>
            <td>2003</td>                       [n]
        </tr>
        
        The data entries for each table data start their counts 
        at 0. The entry we need is the ticker, and the ticker lies
        in table data [0]
        '''
        ticker = row.findAll('td')[0].text
        # Tickers is 'TSLA\n' 
        # strip the whitespace out
        ticker = ticker.strip()
        
        # Appens to the tickers array
        tickers.append(ticker)
        
        # Pickle the tickers array
        with open ("sp500tickers.pickle", "wb") as file:
            pickle.dump(tickers, file)
            
        return tickers
    
from pathlib import Path
import datetime as dt
import yfinance as yf
def get_stock_data(reload_sp500 = False):
    if reload_sp500:
        tickers = save_tickers()
    else:
        with open("sp500tickers.pickle", "rb") as file:
            tickers = pickle.load(file)
            
    
    # Store the individual stock price data 
    # in a new directory. 
    # Create the directory with pathlib
    # Current file directory: 
    # C:\...\stockenv\stock.py
    # Receive C:\...\stock\env
    source_directory = Path(__file__).parent
    # Create the stock_dfs directory path
    # C:\...\stockenv\stock_dfs
    dfs_path = source_directory / "stock_dfs"
    
    # Create the actual stock_dfs directory
    if not dfs_path.exists():
        dfs_path.mkdir()
        
    # Collect stock prices starting from 2010
    import pytz
    tz    = pytz.timezone("America/New_York")
    start = tz.localize(dt.datetime(2013, 1, 1))
    end   = tz.localize(dt.datetime.today())
    
    # For each element ['TSLA', 'NFLX', ...] 
    # in tickers, create a stock_dfs/TSLA directory
    for ticker in tickers:
        ticker_path = dfs_path / f"{ticker}.csv"
        if not ticker_path.exists():
            data = yf.download(
                ticker, 
                start, 
                end,
                auto_adjust = True
                )
            data.to_csv(ticker_path)
        else:
            print(f"Already have the {ticker} data.")
            
