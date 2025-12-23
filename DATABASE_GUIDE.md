# SQL Database for 4D Financial Visualization

This guide shows you how to use the SQL database pipeline for visualizing financial data in 4D space.

## Overview

Instead of using randomly generated data, you can now:
1. **Create a structured SQL database** with financial instrument data
2. **Calculate momentum metrics** automatically
3. **Visualize directly from the database** using our 4D model

## Database Structure

### Tables

#### 1. **Instruments** - The Assets
```sql
- instrument_id (Primary Key)
- symbol (e.g., 'AAPL', 'BTC')
- name (e.g., 'Apple Inc.')
- asset_type ('stock', 'crypto', 'forex', 'commodity')
```

#### 2. **PriceData** - The Raw OHLC Data
```sql
- price_id (Primary Key)
- instrument_id (Foreign Key)
- trade_date
- open_price
- high_price
- low_price
- close_price
- volume
```

#### 3. **MomentumMetrics** - The Calculated Dimensions
```sql
- metric_id (Primary Key)
- price_id (Foreign Key)
- momentum (1st derivative - OUR PRIMARY DIMENSION)
- momentum_percent
- intraday_change
- hidden_pressure (4th dimension)
- momentum_acceleration
- momentum_volatility
- price_volatility
- ... and more
```

#### 4. **vw_FullMarketData** - Combined View
A SQL view that joins all tables for easy querying.

## Quick Start

### Step 1: Create the Database

```bash
python create_database.py
```

**What this does:**
- Creates `market_data.db` (SQLite file)
- Adds 5 sample instruments (AAPL, GOOGL, MSFT, BTC, ETH)
- Generates 500 days of realistic price data for each
- Calculates all momentum metrics automatically
- Shows database statistics

**Output:**
```
✓ Database schema created successfully
✓ Added AAPL (ID: 1)
✓ Inserted 500 price records for AAPL
✓ Calculated and stored 500 metric records for AAPL
...
DATABASE STATISTICS
Instruments: 5
Price Records: 2500
Momentum Metrics: 2500
Date Range: 2023-01-02 to 2024-11-29
```

### Step 2: Visualize from Database

```bash
# Visualize a specific symbol
python visualize_from_database.py AAPL

# Or use default (AAPL)
python visualize_from_database.py
```

**What this does:**
- Loads data from the SQL database
- Creates 3 interactive visualizations:
  1. **4D color-encoded view** - Shows momentum × open × close (color = hidden pressure)
  2. **Temporal analysis** - Shows how variables evolve over time
  3. **Multiple projections** - Shows different 2D/3D views

**Output files:**
- `db_viz_AAPL_4d_color.html`
- `db_viz_AAPL_temporal.html`
- `db_viz_AAPL_projections.html`

### Step 3: Try Other Symbols

```bash
python visualize_from_database.py BTC
python visualize_from_database.py GOOGL
python visualize_from_database.py ETH
```

## Database Schema Reference

### View the Schema

The complete schema is in `schema.sql`. To view it:

```bash
cat schema.sql
```

Or open `market_data.db` with any SQLite browser:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (Free, cross-platform)
- [SQLiteStudio](https://sqlitestudio.pl/)
- VS Code extension: SQLite Viewer

## SQL Query Examples

### Example 1: Get All Data for a Symbol

```sql
SELECT * FROM vw_FullMarketData
WHERE symbol = 'AAPL'
ORDER BY trade_date;
```

### Example 2: Get Data for Visualization (Our 4 Dimensions)

```sql
SELECT
    trade_date,
    momentum,          -- Dimension 1
    open_price,        -- Dimension 2
    close_price,       -- Dimension 3
    hidden_pressure    -- Dimension 4 (hidden)
FROM vw_FullMarketData
WHERE symbol = 'AAPL'
ORDER BY trade_date;
```

### Example 3: Calculate Momentum Distribution

```sql
WITH MomentumBuckets AS (
    SELECT
        CASE
            WHEN momentum > 2 THEN 'Strong Up'
            WHEN momentum > 0 THEN 'Weak Up'
            WHEN momentum > -2 THEN 'Weak Down'
            ELSE 'Strong Down'
        END AS momentum_state,
        COUNT(*) as frequency
    FROM vw_FullMarketData
    WHERE symbol = 'AAPL'
    GROUP BY momentum_state
)
SELECT
    momentum_state,
    frequency,
    ROUND(CAST(frequency AS FLOAT) / SUM(frequency) OVER () * 100, 2) AS probability_pct
FROM MomentumBuckets;
```

**Output:**
```
momentum_state | frequency | probability_pct
Strong Up      | 85        | 17.00
Weak Up        | 215       | 43.00
Weak Down      | 180       | 36.00
Strong Down    | 20        | 4.00
```

This is similar to the "logit to probability" concept - showing the distribution of momentum states.

### Example 4: Find High Hidden Pressure Days

```sql
SELECT
    symbol,
    trade_date,
    close_price,
    momentum,
    hidden_pressure
FROM vw_FullMarketData
WHERE symbol = 'AAPL'
  AND ABS(hidden_pressure) > 1.5
ORDER BY ABS(hidden_pressure) DESC
LIMIT 10;
```

## Understanding the Dimensions

### 1. Momentum (X-axis)
- **What**: First derivative of price (rate of change)
- **Formula**: `close_price[t] - close_price[t-1]`
- **Meaning**: Velocity and direction of price movement
- **Positive**: Price accelerating upward
- **Negative**: Price accelerating downward

### 2. Open Price (Y-axis)
- **What**: Opening price of the period
- **Meaning**: Where the trading period started
- **Use**: Shows price level context

### 3. Close Price (Z-axis)
- **What**: Closing price of the period
- **Meaning**: Where the trading period ended
- **Use**: Shows final price level

### 4. Hidden Pressure (Color)
- **What**: Weighted combination of momentum dynamics
- **Formula**: `0.5×momentum + 0.3×intraday_change + 0.2×acceleration`
- **Meaning**: "Momentum-informed market pressure"
- **Green**: Strong positive pressure (momentum building)
- **Red**: Strong negative pressure (momentum declining)

## Adding Your Own Data

### Option 1: Modify the Generator

Edit `create_database.py` to add more instruments:

```python
instruments = [
    ('AAPL', 'Apple Inc.', 'stock'),
    ('YOUR_SYMBOL', 'Your Company', 'stock'),
    # Add more...
]
```

### Option 2: Import Real Data

If you have real CSV data:

```python
import pandas as pd
import sqlite3

# Load your CSV
df = pd.read_csv('your_data.csv')

# Connect to database
conn = sqlite3.connect('market_data.db')

# Insert price data
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO PriceData
        (instrument_id, trade_date, open_price, high_price, low_price, close_price, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (instrument_id, row['date'], row['open'], row['high'], row['low'], row['close'], row['volume']))

conn.commit()

# Then calculate metrics
# (Use the calculate_momentum_metrics function from create_database.py)
```

### Option 3: Connect to Real API

Example with yfinance (install: `pip install yfinance`):

```python
import yfinance as yf

# Download real data
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# Insert into your database
# (Similar to Option 2)
```

## Exporting Data

### Export to CSV

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('market_data.db')
df = pd.read_sql_query("SELECT * FROM vw_FullMarketData WHERE symbol = 'AAPL'", conn)
df.to_csv('AAPL_export.csv', index=False)
```

### Export to Excel

```python
df.to_excel('AAPL_export.xlsx', index=False)
```

## Visualizations Generated

### 1. 4D Color-Encoded View (`db_viz_{SYMBOL}_4d_color.html`)

**What it shows:**
- Interactive 3D scatter plot
- X-axis: Momentum
- Y-axis: Open Price
- Z-axis: Close Price
- Color: Hidden Pressure

**How to use:**
- Rotate: Click and drag
- Zoom: Scroll
- Hover: See exact values with date
- Look for color patterns and clusters

### 2. Temporal Analysis (`db_viz_{SYMBOL}_temporal.html`)

**What it shows (4 panels):**
1. **Price and Momentum over time** (dual-axis line chart)
2. **Momentum vs Intraday Change** (scatter plot showing relationship)
3. **Hidden Pressure evolution** (bar chart over time)
4. **3D momentum space** (same as #1 but smaller)

**How to use:**
- See how momentum precedes price changes
- Identify periods of high/low pressure
- Spot regime changes in the relationship

**This is where you see "how one variable change informs the next"**

### 3. Multiple Projections (`db_viz_{SYMBOL}_projections.html`)

**What it shows (4 panels):**
1. Momentum vs Open (2D)
2. Momentum vs Close (2D)
3. Open vs Close (2D)
4. Full 3D view

**How to use:**
- Compare different projections
- Each view reveals different patterns
- All colored by hidden pressure

## Understanding "How Changes Flow"

The **temporal analysis** visualization specifically shows how changes in one variable inform the next:

### Panel 1: Price and Momentum Time Series
- **Look at**: When momentum spikes (red line)
- **Then watch**: Does price follow? (blue line)
- **Pattern**: Momentum often leads price changes

### Panel 2: Momentum vs Intraday Scatter
- **X-axis**: Overall momentum (day-to-day change)
- **Y-axis**: Intraday change (open to close)
- **Color**: Hidden pressure
- **Pattern**: When they align (both positive or both negative), pressure is strong

### Panel 3: Hidden Pressure Bars
- **Green bars**: Positive pressure building → likely upward move next
- **Red bars**: Negative pressure building → likely downward move next
- **Pattern**: Clusters of same-color bars indicate regime

## Comparison with "Logits" Concept

You asked about "logits and their formulations" - here's how this relates:

### In Neural Networks:
- **Logits**: Raw scores before softmax
- **Softmax**: Converts to probabilities
- **Output**: Which token is most likely next

### In Our Financial Model:
- **Raw metrics**: Momentum, price, pressure (like logits)
- **Hidden pressure**: Weighted combination (like logit formula)
- **Visualization**: Shows which market state is most likely

### SQL Example (Similar to Softmax):

```sql
-- Calculate "probability" of each momentum state
WITH States AS (
    SELECT
        CASE
            WHEN momentum > 1 THEN 'Up'
            WHEN momentum < -1 THEN 'Down'
            ELSE 'Neutral'
        END AS state,
        COUNT(*) as count
    FROM vw_FullMarketData
    WHERE symbol = 'AAPL'
    GROUP BY state
)
SELECT
    state,
    count,
    ROUND(count * 100.0 / SUM(count) OVER (), 2) as probability_pct
FROM States;
```

**Output (like softmax probabilities):**
```
state    | count | probability_pct
Up       | 220   | 44.00
Neutral  | 180   | 36.00
Down     | 100   | 20.00
```

## Files in This Package

| File | Purpose |
|------|---------|
| `schema.sql` | Database structure definition |
| `create_database.py` | Creates and populates database |
| `visualize_from_database.py` | Creates visualizations from DB |
| `market_data.db` | SQLite database (generated) |
| `db_viz_*.html` | Generated visualizations |

## Next Steps

1. **Explore the sample data**: Run the scripts and open the visualizations
2. **Add your own data**: Modify `create_database.py` or import real data
3. **Customize metrics**: Edit the hidden pressure formula in the schema
4. **Build dashboards**: Use the database as backend for a web dashboard
5. **Train ML models**: Use the database to train predictive models

## Troubleshooting

### Database already exists
```bash
# Delete and recreate
rm market_data.db
python create_database.py
```

### Symbol not found
```bash
# Check available symbols
python visualize_from_database.py
# Look at the "Available symbols" section
```

### Import errors
```bash
pip install -r requirements.txt
```

## Summary

You now have a **complete SQL-based pipeline** for 4D financial visualization:

1. ✅ **Structured database** with instruments, prices, and momentum metrics
2. ✅ **Automatic calculations** of all dimensions including hidden pressure
3. ✅ **SQL queries** to analyze the data like you would with logits
4. ✅ **4D visualizations** showing momentum × open × close × pressure
5. ✅ **Temporal analysis** showing how changes flow between variables

**The key insight**: Just like logits flow through a neural network to predict the next token, momentum flows through our model to show the next market move!
