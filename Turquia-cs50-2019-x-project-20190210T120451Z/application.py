# Import required libraries
import os
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import re

# Import written functions
from helpers import apology, login_required, lookup, usd
from trial import beta, treasury
from fgs import portfol

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():

    # Remember the user
    id = session['user_id']
    # Set an int to store the value of the stocks
    m = db.execute("SELECT cash FROM users WHERE id =:id", id=id)
    cashathand = m[0]['cash']
    cash = 0
    stocks = db.execute("SELECT symbol, quantity FROM portfolio WHERE id = :id", id=id)
    # Get stock symbol, quantity, and price from database
    for stock in stocks:
        s = stock["symbol"]
        q = stock["quantity"]
        tmp = lookup(s)
        cp = tmp["price"]
        # Price paid
        pp = cp*q
        db.execute("UPDATE portfolio SET price=:price, total=:total WHERE id=:id AND symbol=:symbol",
                   price=usd(cp), total=usd(pp), id=id, symbol=s)
        cash = cash + pp

    totalcash = cash + cashathand
    data = db.execute("SELECT symbol,name,quantity,price,total FROM portfolio WHERE id=:id", id=id)

    return render_template("index.html", stocks=data, cash=usd(cashathand), total=usd(totalcash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # User reached route via post
    if request.method == "POST":

        quanti = request.form.get("shares")
        symbol = request.form.get("symbol")

        # Ensure symbol and number of shares are submitted
        if not symbol:
            return apology("Symbol could not be found")
        if not quanti:
            return apology("Please indicate the number of shares you would like to buy")
        # Convert quantity to an integer
        try:
            quant = int(quanti)
        except:
            return apology("Only integers dude")
        # Check positive quantity
        if quant <= 0:
            return apology("Only positive numbers can be bought")

        purchlist = lookup(symbol)
        # Check symbol exists
        if not purchlist:
            return apology("Cy@ -NB3 2K15")

        p = purchlist['price']
        s = purchlist['symbol']
        n = purchlist['name']
        id = session['user_id']

        m = db.execute("SELECT cash FROM users WHERE id = :id", id=id)
        # Get cash from database
        money = m[0]['cash']
        # Get beta
        bet = beta(symbol)
        # If cash is not enough to buy
        if money < p * quant:
            return apology("You are poor")
        oldq = db.execute("SELECT quantity FROM portfolio WHERE id=:id AND symbol=:symbol", id=id, symbol=s)
        # The user does not have stock
        if not oldq:

            db.execute("INSERT INTO portfolio (id, symbol, name, quantity, price, total, beta) VALUES (:id, :symbol, :name, :quantity, :price, :total, :beta)",
                       id=id, symbol=s, name=n, quantity=quant, price=p, total=0, beta=bet)
        else:

            oq = oldq[0]['quantity']

            db.execute("UPDATE portfolio SET quantity=:quantity WHERE id=:id AND symbol=:symbol", quantity= oq+quant, id=id, symbol=s)

        db.execute("UPDATE users SET cash = :cash  WHERE id = :id", id=id, cash=money - p*quant)

        db.execute("INSERT INTO history (id,price,quantity,symbol) VALUES (:id,:price,:quantity,:symbol)",id=id, price=usd(p), quantity=quant, symbol=s)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/portfolio")
@login_required
def portfolio():
    # Get user id
    id = session["user_id"]
    # Get risk-free rate
    rf = treasury()
    # Get portfolio beta
    port_bet = portfol(id)
    portbet = round(port_bet, 2)
    # Calculate expected return based on historical expected return --> Value taken from Introduction to Corporate Finance Brealey,Myers,Marcus
    exp_return = rf + portbet*(7-rf)
    expreturn = round(exp_return, 2)
    ret = 1 + (expreturn/100)
    stocks = db.execute("SELECT * FROM portfolio WHERE id=:id", id=id)
    # Set counter for total
    a = 0
    # Set counter for stock index array
    inarr = 0
    # Append stockreturn into list
    for stock in stocks:
        x = stock['beta']
        stock_ret = float(rf + x*(7-rf))
        stockret = round(stock_ret, 2)
        y = stock['symbol']
        stocks[inarr].update({'stockret': stockret})
        inarr += 1

    totals = db.execute("SELECT total FROM portfolio WHERE id=:id", id=id)
    # Ensure database data is collected with a little humor :)
    if not totals:
        return apology("System Broken :(")
    # Calculate total investment
    for total in totals:
        num = total['total']
        c = num[1:]
        b = float(c.replace(',', ''))
        a += b

    # Create graph
    # X Values
    years = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
    y_pos = np.arange(len(years))
    # Y Values
    InvestmentValue = [a, a*(ret**1), a*(ret**2), a*(ret**3), a*(ret**4), a*(ret**5), a*(ret**6), a*(ret**7), a*(ret**8), a*(ret**9)]
    # Plot bars
    plt.bar(y_pos, InvestmentValue, align='center', alpha=0.5)
    plt.xticks(y_pos, years)
    # Label axes
    plt.ylabel('Investment')
    plt.xlabel('Years')
    plt.title('InvestmentOver10Years')
    plt.show()
    # Save figure into css file
    plt.savefig('static/figure.1.jpg', bbox_inches='tight')

    return render_template("portfolio.html", stocks=stocks, totalin=usd(a), ereturn=expreturn, portbet=portbet)


@app.route("/history")
@login_required
def history():
    # Get id from session and transaction history from database
    id = session["user_id"]
    transactions = db.execute("SELECT * FROM history WHERE id = :id", id=id)
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/quote")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    # User reached route via post
    if request.method == "POST":
        id = session['user_id']
        # Import the typed-in value
        cashadd = request.form.get("addedcash")
        if not cashadd:
            return apology("Please enter the amount")
        # Check the value is digit and positive
        if not cashadd.isdigit():
            return apology("Added cash should be a positive integer")
        if cashadd < 0:
            return apology("Added cash should be positive")

        m = db.execute("SELECT cash FROM users WHERE id =:id", id=id)
        cashadded = int(cashadd)
        cashathand = m[0]['cash']
        # Update database cash
        db.execute("UPDATE users SET cash=:cash WHERE id=:id", cash=cashathand + cashadded, id=id)
        # Redirect user to main page
        return redirect("/")
    # User reached route via get
    else:
        return render_template("addcash.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    # User reached route via post
    if request.method == "POST":
        # Ensure the blank was filled
        if not request.form.get("symbol"):
            return apology("Please enter the symbol of the company.")
        # Get the written symbol of the company
        symbol = request.form.get("symbol")
        # Use the lookup func to get the name, price, and symbol
        dicti = lookup(symbol)
        # Check it is a valid symbol
        if not dicti:
            return apology("Stock symbol is unvalid")
        # Assign single elements
        n = dicti["name"]
        p = dicti["price"]
        s = dicti["symbol"]
        # Return quoted template with the assigned attributes
        return render_template("quoted.html", name=n, price=usd(p), symbol=s)
    # If it not post induce user to co-operate
    else:
        return render_template("quote.html")


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():

    # User reached route via post
    if request.method == "POST":
        id = session['user_id']
        # Collect filled-in data
        oldpw = request.form.get("oldpw")
        newpw = request.form.get("newpw")
        confirmpw = request.form.get("confirmpw")
        # Check filled-in data is collected
        if not oldpw:
            return apology("Please provide your current password")
        elif not newpw:
            return apology("Please provide your new password")
        elif not confirmpw:
            return apology("Please fill the confirmation tab")
        elif not newpw == confirmpw:
            return apology("Passwords do not match")
        # Check password length requirement
        if len(newpw) < 4:
            return apology("Length of password should be greater than 4 characters")
        # Check for digits
        if re.search(r"\d", newpw) is None:
            return apology("Password shall contain at least 1 digit")
        # Check for upper/lowercase chars
        if re.search(r"[A-Z]", newpw) is None or re.search(r"[a-z]", newpw) is None:
            return apology("Password shall contain uppercase/lowercase characters")
        # Check for symbol
        if re.search(r"\W", newpw) is None:
            return apology("Password shall contain at least one symbol")
        # Import old password
        hashed_oldpw = db.execute("SELECT hash FROM users WHERE id=:id", id=id)
        hashedoldpw = hashed_oldpw[0]['hash']
        # Compare typed-in old password and verified old password
        if check_password_hash(hashedoldpw, oldpw) is False:
            return apology("Passwords do not match")
        # Hash the new password
        hashednewpass = generate_password_hash(newpw)
        # Update database
        pw_changed = db.execute("UPDATE users SET hash=:hash WHERE id=:id", hash=hashednewpass, id=id)
        # Ensure password is changed
        if not pw_changed:
            return apology("Password could not be changed")
        return redirect("/")
    # User reached route via get
    else:
        return render_template("changepw.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via post
    if request.method == "POST":
        # ensure proper filling in the blanks
        if not request.form.get("username"):
            return apology("must provide username")

        elif not request.form.get("password"):
            return apology("must provide password")

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")
        # Compare password confirmation and password
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords shall match")

        datas = db.execute("SELECT username FROM users")
        # Check username match
        for key in datas:
            if key == request.form.get("username"):
                return apology("The username has already been taken")
        pw = request.form.get("password")
        # Ensure secure password
        # Check length
        if len(pw) < 4:
            return apology("Length of password should be greater than 4 characters")
        # Check for digits
        if re.search(r"\d", pw) is None:
            return apology("Password shall contain at least 1 digit")
        # Check for upper/lowercase chars
        if re.search(r"[A-Z]", pw) is None or re.search(r"[a-z]", pw) is None:
            return apology("Password shall contain uppercase/lowercase characters")
        # Check for symbol
        if re.search(r"\W",pw) is None:
            return apology("Password shall contain at least one symbol")

        # Hash the password
        hashedpass = generate_password_hash(request.form.get("password"))
        # Store the information in database
        usercreate = db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)",
                                username=request.form.get("username"), hash=hashedpass)
        # Ensure user is created
        if not usercreate:
            return apology("User could not be created")
        # Flash message
        flash("User has successfully been created")
        # Remember which user has logged in
        session["user_id"] = usercreate
        # Redirect user to the index page
        return redirect(url_for("quote"))
    # User reached route via get
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # Import user id
    id = session['user_id']
    # User reached route via post
    if request.method == "POST":
        # Ensure proper usage
        if not request.form.get("shares"):
            return apology("Plase indicate the number of shares you would like to sell")
        if not request.form.get("symbol"):
            return apology("Select the symbol you want to sell pls")
        # Convert selling quantity to an integer
        sellq = int(request.form.get("shares"))

        # Collect the symbol of the stock that is sold
        sym = request.form.get("symbol")
        # Gather relevant data from database
        data = db.execute("SELECT symbol,SUM(quantity) FROM portfolio WHERE id=:id AND symbol=:symbol GROUP BY symbol", id=id, symbol=sym)
        q = data[0]["SUM(quantity)"]
        c = db.execute("SELECT * FROM users WHERE id=:id", id=id)
        cashathand = c[0]['cash']
        # Check positive selling quantity
        if not sellq > 0:
            return apology("Selling quantity must be a positive int")
        # Check the number sold is less than or equal to owned
        if not sellq <= q:
            return apology("You cant sell more than you own")
        # Get the current price
        priceget = lookup(sym)
        price = priceget["price"]
        returnamount = sellq * price
        # Update cash
        db.execute("UPDATE users SET cash=:cash WHERE id=:id", cash=cashathand + returnamount, id=id)
        # Update quantity
        db.execute("UPDATE portfolio SET quantity = :quantity WHERE id =:id AND symbol=:symbol", quantity=q - sellq, id=id, symbol=sym)
        # Record transaction history
        db.execute("INSERT INTO history(id,price,quantity,symbol) VALUES (:id,:price,:quantity,:symbol)",
                   id=id, price=usd(price), quantity=0 - sellq, symbol=sym)
        # If the amount sold is equal to amount owned, delete the share record in user portfolio
        if sellq - q == 0:
            db.execute("DELETE FROM portfolio WHERE id=:id AND symbol=:symbol", id=id, symbol=sym)
        return redirect("/")
    # User reached route via get
    else:
        shares = db.execute("SELECT *FROM portfolio WHERE id =:id GROUP BY symbol", id=id)
        return render_template("sell.html", shares=shares)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)