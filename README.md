# altair_pandas

[![build status](http://img.shields.io/travis/altair-viz/altair_pandas/master.svg?style=flat)](https://travis-ci.org/altair-viz/altair_pandas)

Altair backend for pandas plotting functions.

**Note: this package is a work in progress**

## Installation
Altair pandas backend works with pandas version 0.25 or newer.
```
$ pip install git+https://github.com/altair-viz/altair_pandas
```

## Usage
In a Jupyter notebook with [Altair](http://altair-viz.github.io) properly configured:
```python
import pandas as pd
import numpy as np
pd.set_option('plotting.backend', 'altair_pandas')

data = pd.Series(np.random.randn(100).cumsum())
data.plot()
```
![Altair-Pandas Visualization](https://raw.githubusercontent.com/altair-viz/altair_pandas/master/images/example.png)