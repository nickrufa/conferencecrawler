# Pandas Documentation

Pandas is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of Python. It provides labeled data structures similar to R data.frame objects, statistical functions, and much more.

## Installation

### Using pip (recommended)
```bash
pip install pandas
```

### Using conda
```bash
conda install -c conda-forge pandas
```

### Installing with optional dependencies
```bash
# All optional dependencies
pip install "pandas[all]"

# Specific functionality
pip install "pandas[performance]"     # Performance libraries
pip install "pandas[excel]"          # Excel file support
pip install "pandas[plot]"           # Plotting libraries
pip install "pandas[computation]"    # Scientific computing
pip install "pandas[aws]"            # AWS cloud storage
pip install "pandas[gcp]"            # Google Cloud Storage
```

### From source
```bash
# Clone the repository
git clone https://github.com/pandas-dev/pandas.git
cd pandas
pip install .
```

## Basic Usage

### Creating DataFrames

```python
import pandas as pd
import numpy as np

# From a dictionary
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': ['foo', 'bar', 'baz', 'qux']
})

# From a list of dictionaries
data = [
    {'name': 'Alice', 'age': 25, 'city': 'New York'},
    {'name': 'Bob', 'age': 30, 'city': 'Paris'},
    {'name': 'Charlie', 'age': 35, 'city': 'Tokyo'}
]
df = pd.DataFrame(data)

# From numpy array
df = pd.DataFrame(np.random.randn(5, 3), columns=['A', 'B', 'C'])
```

### Creating Series

```python
# From a list
s = pd.Series([1, 2, 3, 4, 5])

# With custom index
s = pd.Series([1, 2, 3, 4, 5], index=['a', 'b', 'c', 'd', 'e'])

# From a dictionary
s = pd.Series({'a': 1, 'b': 2, 'c': 3})
```

## Data Input/Output

### Reading Data

```python
# CSV files
df = pd.read_csv('file.csv')
df = pd.read_csv('file.csv', index_col=0, parse_dates=True)

# Excel files
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')

# JSON files
df = pd.read_json('file.json')

# SQL databases
import sqlite3
conn = sqlite3.connect('database.db')
df = pd.read_sql_query('SELECT * FROM table_name', conn)

# HTML tables
df = pd.read_html('https://example.com/table.html')[0]

# Parquet files
df = pd.read_parquet('file.parquet')
```

### Writing Data

```python
# CSV files
df.to_csv('output.csv', index=False)

# Excel files
df.to_excel('output.xlsx', sheet_name='Sheet1', index=False)

# JSON files
df.to_json('output.json', orient='records')

# SQL databases
df.to_sql('table_name', conn, if_exists='replace', index=False)

# Parquet files
df.to_parquet('output.parquet')
```

## Data Selection and Filtering

### Column Selection

```python
# Select single column
df['column_name']
df.column_name  # If column name is valid Python identifier

# Select multiple columns
df[['col1', 'col2', 'col3']]

# Select columns by data type
df.select_dtypes(include=['number'])
df.select_dtypes(include=['object'])
```

### Row Selection

```python
# Select by index
df.loc[0]           # First row by integer index
df.loc['row_label'] # Row by label
df.iloc[0]          # First row by position

# Select multiple rows
df.loc[0:2]         # Rows 0, 1, 2 by label
df.iloc[0:3]        # Rows 0, 1, 2 by position

# Select rows by condition
df[df['age'] > 25]
df[df['city'] == 'New York']
df[(df['age'] > 25) & (df['city'] == 'New York')]
```

### Advanced Selection

```python
# Select specific rows and columns
df.loc[0:2, 'name':'age']
df.iloc[0:3, 1:3]

# Boolean indexing
mask = df['age'] > 25
df.loc[mask, ['name', 'city']]

# Query method
df.query('age > 25 and city == "New York"')
```

## Data Manipulation

### Creating New Columns

```python
# Simple calculation
df['new_col'] = df['col1'] + df['col2']

# Conditional column
df['category'] = df['age'].apply(lambda x: 'adult' if x >= 18 else 'minor')

# Using where/conditions
df['status'] = np.where(df['age'] > 30, 'senior', 'junior')
```

### Modifying Data

```python
# Replace values
df['column'] = df['column'].replace('old_value', 'new_value')
df.replace({'column': {'old': 'new'}}, inplace=True)

# Update values conditionally
df.loc[df['age'] > 30, 'status'] = 'senior'

# Apply functions
df['column'] = df['column'].apply(lambda x: x.upper())
df = df.apply(lambda x: x.astype(str), axis=0)  # Apply to columns
df = df.apply(lambda x: x.sum(), axis=1)        # Apply to rows
```

## Data Cleaning

### Handling Missing Data

```python
# Check for missing values
df.isnull()
df.isnull().sum()
df.info()

# Drop missing values
df.dropna()                    # Drop rows with any NaN
df.dropna(subset=['column'])   # Drop rows where specific column is NaN
df.dropna(axis=1)             # Drop columns with any NaN

# Fill missing values
df.fillna(0)                  # Fill with constant
df.fillna(df.mean())          # Fill with mean
df.fillna(method='ffill')     # Forward fill
df.fillna(method='bfill')     # Backward fill

# Fill with different values per column
df.fillna({'col1': 0, 'col2': 'unknown'})
```

### Data Type Conversion

```python
# Check data types
df.dtypes

# Convert data types
df['column'] = df['column'].astype('int64')
df['column'] = df['column'].astype('category')
df['date_column'] = pd.to_datetime(df['date_column'])
df['numeric_column'] = pd.to_numeric(df['numeric_column'], errors='coerce')
```

### Removing Duplicates

```python
# Check for duplicates
df.duplicated()
df.duplicated().sum()

# Remove duplicates
df.drop_duplicates()
df.drop_duplicates(subset=['column1', 'column2'])
df.drop_duplicates(keep='last')  # Keep last occurrence
```

## Data Analysis and Statistics

### Basic Statistics

```python
# Summary statistics
df.describe()
df['column'].describe()

# Individual statistics
df.mean()
df.median()
df.std()
df.var()
df.min()
df.max()
df.count()
df.sum()

# Correlation
df.corr()
df['col1'].corr(df['col2'])
```

### Value Counts and Frequencies

```python
# Count unique values
df['column'].value_counts()
df['column'].value_counts(normalize=True)  # Percentages

# Count unique values across multiple columns
df.value_counts(['col1', 'col2'])

# Unique values
df['column'].unique()
df['column'].nunique()
```

## GroupBy Operations

### Basic GroupBy

```python
# Group by single column
grouped = df.groupby('category')
grouped.mean()
grouped.sum()
grouped.count()

# Group by multiple columns
grouped = df.groupby(['category', 'subcategory'])
grouped.mean()

# Access specific groups
grouped.get_group('category_value')
```

### Advanced GroupBy

```python
# Apply different aggregations to different columns
df.groupby('category').agg({
    'sales': 'sum',
    'price': 'mean',
    'quantity': ['min', 'max']
})

# Apply custom functions
df.groupby('category').apply(lambda x: x.max() - x.min())

# Transform (keep original shape)
df['sales_normalized'] = df.groupby('category')['sales'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Filter groups
df.groupby('category').filter(lambda x: x['sales'].sum() > 1000)
```

## Data Reshaping

### Pivot Tables

```python
# Basic pivot table
pivot = df.pivot_table(
    values='sales', 
    index='category', 
    columns='month', 
    aggfunc='sum'
)

# Pivot with multiple aggregations
pivot = df.pivot_table(
    values='sales',
    index='category',
    columns='month',
    aggfunc=['sum', 'mean', 'count']
)

# Simple pivot (no aggregation)
df.pivot(index='date', columns='category', values='sales')
```

### Melt (Wide to Long)

```python
# Basic melt
df_long = pd.melt(df, id_vars=['id'], value_vars=['col1', 'col2'])

# Melt with custom names
df_long = pd.melt(
    df, 
    id_vars=['id'], 
    value_vars=['col1', 'col2'],
    var_name='variable',
    value_name='value'
)
```

### Stack and Unstack

```python
# Stack (columns to index)
df_stacked = df.stack()

# Unstack (index to columns)
df_unstacked = df_stacked.unstack()

# Unstack specific level
df_unstacked = df.unstack(level=0)
```

## Merging and Joining Data

### Merge DataFrames

```python
# Inner join (default)
merged = pd.merge(df1, df2, on='key_column')

# Different join types
merged = pd.merge(df1, df2, on='key_column', how='left')    # Left join
merged = pd.merge(df1, df2, on='key_column', how='right')   # Right join
merged = pd.merge(df1, df2, on='key_column', how='outer')   # Full outer join

# Merge on multiple columns
merged = pd.merge(df1, df2, on=['key1', 'key2'])

# Merge with different column names
merged = pd.merge(df1, df2, left_on='left_key', right_on='right_key')

# Merge with suffixes for overlapping columns
merged = pd.merge(df1, df2, on='key', suffixes=('_left', '_right'))
```

### Concatenate DataFrames

```python
# Concatenate vertically (row-wise)
result = pd.concat([df1, df2])
result = pd.concat([df1, df2], ignore_index=True)

# Concatenate horizontally (column-wise)
result = pd.concat([df1, df2], axis=1)

# Concatenate with keys
result = pd.concat([df1, df2], keys=['df1', 'df2'])
```

### Join (Index-based)

```python
# Join on index
result = df1.join(df2)
result = df1.join(df2, how='left')

# Join with suffix
result = df1.join(df2, rsuffix='_right')
```

## Time Series Data

### Working with Dates

```python
# Create date ranges
dates = pd.date_range('2023-01-01', periods=365, freq='D')
dates = pd.date_range('2023-01-01', '2023-12-31', freq='M')

# Convert to datetime
df['date'] = pd.to_datetime(df['date_string'])
df['date'] = pd.to_datetime(df['date_string'], format='%Y-%m-%d')

# Set datetime index
df.set_index('date', inplace=True)
```

### Time-based Indexing

```python
# Select by date
df['2023']           # All data from 2023
df['2023-01']        # All data from January 2023
df['2023-01-01']     # Data from specific date

# Date range selection
df['2023-01-01':'2023-01-31']

# Recent data
df.last('30D')       # Last 30 days
df.first('3M')       # First 3 months
```

### Resampling

```python
# Resample to different frequencies
df.resample('M').mean()      # Monthly averages
df.resample('Q').sum()       # Quarterly sums
df.resample('W').std()       # Weekly standard deviation

# Upsampling (higher frequency)
df.resample('D').interpolate()

# Downsampling with custom aggregation
df.resample('M').agg({
    'sales': 'sum',
    'price': 'mean'
})
```

### Time Series Operations

```python
# Shift data
df['previous_month'] = df['sales'].shift(1)
df['next_month'] = df['sales'].shift(-1)

# Rolling windows
df['rolling_mean'] = df['sales'].rolling(window=7).mean()
df['rolling_std'] = df['sales'].rolling(window=30).std()

# Expanding windows
df['expanding_mean'] = df['sales'].expanding().mean()

# Time differences
df['days_since'] = (df.index - df.index[0]).days
```

## Data Visualization

### Basic Plotting

```python
import matplotlib.pyplot as plt

# Line plot
df.plot()
df['column'].plot()

# Different plot types
df.plot(kind='bar')         # Bar chart
df.plot(kind='hist')        # Histogram
df.plot(kind='box')         # Box plot
df.plot(kind='scatter', x='col1', y='col2')  # Scatter plot

# Multiple subplots
df.plot(subplots=True, figsize=(10, 8))

# Customization
df.plot(title='My Plot', xlabel='X Label', ylabel='Y Label')
```

## Advanced Operations

### Apply Functions

```python
# Apply to columns
df.apply(lambda x: x.max() - x.min())

# Apply to rows
df.apply(lambda x: x.sum(), axis=1)

# Apply with additional arguments
df.apply(lambda x: x.clip(lower=0, upper=100))

# Map values (Series only)
df['column'].map({'old': 'new', 'value1': 'value2'})
```

### String Operations

```python
# String methods (for string columns)
df['text'].str.upper()
df['text'].str.lower()
df['text'].str.strip()
df['text'].str.replace('old', 'new')
df['text'].str.contains('pattern')
df['text'].str.extract(r'(\d+)')        # Extract numbers
df['text'].str.split(',")               # Split strings
df['text'].str.len()                    # String length
```

### Categorical Data

```python
# Convert to category
df['category'] = df['category'].astype('category')

# Create ordered categories
df['grade'] = pd.Categorical(
    df['grade'], 
    categories=['F', 'D', 'C', 'B', 'A'], 
    ordered=True
)

# Category operations
df['category'].cat.categories           # View categories
df['category'].cat.add_categories(['new_cat'])
df['category'].cat.remove_categories(['old_cat'])
```

## Performance Tips

### Efficient Operations

```python
# Use vectorized operations instead of loops
# Good
df['new_col'] = df['col1'] * df['col2']

# Avoid
# df['new_col'] = df.apply(lambda x: x['col1'] * x['col2'], axis=1)

# Use query for filtering
# Good
df.query('col1 > 5 and col2 < 10')

# Less efficient
# df[(df['col1'] > 5) & (df['col2'] < 10)]

# Use categorical data for string columns with few unique values
df['category'] = df['category'].astype('category')

# Use appropriate data types
df['int_col'] = df['int_col'].astype('int32')  # If values fit
```

### Memory Usage

```python
# Check memory usage
df.info(memory_usage='deep')
df.memory_usage(deep=True)

# Optimize data types
df = df.astype({
    'int_col': 'int32',
    'float_col': 'float32',
    'string_col': 'category'
})

# Use chunking for large files
chunk_list = []
for chunk in pd.read_csv('large_file.csv', chunksize=1000):
    chunk_processed = process_chunk(chunk)
    chunk_list.append(chunk_processed)
df = pd.concat(chunk_list, ignore_index=True)
```

## Configuration

### Display Options

```python
# Set pandas options
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 3)

# Get current options
pd.get_option('display.max_rows')

# Reset options
pd.reset_option('display.max_rows')

# Context manager for temporary settings
with pd.option_context('display.max_rows', 10):
    print(df)
```

### Common Options

```python
# Display options
pd.set_option('display.max_rows', None)          # Show all rows
pd.set_option('display.max_columns', None)       # Show all columns
pd.set_option('display.width', None)             # Use terminal width
pd.set_option('display.precision', 3)            # Decimal precision

# Computation options
pd.set_option('mode.chained_assignment', None)   # Suppress warnings
pd.set_option('compute.use_bottleneck', True)    # Use bottleneck for speed
pd.set_option('compute.use_numexpr', True)       # Use numexpr for speed
```

## Common Patterns

### Data Pipeline

```python
# Method chaining
result = (df
    .dropna()
    .query('age > 18')
    .groupby('category')
    .agg({'sales': 'sum', 'profit': 'mean'})
    .sort_values('sales', ascending=False)
    .reset_index()
)
```

### Working with Duplicates

```python
# Find and handle duplicates
duplicates = df[df.duplicated(keep=False)]
df_clean = df.drop_duplicates(subset=['key_column'], keep='first')
```

### Data Validation

```python
# Check data quality
print(f"Shape: {df.shape}")
print(f"Null values: {df.isnull().sum().sum()}")
print(f"Duplicates: {df.duplicated().sum()}")
print(f"Data types: {df.dtypes.value_counts()}")
```

This documentation covers the most commonly used pandas functionality for data manipulation, analysis, and processing. For more advanced features and detailed API documentation, refer to the official pandas documentation.