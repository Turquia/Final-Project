from trial import treasury
from cs50 import SQL
db = SQL("sqlite:///finance.db")

# Function that calculates portfolio beta


def portfol(id):
    # Set portfolio beta counter
    portbet = 0
    # Set total counter
    a = 0
    # Get relevant data from database for stocks
    stocks = db.execute("SELECT total, beta FROM portfolio WHERE id=:id", id=id)
    # Ensure relevant data is collected
    if not stocks:
        return None
    print(stocks)
    # Get relevant data from database to calculate total investment
    totals = db.execute("SELECT total FROM portfolio WHERE id=:id", id=id)
    if not totals:
        return None
    print(totals)
    # Calculate total investment
    for total in totals:
        num = total['total']
        c = num[1:]
        b = float(c.replace(',', ''))
        print(b)
        a += b
    # Calculate stock weights
    for stock in stocks:
        num = stock['total']
        c = num[1:]
        stocktot = float(c.replace(',', ''))
        weight=stocktot/a
        portbet += stock['beta']*weight
    # Return portfolio beta
    return portbet