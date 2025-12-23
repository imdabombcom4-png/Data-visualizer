"""
Visualize Financial Data from SQL Database

This script loads data from the SQLite database and creates
4D visualizations using the momentum-based model.

Usage:
    python visualize_from_database.py [symbol]

    symbol: Optional. Instrument symbol to visualize (default: AAPL)

Examples:
    python visualize_from_database.py
    python visualize_from_database.py BTC
    python visualize_from_database.py GOOGL
"""

import sys
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class DatabaseVisualizer:
    """Load and visualize data from SQL database"""

    def __init__(self, db_path='market_data.db'):
        """Initialize with database path"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

    def get_available_symbols(self):
        """Get list of available symbols"""
        df = pd.read_sql_query(
            "SELECT symbol, name, asset_type FROM Instruments ORDER BY symbol",
            self.conn
        )
        return df

    def load_data(self, symbol='AAPL'):
        """Load all data for a specific symbol"""
        query = """
            SELECT
                trade_date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                momentum,
                momentum_percent,
                intraday_change,
                intraday_return,
                hidden_pressure,
                momentum_acceleration,
                momentum_volatility
            FROM vw_FullMarketData
            WHERE symbol = ?
            ORDER BY trade_date
        """

        df = pd.read_sql_query(query, self.conn, params=(symbol,))
        df['trade_date'] = pd.to_datetime(df['trade_date'])

        print(f"\n✓ Loaded {len(df)} records for {symbol}")
        print(f"  Date range: {df['trade_date'].min().strftime('%Y-%m-%d')} to {df['trade_date'].max().strftime('%Y-%m-%d')}")
        print(f"  Price range: ${df['close_price'].min():.2f} to ${df['close_price'].max():.2f}")

        return df

    def visualize_4d_color_encoding(self, df, symbol):
        """Create 3D scatter plot with 4th dimension as color"""
        df_clean = df.dropna()

        fig = go.Figure(data=[go.Scatter3d(
            x=df_clean['momentum'],
            y=df_clean['open_price'],
            z=df_clean['close_price'],
            mode='markers',
            marker=dict(
                size=4,
                color=df_clean['hidden_pressure'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Hidden<br>Pressure", x=1.1),
                line=dict(width=0)
            ),
            text=[f"Date: {d.strftime('%Y-%m-%d')}<br>Hidden Pressure: {h:.4f}<br>Close: ${c:.2f}"
                  for d, h, c in zip(df_clean['trade_date'], df_clean['hidden_pressure'], df_clean['close_price'])],
            hovertemplate=(
                '<b>Momentum:</b> %{x:.3f}<br>'
                '<b>Open:</b> $%{y:.2f}<br>'
                '<b>Close:</b> $%{z:.2f}<br>'
                '%{text}<br>'
                '<extra></extra>'
            )
        )])

        fig.update_layout(
            scene=dict(
                xaxis_title='Momentum (Derivative)',
                yaxis_title='Open Price ($)',
                zaxis_title='Close Price ($)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            title=f'4D Visualization: {symbol} (Color = Hidden Pressure)',
            width=1000,
            height=800
        )

        return fig

    def visualize_temporal_analysis(self, df, symbol):
        """Show how variables evolve over time"""
        df_clean = df.dropna()

        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=(
                f'{symbol}: Price and Momentum Over Time',
                'Momentum Dynamics',
                'Hidden Pressure Evolution',
                '3D Momentum Space'
            ),
            specs=[
                [{'secondary_y': True}],
                [{'type': 'scatter'}],
                [{'type': 'scatter'}],
                [{'type': 'scatter3d'}]
            ],
            vertical_spacing=0.08
        )

        # Row 1: Price and Momentum time series
        fig.add_trace(
            go.Scatter(
                x=df_clean['trade_date'],
                y=df_clean['close_price'],
                name='Close Price',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1, secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=df_clean['trade_date'],
                y=df_clean['momentum'],
                name='Momentum',
                line=dict(color='red', width=1.5)
            ),
            row=1, col=1, secondary_y=True
        )

        # Row 2: Momentum vs Intraday Change (shows relationship)
        fig.add_trace(
            go.Scatter(
                x=df_clean['momentum'],
                y=df_clean['intraday_change'],
                mode='markers',
                marker=dict(
                    color=df_clean['hidden_pressure'],
                    colorscale='RdYlGn',
                    size=4,
                    showscale=False
                ),
                name='Momentum vs Intraday'
            ),
            row=2, col=1
        )

        # Row 3: Hidden Pressure over time
        colors = ['red' if p < 0 else 'green' for p in df_clean['hidden_pressure']]
        fig.add_trace(
            go.Bar(
                x=df_clean['trade_date'],
                y=df_clean['hidden_pressure'],
                name='Hidden Pressure',
                marker=dict(color=colors),
                showlegend=False
            ),
            row=3, col=1
        )

        # Row 4: 3D view
        fig.add_trace(
            go.Scatter3d(
                x=df_clean['momentum'],
                y=df_clean['open_price'],
                z=df_clean['close_price'],
                mode='markers',
                marker=dict(
                    color=df_clean['hidden_pressure'],
                    colorscale='RdYlGn',
                    size=2,
                    showscale=True,
                    colorbar=dict(
                        title="Hidden<br>Pressure",
                        x=1.15,
                        len=0.2,
                        y=0.1
                    )
                ),
                name='3D View'
            ),
            row=4, col=1
        )

        # Update axes
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_yaxes(title_text="Close Price ($)", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Momentum", row=1, col=1, secondary_y=True)

        fig.update_xaxes(title_text="Momentum", row=2, col=1)
        fig.update_yaxes(title_text="Intraday Change", row=2, col=1)

        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Hidden Pressure", row=3, col=1)

        fig.update_layout(
            title=f'Temporal Analysis: {symbol}',
            height=1400,
            width=1200,
            showlegend=True
        )

        return fig

    def visualize_multiple_projections(self, df, symbol):
        """Create multiple views of the 4D space"""
        df_clean = df.dropna()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Momentum vs Open',
                'Momentum vs Close',
                'Open vs Close',
                '3D: Momentum-Open-Close'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'scatter3d'}]
            ],
            horizontal_spacing=0.12,
            vertical_spacing=0.15
        )

        # 2D projections
        for row, col, x_col, y_col in [
            (1, 1, 'momentum', 'open_price'),
            (1, 2, 'momentum', 'close_price'),
            (2, 1, 'open_price', 'close_price')
        ]:
            fig.add_trace(
                go.Scatter(
                    x=df_clean[x_col],
                    y=df_clean[y_col],
                    mode='markers',
                    marker=dict(
                        color=df_clean['hidden_pressure'],
                        colorscale='RdYlGn',
                        size=5,
                        showscale=False
                    ),
                    name=f'{x_col}-{y_col}'
                ),
                row=row, col=col
            )

        # 3D view
        fig.add_trace(
            go.Scatter3d(
                x=df_clean['momentum'],
                y=df_clean['open_price'],
                z=df_clean['close_price'],
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

        # Update axes
        fig.update_xaxes(title_text="Momentum", row=1, col=1)
        fig.update_yaxes(title_text="Open ($)", row=1, col=1)

        fig.update_xaxes(title_text="Momentum", row=1, col=2)
        fig.update_yaxes(title_text="Close ($)", row=1, col=2)

        fig.update_xaxes(title_text="Open ($)", row=2, col=1)
        fig.update_yaxes(title_text="Close ($)", row=2, col=1)

        fig.update_layout(
            title=f'Multiple Projections: {symbol}',
            showlegend=False,
            height=900,
            width=1200
        )

        return fig

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main visualization function"""
    print("\n" + "="*60)
    print("DATABASE 4D VISUALIZATION TOOL")
    print("="*60)

    # Get symbol from command line or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'

    # Initialize visualizer
    viz = DatabaseVisualizer('market_data.db')

    # Show available symbols
    print("\nAvailable symbols:")
    symbols_df = viz.get_available_symbols()
    for _, row in symbols_df.iterrows():
        print(f"  {row['symbol']:<10} {row['name']:<30} ({row['asset_type']})")

    # Load data
    print(f"\nLoading data for: {symbol}")
    df = viz.load_data(symbol)

    # Generate visualizations
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)

    print("\n1. Creating 4D color-encoded visualization...")
    fig1 = viz.visualize_4d_color_encoding(df, symbol)
    filename1 = f"db_viz_{symbol}_4d_color.html"
    fig1.write_html(filename1)
    print(f"   ✓ Saved: {filename1}")

    print("2. Creating temporal analysis visualization...")
    fig2 = viz.visualize_temporal_analysis(df, symbol)
    filename2 = f"db_viz_{symbol}_temporal.html"
    fig2.write_html(filename2)
    print(f"   ✓ Saved: {filename2}")

    print("3. Creating multiple projections visualization...")
    fig3 = viz.visualize_multiple_projections(df, symbol)
    filename3 = f"db_viz_{symbol}_projections.html"
    fig3.write_html(filename3)
    print(f"   ✓ Saved: {filename3}")

    # Close database
    viz.close()

    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE!")
    print("="*60)
    print(f"\nGenerated visualizations for {symbol}:")
    print(f"  1. {filename1} - Interactive 4D view")
    print(f"  2. {filename2} - Temporal analysis (shows variable flow)")
    print(f"  3. {filename3} - Multiple projection views")
    print("\nOpen any HTML file in your browser to explore!")
    print("\nTry other symbols:")
    print("  python visualize_from_database.py BTC")
    print("  python visualize_from_database.py GOOGL\n")


if __name__ == "__main__":
    main()
