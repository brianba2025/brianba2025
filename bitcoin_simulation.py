import numpy as np
import pandas as pd

def simulate_bitcoin_price(days=60, start_price=50000, mu=0.0005, sigma=0.04):
    """
    Simulates Bitcoin price using Geometric Brownian Motion.
    mu: daily drift
    sigma: daily volatility
    """
    np.random.seed(1)  # For reproducibility (Seed 1 ensures a Golden Cross)
    returns = np.random.normal(mu, sigma, days)
    price_path = start_price * np.exp(np.cumsum(returns))

    # Prepend the start price
    price_path = np.insert(price_path, 0, start_price)

    dates = pd.date_range(start='2023-01-01', periods=days+1)
    df = pd.DataFrame({'Date': dates, 'Price': price_path})

    # Calculate Moving Averages
    df['MA7'] = df['Price'].rolling(window=7).mean()
    df['MA30'] = df['Price'].rolling(window=30).mean()

    return df

def run_trading_algorithm(df):
    cash = 10000.0
    position = 0.0  # BTC held
    ledger = []

    for i in range(len(df)):
        date = df.iloc[i]['Date']
        price = df.iloc[i]['Price']
        ma7 = df.iloc[i]['MA7']
        ma30 = df.iloc[i]['MA30']

        action = 'Hold'

        # Golden Cross Logic: MA7 crosses above MA30
        # Check if we have both MAs
        if not pd.isna(ma7) and not pd.isna(ma30):
            prev_ma7 = df.iloc[i-1]['MA7']
            prev_ma30 = df.iloc[i-1]['MA30']

            if prev_ma7 <= prev_ma30 and ma7 > ma30:
                # Buy
                if cash > 0:
                    position = cash / price
                    cash = 0
                    action = 'Buy'
            elif prev_ma7 >= prev_ma30 and ma7 < ma30:
                # Sell
                if position > 0:
                    cash = position * price
                    position = 0
                    action = 'Sell'

        portfolio_value = cash + (position * price)
        ledger.append({
            'Date': date,
            'Price': price,
            'MA7': ma7,
            'MA30': ma30,
            'Action': action,
            'Cash': cash,
            'Position': position,
            'Total Value': portfolio_value
        })

    return pd.DataFrame(ledger)

def print_report(ledger_df):
    print("Daily Trading Ledger:")
    print("-" * 110)
    print(f"{'Date':<12} | {'Price':<10} | {'MA7':<10} | {'MA30':<10} | {'Action':<6} | {'Total Value':<12}")
    print("-" * 110)

    for _, row in ledger_df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        price = f"{row['Price']:,.2f}"
        ma7 = f"{row['MA7']:,.2f}" if not pd.isna(row['MA7']) else "N/A"
        ma30 = f"{row['MA30']:,.2f}" if not pd.isna(row['MA30']) else "N/A"
        action = row['Action']
        total_value = f"${row['Total Value']:,.2f}"

        print(f"{date_str:<12} | {price:<10} | {ma7:<10} | {ma30:<10} | {action:<6} | {total_value:<12}")

    print("-" * 110)
    initial_value = ledger_df.iloc[0]['Total Value']
    final_value = ledger_df.iloc[-1]['Total Value']
    total_return = ((final_value - initial_value) / initial_value) * 100

    print(f"Initial Portfolio Value: ${initial_value:,.2f}")
    print(f"Final Portfolio Value:   ${final_value:,.2f}")
    print(f"Total Return:            {total_return:.2f}%")

if __name__ == "__main__":
    # Simulate 60 days of data
    df = simulate_bitcoin_price(60)

    # Run the trading algorithm
    ledger_df = run_trading_algorithm(df)

    # Print the report
    print_report(ledger_df)
