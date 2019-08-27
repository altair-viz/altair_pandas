# altair_pandas

[![build status](http://img.shields.io/travis/altair-viz/altair_pandas/master.svg?style=flat)](https://travis-ci.org/altair-viz/altair_pandas)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Altair backend for pandas plotting functions.

**Note: this package is a work in progress**

## Installation
Altair pandas backend works with pandas version 0.25.1 or newer.
```
$ pip install git+https://github.com/altair-viz/altair_pandas
$ pip install -U pandas
```

## Usage
In a Jupyter notebook with [Altair](http://altair-viz.github.io) properly configured:
```python
import pandas as pd
import numpy as np
pd.set_option('plotting.backend', 'altair')  # Installing altair_pandas registers this.

data = pd.Series(np.random.randn(100).cumsum())
data.plot()
```
![Altair-Pandas Visualization](https://raw.githubusercontent.com/altair-viz/altair_pandas/master/images/example.png)

The goal of this package is to implement all of [Pandas' Plotting API](https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html)