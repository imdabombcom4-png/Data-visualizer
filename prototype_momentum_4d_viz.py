"""
4D Financial Data Visualization Prototype - Momentum-Based

This prototype demonstrates different techniques for visualizing 4-dimensional
relationships in financial instrument data:
- Momentum/Derivative (dimension 1) - rate of price change
- Open Price (dimension 2)
- Close Price (dimension 3)
- Hidden Dimension (dimension 4) - to be discovered

Key difference from original: Uses momentum (velocity) instead of price level
as the first dimension to better capture market dynamics.

Visualization techniques demonstrated:
1. PCA analysis to find hidden patterns
2. Color encoding (4th dimension as color in 3D space)
3. Size encoding (4th dimension as marker size)
4. Multiple projections
5. Machine learning to discover the hidden dimension
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MomentumFinancialData4D:
    """Generate and analyze 4D financial data with momentum as primary dimension"""

    def __init__(self, n_days=500, seed=42):
        """
        Initialize with sample financial data

        Args:
            n_days: Number of trading days to generate
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.n_days = n_days
        self.df = self._generate_sample_data()

    def _generate_sample_data(self):
        """Generate realistic sample financial data with hidden patterns"""
        # Generate dates (trading days only - skip weekends)
        start_date = datetime(2023, 1, 1)
        dates = []
        current_date = start_date
        while len(dates) < self.n_days:
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                dates.append(current_date)
            current_date += timedelta(days=1)

        # Generate base price with trend and noise
        trend = np.linspace(100, 120, self.n_days)
        noise = np.cumsum(np.random.randn(self.n_days) * 0.5)
        base_price = trend + noise

        # Generate open price with overnight gap
        gap = np.random.randn(self.n_days) * 0.4
        open_price = base_price + gap

        # Generate close price with intraday movement
        intraday_movement = np.random.randn(self.n_days) * 0.6
        # Add mean reversion: if gap is large, price tends to reverse
        mean_reversion = -gap * 0.4
        close_price = open_price + intraday_movement + mean_reversion

        # Calculate MOMENTUM as the derivative (rate of change)
        # This is the key difference: momentum instead of previous price
        price_change = np.diff(close_price, prepend=close_price[0])
        momentum = price_change  # First derivative

        # Alternative momentum calculations
        momentum_percent = np.zeros(self.n_days)
        momentum_percent[1:] = (close_price[1:] - close_price[:-1]) / close_price[:-1] * 100

        df = pd.DataFrame({
            'date': dates,
            'open': open_price,
            'close': close_price,
            'momentum': momentum,  # PRIMARY DIMENSION: rate of change
            'momentum_percent': momentum_percent,  # % change
        })

        return df

    def calculate_derived_features(self):
        """Calculate various features that might reveal hidden dimensions"""
        df = self.df.copy()

        # Intraday movement
        df['intraday_change'] = df['close'] - df['open']
        df['intraday_return'] = (df['close'] - df['open']) / df['open'] * 100

        # Momentum derivatives (acceleration)
        df['momentum_acceleration'] = df['momentum'].diff()  # Second derivative

        # Moving averages of momentum
        df['momentum_ma_5'] = df['momentum'].rolling(window=5).mean()
        df['momentum_ma_10'] = df['momentum'].rolling(window=10).mean()

        # Volatility measures
        df['momentum_volatility'] = df['momentum'].rolling(window=10).std()
        df['price_volatility'] = df['close'].rolling(window=10).std()

        # Price position relative to recent range
        rolling_high = df['close'].rolling(window=20).max()
        rolling_low = df['close'].rolling(window=20).min()
        df['price_position'] = (df['close'] - rolling_low) / (rolling_high - rolling_low)

        # Momentum divergence: when momentum and price action diverge
        price_direction = np.sign(df['intraday_change'])
        momentum_direction = np.sign(df['momentum'])
        df['momentum_divergence'] = (price_direction != momentum_direction).astype(float)

        # HIDDEN DIMENSION CANDIDATE: Combines momentum dynamics with intraday action
        # This represents "momentum-informed price pressure"
        df['hidden_pressure'] = (
            0.5 * df['momentum'] +  # Current momentum
            0.3 * df['intraday_change'] +  # Intraday movement
            0.2 * df['momentum_acceleration'].fillna(0)  # Acceleration
        )

        # Alternative hidden dimension: Momentum-adjusted volatility
        df['momentum_vol_ratio'] = df['momentum'].abs() / (df['momentum_volatility'] + 0.001)

        return df

    def perform_pca_analysis(self, df):
        """Use PCA to find principal components and explained variance"""
        # Use momentum, open, close as the 3 base dimensions
        features = ['momentum', 'open', 'close']
        X = df[features].dropna().values

        # Standardize the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Apply PCA
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X_scaled)

        print("=" * 60)
        print("PCA ANALYSIS - MOMENTUM-BASED MODEL")
        print("=" * 60)
        print("\nBase dimensions: Momentum, Open, Close")
        print("\nVariance explained by each component:")
        for i, var in enumerate(pca.explained_variance_ratio_):
            print(f"  Component {i+1}: {var:.2%}")
        print(f"\nTotal variance explained: {pca.explained_variance_ratio_.sum():.2%}")

        print("\nPCA Components (how each feature contributes):")
        components_df = pd.DataFrame(
            pca.components_,
            columns=features,
            index=['PC1', 'PC2', 'PC3']
        )
        print(components_df.round(3))
        print()

        return X_pca, pca, scaler

    def train_ml_model(self, df_features):
        """Train ML model to discover hidden dimension"""
        # Create a target: future momentum (what we're trying to predict)
        df_features['future_momentum'] = df_features['momentum'].shift(-1)

        # Prepare data
        features = ['momentum', 'open', 'close']
        df_clean = df_features.dropna()
        X = df_clean[features]
        y = df_clean['future_momentum']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
        model.fit(X_train, y_train)

        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)

        print("=" * 60)
        print("MACHINE LEARNING ANALYSIS - MOMENTUM MODEL")
        print("=" * 60)
        print(f"\nPredicting: Future Momentum (next period's price velocity)")
        print(f"Train R² score: {train_score:.4f}")
        print(f"Test R² score: {test_score:.4f}")

        print("\nFeature importances (how much each dimension matters):")
        for feature, importance in zip(features, model.feature_importances_):
            print(f"  {feature}: {importance:.3f}")

        # Predict on all data (for visualization)
        df_features['ml_hidden_dim'] = np.nan
        df_features.loc[X.index, 'ml_hidden_dim'] = model.predict(X)

        print()
        return model, df_features


def visualize_4d_color_encoding(df, title="4D Visualization - Momentum Model (Color Encoding)"):
    """Create 3D scatter plot with 4th dimension as color"""
    df_clean = df.dropna()

    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean['momentum'],
        y=df_clean['open'],
        z=df_clean['close'],
        mode='markers',
        marker=dict(
            size=4,
            color=df_clean['hidden_pressure'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Hidden<br>Pressure", x=1.1),
            line=dict(width=0)
        ),
        text=[f"Date: {d.strftime('%Y-%m-%d')}<br>Hidden Pressure: {h:.4f}"
              for d, h in zip(df_clean['date'], df_clean['hidden_pressure'])],
        hovertemplate=(
            '<b>Momentum:</b> %{x:.3f}<br>'
            '<b>Open:</b> %{y:.2f}<br>'
            '<b>Close:</b> %{z:.2f}<br>'
            '%{text}<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Momentum (Derivative)',
            yaxis_title='Open Price',
            zaxis_title='Close Price',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        title=title,
        width=900,
        height=700
    )

    return fig


def visualize_4d_size_encoding(df, title="4D Visualization - Momentum Model (Size Encoding)"):
    """Create 3D scatter plot with 4th dimension as size"""
    df_clean = df.dropna()

    # Normalize the hidden dimension to reasonable marker sizes
    hidden_norm = (df_clean['hidden_pressure'] - df_clean['hidden_pressure'].min())
    hidden_norm = hidden_norm / (df_clean['hidden_pressure'].max() - df_clean['hidden_pressure'].min())
    sizes = 2 + hidden_norm * 10

    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean['momentum'],
        y=df_clean['open'],
        z=df_clean['close'],
        mode='markers',
        marker=dict(
            size=sizes,
            color='steelblue',
            opacity=0.6,
            line=dict(width=0)
        ),
        text=[f"Date: {d.strftime('%Y-%m-%d')}<br>Hidden Pressure: {h:.4f}<br>Size: {s:.2f}"
              for d, h, s in zip(df_clean['date'], df_clean['hidden_pressure'], sizes)],
        hovertemplate=(
            '<b>Momentum:</b> %{x:.3f}<br>'
            '<b>Open:</b> %{y:.2f}<br>'
            '<b>Close:</b> %{z:.2f}<br>'
            '%{text}<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Momentum (Derivative)',
            yaxis_title='Open Price',
            zaxis_title='Close Price',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        title=title,
        width=900,
        height=700
    )

    return fig


def visualize_multiple_projections(df, title="4D Visualization - Momentum Model (Multiple Projections)"):
    """Create multiple 2D/3D views to show different aspects"""
    df_clean = df.dropna()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Momentum vs Open (color=hidden)',
            'Momentum vs Close (color=hidden)',
            'Open vs Close (color=hidden)',
            '3D View (color=hidden)'
        ),
        specs=[
            [{'type': 'scatter'}, {'type': 'scatter'}],
            [{'type': 'scatter'}, {'type': 'scatter3d'}]
        ],
        horizontal_spacing=0.12,
        vertical_spacing=0.12
    )

    # 2D projection 1: Momentum vs Open
    fig.add_trace(
        go.Scatter(
            x=df_clean['momentum'],
            y=df_clean['open'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                size=5,
                showscale=False
            ),
            name='Mom-Open'
        ),
        row=1, col=1
    )

    # 2D projection 2: Momentum vs Close
    fig.add_trace(
        go.Scatter(
            x=df_clean['momentum'],
            y=df_clean['close'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                size=5,
                showscale=False
            ),
            name='Mom-Close'
        ),
        row=1, col=2
    )

    # 2D projection 3: Open vs Close
    fig.add_trace(
        go.Scatter(
            x=df_clean['open'],
            y=df_clean['close'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                size=5,
                showscale=False
            ),
            name='Open-Close'
        ),
        row=2, col=1
    )

    # 3D view
    fig.add_trace(
        go.Scatter3d(
            x=df_clean['momentum'],
            y=df_clean['open'],
            z=df_clean['close'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                size=3,
                showscale=True,
                colorbar=dict(
                    title="Hidden<br>Pressure",
                    x=1.15,
                    len=0.4,
                    y=0.25
                )
            ),
            name='3D View'
        ),
        row=2, col=2
    )

    # Update axes labels
    fig.update_xaxes(title_text="Momentum", row=1, col=1)
    fig.update_yaxes(title_text="Open", row=1, col=1)

    fig.update_xaxes(title_text="Momentum", row=1, col=2)
    fig.update_yaxes(title_text="Close", row=1, col=2)

    fig.update_xaxes(title_text="Open", row=2, col=1)
    fig.update_yaxes(title_text="Close", row=2, col=1)

    fig.update_layout(
        title=title,
        showlegend=False,
        height=900,
        width=1200
    )

    return fig


def visualize_ml_discovered_dimension(df, title="ML-Discovered Hidden Dimension (Momentum Model)"):
    """Visualize the hidden dimension discovered by ML"""
    df_clean = df.dropna()

    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean['momentum'],
        y=df_clean['open'],
        z=df_clean['close'],
        mode='markers',
        marker=dict(
            size=4,
            color=df_clean['ml_hidden_dim'],
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Predicted<br>Future<br>Momentum", x=1.1),
            line=dict(width=0)
        ),
        text=[f"Date: {d.strftime('%Y-%m-%d')}<br>ML Prediction: {h:.4f}"
              for d, h in zip(df_clean['date'], df_clean['ml_hidden_dim'])],
        hovertemplate=(
            '<b>Momentum:</b> %{x:.3f}<br>'
            '<b>Open:</b> %{y:.2f}<br>'
            '<b>Close:</b> %{z:.2f}<br>'
            '%{text}<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Momentum (Derivative)',
            yaxis_title='Open Price',
            zaxis_title='Close Price',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        title=title,
        width=900,
        height=700
    )

    return fig


def visualize_momentum_dynamics(df, title="Momentum Dynamics Over Time"):
    """Show how momentum relates to price action over time"""
    df_clean = df.dropna()

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'Price and Momentum Over Time',
            'Momentum vs Intraday Change',
            '3D: Momentum-Open-Close'
        ),
        specs=[
            [{'secondary_y': True}],
            [{'type': 'scatter'}],
            [{'type': 'scatter3d'}]
        ],
        vertical_spacing=0.1
    )

    # Row 1: Time series
    fig.add_trace(
        go.Scatter(
            x=df_clean['date'],
            y=df_clean['close'],
            name='Close Price',
            line=dict(color='blue')
        ),
        row=1, col=1, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_clean['date'],
            y=df_clean['momentum'],
            name='Momentum',
            line=dict(color='red')
        ),
        row=1, col=1, secondary_y=True
    )

    # Row 2: Momentum vs Intraday change
    fig.add_trace(
        go.Scatter(
            x=df_clean['momentum'],
            y=df_clean['intraday_change'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                size=4
            ),
            name='Momentum vs Intraday'
        ),
        row=2, col=1
    )

    # Row 3: 3D view
    fig.add_trace(
        go.Scatter3d(
            x=df_clean['momentum'],
            y=df_clean['open'],
            z=df_clean['close'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                size=2,
                showscale=True
            ),
            name='3D View'
        ),
        row=3, col=1
    )

    # Update axes
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Close Price", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Momentum", row=1, col=1, secondary_y=True)

    fig.update_xaxes(title_text="Momentum", row=2, col=1)
    fig.update_yaxes(title_text="Intraday Change", row=2, col=1)

    fig.update_layout(
        title=title,
        height=1200,
        width=1000,
        showlegend=True
    )

    return fig


def main():
    """Run the complete momentum-based prototype demonstration"""
    print("\n" + "="*60)
    print("4D MOMENTUM-BASED FINANCIAL VISUALIZATION PROTOTYPE")
    print("="*60 + "\n")

    # Generate data
    print("Generating sample financial data with momentum as primary dimension...")
    fin_data = MomentumFinancialData4D(n_days=500)

    # Calculate derived features
    print("Calculating derived features and hidden dimensions...")
    df_features = fin_data.calculate_derived_features()

    print(f"\nGenerated {len(df_features)} trading days")
    print(f"Date range: {df_features['date'].min().strftime('%Y-%m-%d')} to {df_features['date'].max().strftime('%Y-%m-%d')}")
    print(f"\nBase dimensions:")
    print(f"  1. Momentum (derivative/rate of change)")
    print(f"  2. Open Price")
    print(f"  3. Close Price")
    print(f"\nDerived features calculated: {list(df_features.columns)}\n")

    # Perform PCA analysis
    X_pca, pca, scaler = fin_data.perform_pca_analysis(df_features)

    # Train ML model
    model, df_features = fin_data.train_ml_model(df_features)

    # Generate visualizations
    print("=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    print("\nCreating interactive visualizations...")
    print("(HTML files will be saved to current directory)\n")

    # 1. Color encoding
    print("1. Creating color-encoded 4D visualization (momentum-based)...")
    fig1 = visualize_4d_color_encoding(df_features)
    fig1.write_html("momentum_viz_1_color_encoding.html")
    print("   Saved: momentum_viz_1_color_encoding.html")

    # 2. Size encoding
    print("2. Creating size-encoded 4D visualization (momentum-based)...")
    fig2 = visualize_4d_size_encoding(df_features)
    fig2.write_html("momentum_viz_2_size_encoding.html")
    print("   Saved: momentum_viz_2_size_encoding.html")

    # 3. Multiple projections
    print("3. Creating multiple projection views (momentum-based)...")
    fig3 = visualize_multiple_projections(df_features)
    fig3.write_html("momentum_viz_3_multiple_projections.html")
    print("   Saved: momentum_viz_3_multiple_projections.html")

    # 4. ML-discovered dimension
    print("4. Creating ML-discovered dimension visualization (momentum-based)...")
    fig4 = visualize_ml_discovered_dimension(df_features)
    fig4.write_html("momentum_viz_4_ml_discovered.html")
    print("   Saved: momentum_viz_4_ml_discovered.html")

    # 5. Momentum dynamics
    print("5. Creating momentum dynamics visualization...")
    fig5 = visualize_momentum_dynamics(df_features)
    fig5.write_html("momentum_viz_5_dynamics.html")
    print("   Saved: momentum_viz_5_dynamics.html")

    print("\n" + "=" * 60)
    print("MOMENTUM-BASED PROTOTYPE COMPLETE!")
    print("=" * 60)
    print("\nKey Differences from Price-Based Model:")
    print("- Uses MOMENTUM (derivative) instead of previous price")
    print("- Shows velocity/direction of price movement")
    print("- Better captures market dynamics and turning points")
    print("- Hidden dimension represents 'momentum-informed pressure'")
    print("\nSummary:")
    print("- Generated sample financial data over", len(df_features), "trading days")
    print("- Calculated momentum as first derivative of price")
    print("- Used (momentum, open, close) as 3D base dimensions")
    print("- Performed PCA to understand variance")
    print("- Trained ML model to predict future momentum")
    print("- Created 5 different visualization techniques")
    print("\nOpen the HTML files in your browser to explore the visualizations!")
    print("They are interactive - you can rotate, zoom, and hover for details.\n")


if __name__ == "__main__":
    main()
