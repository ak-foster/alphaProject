import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np

today = datetime.date.today()

# Pre-processing for now, will include in __main__ later. Configure data source
df = pd.read_csv('historicalPriceData.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
dfl = df['2016-01-01':today]


# dfl.to_csv('test.csv')


class MovingAverageCrossStrategy():
    """
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""

    def __init__(self, symbol, bars, short_window=30, long_window=120):
        self.symbol = symbol
        self.bars = bars

        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals
        to go long, short or hold (1, -1 or 0)."""
        signals = pd.DataFrame(index=dfl.index)
        signals['signal'] = 0.0

        # Set number of days to be used for calculating a moving average
        S = 30
        M = 90
        L = 120

        """
        # Create the set of short and long simple moving averages over the
        # respective periods
        for t in timePeriods:
            signals[str(t) + 'd_SMA'] = bars['Close'].rolling(window=t, center=False, min_periods=1).mean()
        """
        signals['short_mavg'] = bars['Close'].rolling(window=S, center=False, min_periods=1).mean()
        signals['long_mavg'] = bars['Close'].rolling(window=L, center=False, min_periods=1).mean()

        # Create a 'signal' (invested or not invested) when the short moving average crosses the long
        # moving average, but only for the period greater than the shortest moving average window
        signals['signal'][:] = np.where(signals['short_mavg'][:] > signals['long_mavg'][:], 1.0, 0.0)

        # Take the difference of the signals in order to generate actual trading orders
        signals['positions'] = signals['signal'].diff()

        # signals.to_csv('signals.csv', header=True)
        return signals


class MarketOnClosePortfolio():
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:q
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()

    def generate_positions(self):
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions[self.symbol] = 10 * signals['signal']  # This strategy buys 10 shares

        # positions.to_csv('positions.csv', header=True)
        return positions

    def backtest_portfolio(self):
        portfolio = pd.DataFrame(index=bars.index).fillna(0.0)
        portfolio[self.symbol] = self.positions[self.symbol] * self.bars['Close']
        pos_diff = self.positions.diff()

        portfolio['holdings'] = portfolio.sum(axis=1)
        portfolio['cash'] = self.initial_capital - (pos_diff[self.symbol] * self.bars['Close']).cumsum(axis=0)
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()

        # portfolio.to_csv('portfolio_returns.csv', header=True)
        return portfolio


if __name__ == "__main__":
    # Obtain daily bars for stock or index from Yahoo Finance or other local source
    symbol = 'SP500'
    bars = dfl

    # Create a Moving Average Cross Strategy instance with a short moving
    # average window of 30 days and a long window of 120 days
    mac = MovingAverageCrossStrategy(symbol, bars, short_window=30, long_window=120)
    signals = mac.generate_signals()

    # Create a portfolio with $100,000 initial capital
    portfolio = MarketOnClosePortfolio(symbol, bars, signals, initial_capital=100000.0)
    returns = portfolio.backtest_portfolio()


def plot_chart():
    # Plot two charts to assess trades and equity curve
    fig = plt.figure()
    fig.patch.set_facecolor('white')  # Set the outer colour to white
    ax1 = fig.add_subplot(211, ylabel='Price in $')

    def plotPerformance():
        # Plot the closing price overlaid with the moving averages
        bars['Close'].plot(ax=ax1, color='r', lw=2.)
        signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)

        # Plot the "buy" trades against closing price
        ax1.plot(signals.loc[signals.positions == 1.0].index,
                 signals.short_mavg[signals.positions == 1.0],
                 '^', markersize=10, color='m')

        # Plot the "sell" trades against closing price
        ax1.plot(signals.loc[signals.positions == -1.0].index,
                 signals.short_mavg[signals.positions == -1.0],
                 'v', markersize=10, color='k')

    def plotReturns():
        # Plot the equity curve in dollars
        ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
        returns['total'].plot(ax=ax2, lw=2.)

        # Plot the "buy" and "sell" trades against the equity curve
        ax2.plot(returns.loc[signals.positions == 1.0].index,
                 returns.total[signals.positions == 1.0],
                 '^', markersize=10, color='m')
        ax2.plot(returns.loc[signals.positions == -1.0].index,
                 returns.total[signals.positions == -1.0],
                 'v', markersize=10, color='k')
    plotPerformance()
    plotReturns()
    # Plot the figure
    fig.show()


plot_chart()
