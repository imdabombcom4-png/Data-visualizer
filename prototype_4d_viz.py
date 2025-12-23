"""
4D Financial Data Visualization Prototype

This prototype demonstrates different techniques for visualizing 4-dimensional
relationships in financial instrument data:
- Previous Price (dimension 1)
- Open Price (dimension 2)
- Close Price (dimension 3)
- Hidden Dimension (dimension 4) - to be discovered

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
import warnings
warnings.filterwarnings('ignore')


class FinancialData4D:
    """Generate and analyze 4D financial data"""

    def __init__(self, n_samples=500, seed=42):
        """
        Initialize with sample financial data

        Args:
            n_samples: Number of data points to generate
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.n_samples = n_samples
        self.df = self._generate_sample_data()

    def _generate_sample_data(self):
        """Generate realistic sample financial data with hidden patterns"""
        # Generate base price with trend and noise
        trend = np.linspace(100, 120, self.n_samples)
        noise = np.cumsum(np.random.randn(self.n_samples) * 0.5)
        previous_price = trend + noise

        # Open price: influenced by previous price with gap
        gap = np.random.randn(self.n_samples) * 0.3
        open_price = previous_price + gap

        # Close price: influenced by open with intraday movement
        intraday_movement = np.random.randn(self.n_samples) * 0.5
        # Add hidden pattern: mean reversion
        mean_reversion = -(open_price - previous_price) * 0.3
        close_price = open_price + intraday_movement + mean_reversion

        df = pd.DataFrame({
            'previous_price': previous_price,
            'open': open_price,
            'close': close_price
        })

        return df

    def calculate_derived_features(self):
        """Calculate various features that might reveal hidden dimensions"""
        df = self.df.copy()

        # Price changes
        df['price_change'] = df['close'] - df['previous_price']
        df['intraday_change'] = df['close'] - df['open']
        df['gap'] = df['open'] - df['previous_price']

        # Returns (percentage changes)
        df['total_return'] = (df['close'] - df['previous_price']) / df['previous_price']
        df['intraday_return'] = (df['close'] - df['open']) / df['open']

        # Momentum indicators
        df['momentum_5'] = df['close'] - df['close'].shift(5)
        df['momentum_10'] = df['close'] - df['close'].shift(10)

        # Volatility
        df['volatility_5'] = df['intraday_change'].rolling(window=5).std()
        df['volatility_10'] = df['intraday_change'].rolling(window=10).std()

        # Hidden dimension candidate: combined momentum and mean reversion
        df['hidden_momentum'] = (
            0.4 * df['price_change'] +  # overall trend
            0.3 * df['intraday_change'] +  # intraday movement
            0.3 * df['gap']  # gap effect
        )

        # Mean reversion indicator
        rolling_mean = df['close'].rolling(window=20).mean()
        df['mean_reversion'] = (df['close'] - rolling_mean) / rolling_mean

        return df

    def perform_pca_analysis(self):
        """Use PCA to find principal components and explained variance"""
        features = ['previous_price', 'open', 'close']
        X = self.df[features].values

        # Standardize the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Apply PCA
        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X_scaled)

        print("=" * 60)
        print("PCA ANALYSIS")
        print("=" * 60)
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
        # Create a target: future return (what we're trying to predict)
        df_features['future_return'] = df_features['close'].shift(-1) / df_features['close'] - 1

        # Prepare data
        features = ['previous_price', 'open', 'close']
        X = df_features[features].iloc[:-1]  # Remove last row (no future return)
        y = df_features['future_return'].iloc[:-1]

        # Remove any NaN values
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]

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
        print("MACHINE LEARNING ANALYSIS")
        print("=" * 60)
        print(f"\nPredicting: Future Returns")
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


def visualize_4d_color_encoding(df, title="4D Visualization - Color Encoding"):
    """Create 3D scatter plot with 4th dimension as color"""
    df_clean = df.dropna()

    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean['previous_price'],
        y=df_clean['open'],
        z=df_clean['close'],
        mode='markers',
        marker=dict(
            size=4,
            color=df_clean['hidden_momentum'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Hidden<br>Momentum", x=1.1),
            line=dict(width=0)
        ),
        text=[f"Hidden: {h:.4f}" for h in df_clean['hidden_momentum']],
        hovertemplate=(
            '<b>Previous:</b> %{x:.2f}<br>'
            '<b>Open:</b> %{y:.2f}<br>'
            '<b>Close:</b> %{z:.2f}<br>'
            '%{text}<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Previous Price',
            yaxis_title='Open',
            zaxis_title='Close',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        title=title,
        width=900,
        height=700
    )

    return fig


def visualize_4d_size_encoding(df, title="4D Visualization - Size Encoding"):
    """Create 3D scatter plot with 4th dimension as size"""
    df_clean = df.dropna()

    # Normalize the hidden dimension to reasonable marker sizes
    hidden_norm = (df_clean['hidden_momentum'] - df_clean['hidden_momentum'].min())
    hidden_norm = hidden_norm / (df_clean['hidden_momentum'].max() - df_clean['hidden_momentum'].min())
    sizes = 2 + hidden_norm * 10  # Sizes between 2 and 12

    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean['previous_price'],
        y=df_clean['open'],
        z=df_clean['close'],
        mode='markers',
        marker=dict(
            size=sizes,
            color='steelblue',
            opacity=0.6,
            line=dict(width=0)
        ),
        text=[f"Hidden: {h:.4f}<br>Size: {s:.2f}"
              for h, s in zip(df_clean['hidden_momentum'], sizes)],
        hovertemplate=(
            '<b>Previous:</b> %{x:.2f}<br>'
            '<b>Open:</b> %{y:.2f}<br>'
            '<b>Close:</b> %{z:.2f}<br>'
            '%{text}<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Previous Price',
            yaxis_title='Open',
            zaxis_title='Close',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        title=title,
        width=900,
        height=700
    )

    return fig


def visualize_multiple_projections(df, title="4D Visualization - Multiple Projections"):
    """Create multiple 2D/3D views to show different aspects"""
    df_clean = df.dropna()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Previous vs Open (color=hidden)',
            'Previous vs Close (color=hidden)',
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

    # 2D projection 1: Previous vs Open
    fig.add_trace(
        go.Scatter(
            x=df_clean['previous_price'],
            y=df_clean['open'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_momentum'],
                colorscale='RdYlGn',
                size=5,
                showscale=False
            ),
            name='Prev-Open'
        ),
        row=1, col=1
    )

    # 2D projection 2: Previous vs Close
    fig.add_trace(
        go.Scatter(
            x=df_clean['previous_price'],
            y=df_clean['close'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_momentum'],
                colorscale='RdYlGn',
                size=5,
                showscale=False
            ),
            name='Prev-Close'
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
                color=df_clean['hidden_momentum'],
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
            x=df_clean['previous_price'],
            y=df_clean['open'],
            z=df_clean['close'],
            mode='markers',
            marker=dict(
                color=df_clean['hidden_momentum'],
                colorscale='RdYlGn',
                size=3,
                showscale=True,
                colorbar=dict(
                    title="Hidden<br>Momentum",
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
    fig.update_xaxes(title_text="Previous Price", row=1, col=1)
    fig.update_yaxes(title_text="Open", row=1, col=1)

    fig.update_xaxes(title_text="Previous Price", row=1, col=2)
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


def visualize_ml_discovered_dimension(df, title="ML-Discovered Hidden Dimension"):
    """Visualize the hidden dimension discovered by ML"""
    df_clean = df.dropna()

    fig = go.Figure(data=[go.Scatter3d(
        x=df_clean['previous_price'],
        y=df_clean['open'],
        z=df_clean['close'],
        mode='markers',
        marker=dict(
            size=4,
            color=df_clean['ml_hidden_dim'],
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Predicted<br>Future<br>Return", x=1.1),
            line=dict(width=0)
        ),
        text=[f"ML Prediction: {h:.4f}" for h in df_clean['ml_hidden_dim']],
        hovertemplate=(
            '<b>Previous:</b> %{x:.2f}<br>'
            '<b>Open:</b> %{y:.2f}<br>'
            '<b>Close:</b> %{z:.2f}<br>'
            '%{text}<br>'
            '<extra></extra>'
        )
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title='Previous Price',
            yaxis_title='Open',
            zaxis_title='Close',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        title=title,
        width=900,
        height=700
    )

    return fig


def main():
    """Run the complete prototype demonstration"""
    print("\n" + "="*60)
    print("4D FINANCIAL DATA VISUALIZATION PROTOTYPE")
    print("="*60 + "\n")

    # Generate data
    print("Generating sample financial data...")
    fin_data = FinancialData4D(n_samples=500)

    # Calculate derived features
    print("Calculating derived features and hidden dimensions...")
    df_features = fin_data.calculate_derived_features()

    print(f"\nGenerated {len(df_features)} data points")
    print(f"Features calculated: {list(df_features.columns)}\n")

    # Perform PCA analysis
    X_pca, pca, scaler = fin_data.perform_pca_analysis()

    # Train ML model
    model, df_features = fin_data.train_ml_model(df_features)

    # Generate visualizations
    print("=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    print("\nCreating interactive visualizations...")
    print("(HTML files will be saved to current directory)\n")

    # 1. Color encoding
    print("1. Creating color-encoded 4D visualization...")
    fig1 = visualize_4d_color_encoding(df_features)
    fig1.write_html("viz_1_color_encoding.html")
    print("   Saved: viz_1_color_encoding.html")

    # 2. Size encoding
    print("2. Creating size-encoded 4D visualization...")
    fig2 = visualize_4d_size_encoding(df_features)
    fig2.write_html("viz_2_size_encoding.html")
    print("   Saved: viz_2_size_encoding.html")

    # 3. Multiple projections
    print("3. Creating multiple projection views...")
    fig3 = visualize_multiple_projections(df_features)
    fig3.write_html("viz_3_multiple_projections.html")
    print("   Saved: viz_3_multiple_projections.html")

    # 4. ML-discovered dimension
    print("4. Creating ML-discovered dimension visualization...")
    fig4 = visualize_ml_discovered_dimension(df_features)
    fig4.write_html("viz_4_ml_discovered.html")
    print("   Saved: viz_4_ml_discovered.html")

    print("\n" + "=" * 60)
    print("PROTOTYPE COMPLETE!")
    print("=" * 60)
    print("\nSummary:")
    print("- Generated sample financial data with 3 base dimensions")
    print("- Calculated multiple candidate 'hidden dimensions'")
    print("- Performed PCA to understand variance")
    print("- Trained ML model to discover predictive dimension")
    print("- Created 4 different visualization techniques")
    print("\nOpen the HTML files in your browser to explore the visualizations!")
    print("They are interactive - you can rotate, zoom, and hover for details.\n")


if __name__ == "__main__":
    main()
