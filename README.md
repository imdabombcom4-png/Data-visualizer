# 4D Financial Data Visualization Prototype

A prototype for visualizing 4-dimensional relationships in financial instrument data using Python.

## Concept

This prototype explores how to visualize relationships between:
- **Previous Price** (dimension 1)
- **Open Price** (dimension 2)
- **Close Price** (dimension 3)
- **Hidden Dimension** (dimension 4) - discovered through analysis

Since humans can only directly visualize 3D space, we use various techniques to represent the 4th dimension.

## Features

### 1. **Data Generation**
- Creates realistic sample financial data with hidden patterns
- Includes trends, noise, gaps, and mean reversion

### 2. **Hidden Dimension Discovery**
- **Engineered Features**: Calculates momentum, volatility, and mean reversion indicators
- **PCA Analysis**: Finds principal components and variance explanation
- **Machine Learning**: Random Forest model learns predictive patterns

### 3. **Visualization Techniques**

#### Color Encoding
- 3D scatter plot where the 4th dimension is represented as color
- Uses a color scale to show the "hidden momentum" value
- Interactive: rotate, zoom, and hover for details

#### Size Encoding
- 3D scatter plot where the 4th dimension controls marker size
- Larger points = higher hidden dimension values
- Useful for seeing magnitude patterns

#### Multiple Projections
- Four different views showing 2D and 3D projections
- Each projection colored by the hidden dimension
- Helps understand relationships from different angles

#### ML-Discovered Dimension
- Shows the hidden dimension learned by the ML model
- Represents predicted future returns
- Different color scale to distinguish from engineered features

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python prototype_4d_viz.py
```

The script will:
1. Generate sample financial data (500 data points)
2. Calculate derived features and hidden dimensions
3. Perform PCA analysis (printed to console)
4. Train a Random Forest model (results printed to console)
5. Generate 4 interactive HTML visualizations

### Output Files

- `viz_1_color_encoding.html` - Color-encoded 4D visualization
- `viz_2_size_encoding.html` - Size-encoded 4D visualization
- `viz_3_multiple_projections.html` - Multiple projection views
- `viz_4_ml_discovered.html` - ML-discovered dimension

Open these HTML files in your browser to explore the interactive 3D visualizations!

## Understanding the Output

### Console Output

The script prints analysis results including:

**PCA Analysis:**
- Variance explained by each principal component
- How each original feature contributes to components
- Helps understand which dimensions carry the most information

**ML Analysis:**
- Model performance (R² scores)
- Feature importances showing which dimensions matter most for prediction
- The model predicts future returns based on the 3 input dimensions

### Interactive Visualizations

All visualizations are interactive:
- **Click and drag** to rotate the 3D view
- **Scroll** to zoom in/out
- **Hover** over points to see exact values
- Use the toolbar to pan, reset, or save images

## Key Insights

1. **Color patterns** reveal how the hidden dimension relates to the 3D space
2. **Clusters** suggest different market regimes or patterns
3. **PCA** shows that even with 3 dimensions, most variance is in 1-2 principal directions
4. **ML feature importance** reveals which price (previous, open, close) matters most for prediction

## Next Steps

This prototype demonstrates the concepts. The next phase would be:
1. Build a full visualization tool with GUI
2. Support loading real financial data (CSV, API)
3. Add more visualization options (animation through time, etc.)
4. Allow customization of the hidden dimension calculation
5. Add real-time data streaming capabilities

## Technical Details

- **Language**: Python 3.x
- **Visualization**: Plotly (interactive 3D)
- **ML Framework**: scikit-learn
- **Data Processing**: pandas, numpy
- **Model**: Random Forest Regressor (ensemble method)

## Understanding 4D Visualization

Since we can't directly see 4D, we use these strategies:
- **Encoding**: Map the 4th dimension to visual properties (color, size)
- **Projection**: Show multiple 3D views of the 4D space
- **Reduction**: Use PCA to find the most important dimensions
- **Learning**: Use ML to discover what the 4th dimension should represent

Each technique gives a different perspective on the same 4D data!
