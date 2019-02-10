Investments101

Basically my final project is developed further based on CS50 finance, and it capitalizes Markowitz Portfolio theory in order to build a stock portfolio that takes risk and return relationship into account.
This is done by using the following formula:
portfolioreturn = risk-free-rate + ß(marketreturn - risk-free-rate)
The project imports risk free rate using quandl connection, beta is imported via parsing the response from yahoo finance, and market return value is taken from
Introduction to Corporate Finance book by Brealey,Myers, and Marcus. The reason static value is used for historical return is that CAPM theory is a long-term calculation,
and as indicated in the book as well, the historical return of the stock market tends to be smooth in the long-run.

After making the calculation, portfolio return is calculated by taking stock weights in the portfolio into account. This allows to compute the return of the overall portfolio for 1 year, and
investment value over the years is shown by using a dynamic bar plot that allows the users to make more efficient decisions on their portfolio.

Furthermore, many additions to CS50 finance have been made:
- Addcash tab
- Javascript in the quote page to allow users the historical performance of chosen stocks that are selected by investment companies.
- Password security in login
- Change password tab

Overall, the project successfully illustrates the relationship between risk and return, via leveraging the imported values using API connections,
and plots the investment value over the years on a bar graph that allows users to make their decisions based on historical performance of stocks
and their risk tolerance.

