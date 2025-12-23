"""
Create and Populate Financial Market Database

This script creates a SQLite database with financial instrument data,
calculates momentum metrics, and prepares data for 4D visualization.

Usage:
    python create_database.py

Output:
    - market_data.db (SQLite database file)
    - Console output showing database statistics
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class MarketDatabase:
    """Create and manage financial market database"""

    def __init__(self, db_path='market_data.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None

    def create_database(self):
        """Create the database and all tables"""
        print(f"Creating database: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Read and execute schema
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            # Execute each statement separately
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)

        self.conn.commit()
        print("✓ Database schema created successfully")

    def add_instrument(self, symbol, name, asset_type='stock'):
        """Add a new instrument to the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Instruments (symbol, name, asset_type)
            VALUES (?, ?, ?)
        """, (symbol, name, asset_type))
        self.conn.commit()
        return cursor.lastrowid

    def generate_sample_price_data(self, instrument_id, symbol, n_days=500, start_price=100):
        """Generate realistic sample price data"""
        print(f"Generating {n_days} days of data for {symbol}...")

        np.random.seed(42 + instrument_id)  # Different seed per instrument

        # Generate trading dates (skip weekends)
        start_date = datetime(2023, 1, 1)
        dates = []
        current_date = start_date
        while len(dates) < n_days:
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                dates.append(current_date)
            current_date += timedelta(days=1)

        # Generate realistic price data
        trend = np.linspace(0, 20, n_days)  # Upward trend
        noise = np.cumsum(np.random.randn(n_days) * 0.5)
        base_close = start_price + trend + noise

        price_data = []
        for i, date in enumerate(dates):
            # Close price
            close = base_close[i]

            # Open price (with gap from previous close)
            if i == 0:
                open_price = close + np.random.randn() * 0.3
            else:
                gap = np.random.randn() * 0.4
                open_price = base_close[i-1] + gap

            # High and low for the day
            intraday_range = abs(np.random.randn()) * 0.8
            high = max(open_price, close) + intraday_range * np.random.rand()
            low = min(open_price, close) - intraday_range * np.random.rand()

            # Volume
            volume = int(np.random.uniform(1000000, 10000000))

            price_data.append({
                'instrument_id': instrument_id,
                'trade_date': date.strftime('%Y-%m-%d'),
                'open_price': round(open_price, 4),
                'high_price': round(high, 4),
                'low_price': round(low, 4),
                'close_price': round(close, 4),
                'volume': volume
            })

        # Insert into database
        cursor = self.conn.cursor()
        cursor.executemany("""
            INSERT INTO PriceData
            (instrument_id, trade_date, open_price, high_price, low_price, close_price, volume)
            VALUES (:instrument_id, :trade_date, :open_price, :high_price, :low_price, :close_price, :volume)
        """, price_data)
        self.conn.commit()

        print(f"✓ Inserted {len(price_data)} price records for {symbol}")
        return len(price_data)

    def calculate_momentum_metrics(self, instrument_id, symbol):
        """Calculate all momentum and derived metrics"""
        print(f"Calculating momentum metrics for {symbol}...")

        # Load price data
        df = pd.read_sql_query("""
            SELECT price_id, trade_date, open_price, close_price
            FROM PriceData
            WHERE instrument_id = ?
            ORDER BY trade_date
        """, self.conn, params=(instrument_id,))

        # Calculate momentum (first derivative)
        df['momentum'] = df['close_price'].diff()
        df['momentum_percent'] = df['close_price'].pct_change() * 100

        # Intraday metrics
        df['intraday_change'] = df['close_price'] - df['open_price']
        df['intraday_return'] = (df['intraday_change'] / df['open_price']) * 100

        # Gap (open vs previous close)
        df['gap'] = df['open_price'] - df['close_price'].shift(1)

        # Momentum derivatives
        df['momentum_acceleration'] = df['momentum'].diff()
        df['momentum_ma_5'] = df['momentum'].rolling(window=5).mean()
        df['momentum_ma_10'] = df['momentum'].rolling(window=10).mean()

        # Volatility
        df['momentum_volatility'] = df['momentum'].rolling(window=10).std()
        df['price_volatility'] = df['close_price'].rolling(window=10).std()

        # HIDDEN PRESSURE (4th dimension)
        # Weighted combination of momentum, intraday change, and acceleration
        df['hidden_pressure'] = (
            0.5 * df['momentum'].fillna(0) +
            0.3 * df['intraday_change'].fillna(0) +
            0.2 * df['momentum_acceleration'].fillna(0)
        )

        # Prepare for database insertion
        metrics_data = []
        for _, row in df.iterrows():
            metrics_data.append({
                'price_id': row['price_id'],
                'momentum': row['momentum'],
                'momentum_percent': row['momentum_percent'],
                'intraday_change': row['intraday_change'],
                'intraday_return': row['intraday_return'],
                'gap': row['gap'],
                'momentum_acceleration': row['momentum_acceleration'],
                'momentum_ma_5': row['momentum_ma_5'],
                'momentum_ma_10': row['momentum_ma_10'],
                'momentum_volatility': row['momentum_volatility'],
                'price_volatility': row['price_volatility'],
                'hidden_pressure': row['hidden_pressure']
            })

        # Insert metrics
        cursor = self.conn.cursor()
        cursor.executemany("""
            INSERT INTO MomentumMetrics
            (price_id, momentum, momentum_percent, intraday_change, intraday_return,
             gap, momentum_acceleration, momentum_ma_5, momentum_ma_10,
             momentum_volatility, price_volatility, hidden_pressure)
            VALUES (:price_id, :momentum, :momentum_percent, :intraday_change, :intraday_return,
                    :gap, :momentum_acceleration, :momentum_ma_5, :momentum_ma_10,
                    :momentum_volatility, :price_volatility, :hidden_pressure)
        """, metrics_data)
        self.conn.commit()

        print(f"✓ Calculated and stored {len(metrics_data)} metric records for {symbol}")

    def print_statistics(self):
        """Print database statistics"""
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)

        # Instruments
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Instruments")
        print(f"\nInstruments: {cursor.fetchone()[0]}")

        # Price records
        cursor.execute("SELECT COUNT(*) FROM PriceData")
        print(f"Price Records: {cursor.fetchone()[0]}")

        # Metrics records
        cursor.execute("SELECT COUNT(*) FROM MomentumMetrics")
        print(f"Momentum Metrics: {cursor.fetchone()[0]}")

        # Date range
        cursor.execute("SELECT MIN(trade_date), MAX(trade_date) FROM PriceData")
        min_date, max_date = cursor.fetchone()
        print(f"Date Range: {min_date} to {max_date}")

        # Sample data
        print("\n" + "="*60)
        print("SAMPLE DATA (First 5 records)")
        print("="*60)
        df = pd.read_sql_query("""
            SELECT * FROM vw_FullMarketData
            LIMIT 5
        """, self.conn)
        print(df.to_string(index=False))

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print(f"\n✓ Database saved to: {self.db_path}")


def main():
    """Create and populate the market database"""
    print("\n" + "="*60)
    print("FINANCIAL MARKET DATABASE CREATOR")
    print("="*60 + "\n")

    db = MarketDatabase('market_data.db')

    # Create database structure
    db.create_database()

    # Add sample instruments
    print("\nAdding instruments...")
    instruments = [
        ('AAPL', 'Apple Inc.', 'stock'),
        ('GOOGL', 'Alphabet Inc.', 'stock'),
        ('MSFT', 'Microsoft Corporation', 'stock'),
        ('BTC', 'Bitcoin', 'crypto'),
        ('ETH', 'Ethereum', 'crypto'),
    ]

    for symbol, name, asset_type in instruments:
        instrument_id = db.add_instrument(symbol, name, asset_type)
        print(f"✓ Added {symbol} (ID: {instrument_id})")

        # Generate price data
        start_price = np.random.uniform(50, 200)
        db.generate_sample_price_data(instrument_id, symbol, n_days=500, start_price=start_price)

        # Calculate metrics
        db.calculate_momentum_metrics(instrument_id, symbol)

    # Print statistics
    db.print_statistics()

    # Close database
    db.close()

    print("\n" + "="*60)
    print("DATABASE CREATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Open market_data.db with any SQLite browser")
    print("2. Run: python visualize_from_database.py")
    print("3. Explore the 4D visualizations!\n")


if __name__ == "__main__":
    main()
