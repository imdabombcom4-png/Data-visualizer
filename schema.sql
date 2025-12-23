-- Financial Market Data Database Schema
-- This database stores OHLC (Open, High, Low, Close) data for financial instruments
-- and calculates momentum and other derived metrics

-- ============================================================
-- TABLE 1: Instruments (The Assets)
-- ============================================================
CREATE TABLE Instruments (
    instrument_id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100),
    asset_type VARCHAR(20), -- 'stock', 'crypto', 'forex', 'commodity'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2: Price Data (The Raw OHLC Data)
-- ============================================================
CREATE TABLE PriceData (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id INTEGER NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(18,8) NOT NULL,
    high_price DECIMAL(18,8) NOT NULL,
    low_price DECIMAL(18,8) NOT NULL,
    close_price DECIMAL(18,8) NOT NULL,
    volume BIGINT,
    FOREIGN KEY (instrument_id) REFERENCES Instruments(instrument_id),
    UNIQUE(instrument_id, trade_date)
);

-- Index for faster queries
CREATE INDEX idx_price_date ON PriceData(instrument_id, trade_date);

-- ============================================================
-- TABLE 3: Momentum Metrics (The Calculated Dimensions)
-- ============================================================
CREATE TABLE MomentumMetrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    price_id INTEGER NOT NULL,

    -- PRIMARY DIMENSIONS (for our 4D model)
    momentum DECIMAL(18,8),              -- First derivative (close[t] - close[t-1])
    momentum_percent DECIMAL(10,4),      -- Percentage change

    -- DERIVED FEATURES
    intraday_change DECIMAL(18,8),       -- close - open
    intraday_return DECIMAL(10,4),       -- (close - open) / open * 100
    gap DECIMAL(18,8),                   -- open[t] - close[t-1]

    -- MOMENTUM DERIVATIVES
    momentum_acceleration DECIMAL(18,8), -- Second derivative
    momentum_ma_5 DECIMAL(18,8),         -- 5-period moving average
    momentum_ma_10 DECIMAL(18,8),        -- 10-period moving average

    -- VOLATILITY
    momentum_volatility DECIMAL(18,8),   -- Rolling std of momentum
    price_volatility DECIMAL(18,8),      -- Rolling std of price

    -- HIDDEN DIMENSION (Our 4th dimension)
    hidden_pressure DECIMAL(18,8),       -- Weighted combination

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (price_id) REFERENCES PriceData(price_id)
);

-- ============================================================
-- VIEW: Combined Data (For Easy Querying)
-- ============================================================
CREATE VIEW vw_FullMarketData AS
SELECT
    i.symbol,
    i.name,
    i.asset_type,
    p.trade_date,
    p.open_price,
    p.high_price,
    p.low_price,
    p.close_price,
    p.volume,
    m.momentum,
    m.momentum_percent,
    m.intraday_change,
    m.intraday_return,
    m.hidden_pressure,
    m.momentum_acceleration,
    m.momentum_volatility
FROM Instruments i
JOIN PriceData p ON i.instrument_id = p.instrument_id
LEFT JOIN MomentumMetrics m ON p.price_id = m.price_id
ORDER BY i.symbol, p.trade_date;

-- ============================================================
-- QUERY EXAMPLES
-- ============================================================

-- Example 1: Get all data for a specific symbol
-- SELECT * FROM vw_FullMarketData WHERE symbol = 'AAPL';

-- Example 2: Get data for visualization (3 base dimensions + hidden)
-- SELECT
--     trade_date,
--     momentum,
--     open_price,
--     close_price,
--     hidden_pressure
-- FROM vw_FullMarketData
-- WHERE symbol = 'AAPL'
-- ORDER BY trade_date;

-- Example 3: Calculate Softmax-style probabilities for momentum states
-- (Similar to logit concept)
-- WITH MomentumBuckets AS (
--     SELECT
--         CASE
--             WHEN momentum > 2 THEN 'Strong Up'
--             WHEN momentum > 0 THEN 'Weak Up'
--             WHEN momentum > -2 THEN 'Weak Down'
--             ELSE 'Strong Down'
--         END AS momentum_state,
--         COUNT(*) as frequency
--     FROM vw_FullMarketData
--     WHERE symbol = 'AAPL'
--     GROUP BY momentum_state
-- )
-- SELECT
--     momentum_state,
--     frequency,
--     ROUND(CAST(frequency AS FLOAT) / SUM(frequency) OVER () * 100, 2) AS probability_pct
-- FROM MomentumBuckets;
