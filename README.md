# altair_pandas
Altair backend for pandas plotting

**Note: this is a work in progress**

## Installation
Altair pandas backend works with pandas version 0.25 or newer.
```
$ pip install git+https://github.com/altair-viz/altair_pandas
```

## Usage
In a Jupyter notebook with Altair properly configured:
```python
import pandas as pd
pd.set_option('plotting.backend', 'altair')
pd.Series(range(10)).plot()
```