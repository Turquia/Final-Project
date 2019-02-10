import quandl
from pls import parse
import requests

# Get stock beta using parse function


def beta(symbol):
    ticker = symbol
    a = parse(ticker)
    # Check ticker exists
    if not a:
        return None
    # Convert the list into a dict
    b = dict(a)
    c = b['Beta (3Y Monthly)']
    # Return beta
    return c
# Get treasury bill return using quandl connection


def treasury():
    # Get the data and parse respons using json
    data = requests.get("https://www.quandl.com/api/v3/datasets/USTREASURY/YIELD.json?api_key=bWxxscnygedM6bp2tGjq&start_date=2019-01-23&end_date=2019-01-23").json()
    # Check data is collected
    if not data:
        return None
    # Convert list to dict
    c = dict(data)
    # Get 10 YR treasury bill return
    a = c['dataset']['data'][0][10]
    # Return treasury bill yield
    return a

