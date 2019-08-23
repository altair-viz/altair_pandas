import altair as alt
import pandas as pd


class _PandasPlotter:
    """Base class for pandas plotting."""
    @classmethod
    def create(cls, data):
        if isinstance(data, pd.Series):
            return _SeriesPlotter(data)
        elif isinstance(data, pd.DataFrame):
            return _DataFramePlotter(data)
        else:
            raise NotImplementedError(f"data of type {type(data)}")


class _SeriesPlotter(_PandasPlotter):
    """Functionality for plotting of pandas Series."""
    data_class = pd.Series

    def __init__(self, data):
        self._raw_data = data
        self._data = self._preprocess(data)

    @staticmethod
    def _preprocess(data):
        if not isinstance(data, pd.Series):
            raise ValueError(f"data: expected pd.Series; got {type(data)}")
        if isinstance(data.index, pd.MultiIndex):
            raise NotImplementedError("Multi-indexed data.")
        data = data.copy()
        if not data.name:
            data.name = 'values'
        if not data.index.name:
            data.index.name = 'index'
        return data.reset_index()

    def line(self, **kwargs):
        return alt.Chart(self._data).mark_line().encode(
            x=self._data.columns[0],
            y=self._data.columns[1],
            tooltip=[self._data.columns[0], self._data.columns[1]]
        ).interactive()


class _DataFramePlotter(_PandasPlotter):
    """Functionality for plotting of pandas DataFrames."""
    data_class = pd.DataFrame

    def __init__(self, data):
        self._raw_data = data
        self._data = self._preprocess(data)

    @staticmethod
    def _preprocess(data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"data: expected pd.DataFrame; got {type(data)}")
        if isinstance(data.index, pd.MultiIndex):
            raise NotImplementedError("Multi-indexed data.")
        data = data.copy()
        if not data.index.name:
            data.index.name = 'index'
        return data.reset_index()

    def line(self, x=None, y=None, **kwargs):
        if x is None:
            x = self._data.columns[0]
        else:
            assert x in self._data.columns
        if y is None:
            y_values = list(self._data.columns[1:])
        else:
            assert y in self._data.columns
            y_values = [y]

        return alt.Chart(self._data).transform_fold(
            y_values, as_=['column', 'value']
        ).mark_line().encode(
            x=x,
            y=alt.Y('value:Q', title=None),
            color=alt.Color('column:N', title=None),
            tooltip=[x] + y_values,
        ).interactive()


def plot(data, kind='line', **kwargs):
    """Pandas plotting interface for Altair."""
    plotter = _PandasPlotter.create(data)

    if hasattr(plotter, kind):
        plotfunc = getattr(plotter, kind)
    else:
        raise NotImplementedError(
            f"kind='{kind}' for data of type {type(data)}")

    return plotfunc(**kwargs)
