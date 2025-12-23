# Momentum-Based 4D Visualization Model

## Key Change: Momentum Instead of Previous Price

This enhanced model uses **momentum (derivative)** as the first dimension instead of previous price, providing a fundamentally different perspective on market dynamics.

## The Three Base Dimensions

### 1. Momentum (Derivative) - The Velocity Dimension
- **What it is**: Rate of price change (first derivative)
- **Formula**: `momentum = price[t] - price[t-1]`
- **What it shows**: The **velocity** and **direction** of price movement
- **Why it matters**: Captures market dynamics better than static price levels

### 2. Open Price
- The opening price for the trading period
- Represents the initial market consensus

### 3. Close Price
- The closing price for the trading period
- Represents the final market consensus

## The Fourth (Hidden) Dimension

The hidden dimension is discovered through analysis and represents **"momentum-informed pressure"**:

```
hidden_pressure = 0.5 × momentum + 0.3 × intraday_change + 0.2 × acceleration
```

This captures:
- **Current momentum** (50%): How fast prices are moving
- **Intraday action** (30%): What happened during the day
- **Acceleration** (20%): Is momentum increasing or decreasing?

## Key Results from Analysis

### PCA Analysis - Much Better Variance Distribution!

```
Component 1: 66.77%  <- Price level variation
Component 2: 33.17%  <- Momentum variation
Component 3: 0.06%   <- Residual
```

**This is MUCH better than the price-based model (which had 99.91% in PC1)!**

**What this means:**
- The momentum dimension adds **real independent information** (33% variance)
- The 3D space is truly 3-dimensional, not nearly a line
- Two major factors: overall price level (67%) and price velocity (33%)
- The data has richer structure for analysis

### Component Contributions

```
     momentum   open  close
PC1     0.075  0.704  0.706  <- Price level (open and close move together)
PC2     0.997 -0.071 -0.035  <- Pure momentum dimension
PC3    -0.025 -0.706  0.708  <- Open-close differential
```

**Interpretation:**
- **PC1**: Captures overall price level (open and close contribute equally)
- **PC2**: Captures pure momentum (almost entirely from momentum dimension)
- **PC3**: Captures the spread between open and close (intraday movement)

### Machine Learning Results - Better Predictive Power!

```
Train R² score: 0.4124
Test R² score: 0.2089

Feature importances:
  momentum: 0.644  <- Most important!
  close: 0.195
  open: 0.161
```

**Key insights:**
- **Current momentum is the best predictor of future momentum** (64.4%)
- Close price adds some context (19.5%)
- Open price adds minimal information (16.1%)
- Better test score (0.21 vs 0.10) suggests the model generalizes better

## Comparison: Price-Based vs Momentum-Based

| Aspect | Price-Based Model | Momentum-Based Model |
|--------|------------------|---------------------|
| **First dimension** | Previous Price | Momentum (derivative) |
| **Information type** | Static levels | Dynamic velocity |
| **PC1 variance** | 99.91% | 66.77% |
| **PC2 variance** | 0.08% | 33.17% |
| **Dimensionality** | Nearly 1D | True 3D |
| **ML Test R²** | 0.10 | 0.21 |
| **Best predictor** | Close (50%) | Momentum (64%) |
| **Use case** | Price levels | Market dynamics |

## Visualizations Generated

### 1. momentum_viz_1_color_encoding.html ⭐ **START HERE**
- **3D scatter**: Momentum × Open × Close
- **Color**: Hidden pressure (momentum-informed)
- **Best for**: Seeing momentum patterns and regimes
- **Look for**: Color clusters showing different market conditions

### 2. momentum_viz_2_size_encoding.html
- **3D scatter**: Same axes
- **Size**: Hidden pressure
- **Best for**: Identifying magnitude of momentum-pressure events

### 3. momentum_viz_3_multiple_projections.html
- **Four views**: Three 2D + one 3D
- **Best for**: Understanding how momentum relates to price levels
- **Look for**: Patterns across different projection angles

### 4. momentum_viz_4_ml_discovered.html
- **3D scatter**: Same axes
- **Color**: ML-predicted future momentum
- **Best for**: Seeing what patterns predict momentum continuation/reversal
- **Compare with**: viz_1 to see engineered vs learned dimensions

### 5. momentum_viz_5_dynamics.html ⭐ **NEW - TIME DIMENSION**
- **Row 1**: Price and momentum over time (dual-axis)
- **Row 2**: Momentum vs intraday change scatter
- **Row 3**: 3D momentum-open-close view
- **Best for**: Understanding temporal relationships and causality

## How to Interpret the Visualizations

### Understanding Momentum Patterns

1. **Positive momentum (right side of 3D plot)**:
   - Prices accelerating upward
   - Look at color to see if pressure supports continuation

2. **Negative momentum (left side of 3D plot)**:
   - Prices accelerating downward
   - Color shows if selling pressure is building or exhausting

3. **Near-zero momentum (center)**:
   - Consolidation or reversal zones
   - Color reveals hidden pressure that may drive next move

### Color Interpretation (Hidden Pressure)

- **Green**: High positive pressure (momentum + intraday strength + acceleration)
- **Yellow**: Neutral pressure
- **Red**: High negative pressure (momentum declining + weakness + deceleration)

### Patterns to Look For

1. **Momentum clusters**: Groups of similar momentum at different price levels
   - May indicate consistent market regime

2. **Color gradients**: Smooth transitions suggest steady trends
   - Sharp color changes suggest regime shifts

3. **Divergences**: When momentum direction doesn't match color
   - E.g., positive momentum with red color = weakening rally
   - E.g., negative momentum with green color = oversold bounce coming

## Practical Applications

### 1. Trend Identification
- Look for sustained positive or negative momentum zones
- Color confirms if the trend has supporting pressure

### 2. Reversal Detection
- Look for momentum extremes with opposite-colored pressure
- E.g., Strong negative momentum with green pressure = potential bottom

### 3. Consolidation Recognition
- Look for momentum clustering near zero
- Multiple colors suggest indecision

### 4. Regime Changes
- Look for sudden shifts in the momentum-price-pressure relationship
- Color pattern changes indicate regime shifts

## Technical Implementation Details

### Data Generation
- **500 trading days** of sample data (excludes weekends)
- Includes realistic patterns:
  - Trend component
  - Random walk noise
  - Overnight gaps
  - Intraday mean reversion

### Momentum Calculation
```python
momentum = price[t] - price[t-1]  # First derivative
```

### Hidden Dimension Calculation
```python
hidden_pressure = (
    0.5 * momentum +              # Current velocity
    0.3 * intraday_change +       # Daily action
    0.2 * momentum_acceleration   # Second derivative
)
```

### ML Model
- **Algorithm**: Random Forest Regressor
- **Target**: Future momentum (next period)
- **Features**: Current momentum, open, close
- **Purpose**: Discover predictive patterns

## Running the Prototype

```bash
python prototype_momentum_4d_viz.py
```

**Output:**
- 5 interactive HTML visualizations
- Console output with PCA and ML analysis
- All files prefixed with `momentum_viz_`

## Why This Model is Better

### 1. Captures Market Dynamics
- Momentum shows **velocity**, not just position
- Better for understanding market behavior

### 2. True Multi-Dimensional Structure
- 67% / 33% variance split shows two real dimensions
- Not compressed into nearly 1D like price-based model

### 3. Better Predictive Power
- Test R² of 0.21 vs 0.10
- Momentum is the strongest predictor (64%)

### 4. More Interpretable Patterns
- Momentum clusters reveal market regimes
- Color (pressure) adds actionable context
- Easier to spot reversals and trend changes

### 5. Temporally Informative
- Shows how price velocity relates to levels
- Reveals acceleration/deceleration patterns
- Better for understanding causality

## Next Steps

With this momentum-based foundation, we can build:

1. **Real-time dashboard** with live data feeds
2. **Custom momentum calculations** (RSI, MACD, etc.)
3. **Multi-timeframe analysis** (different period lengths)
4. **Predictive models** trained on real historical data
5. **Alert system** for pattern detection
6. **Portfolio view** showing multiple instruments

## Key Takeaway

**Using momentum (derivative) instead of previous price transforms the visualization from showing "where prices are" to showing "how prices are moving" - a fundamentally more useful perspective for understanding market dynamics.**

The 3D space now represents:
- **X-axis (Momentum)**: How fast and in what direction?
- **Y-axis (Open)**: Where did we start?
- **Z-axis (Close)**: Where did we end up?
- **Color (Hidden)**: What's the underlying pressure?

This creates a powerful framework for understanding the interplay between price movement, price levels, and hidden market forces!
