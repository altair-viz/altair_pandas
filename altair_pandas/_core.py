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
            data.name = 'value'
        if not data.index.name:
            data.index.name = 'index'
        return data.reset_index()

    def _xy(self, mark='line', **kwargs):
        return alt.Chart(self._data, mark=mark).encode(
            x=alt.X(self._data.columns[0], title=None),
            y=alt.Y(self._data.columns[1], title=None),
            tooltip=[self._data.columns[0], self._data.columns[1]]
        ).interactive()

    def line(self, **kwargs):
        return self._xy(mark='line', **kwargs)

    def bar(self, **kwargs):
        return self._xy(mark='bar', **kwargs)

    def area(self, **kwargs):
        return self._xy(mark='area', **kwargs)

    def scatter(self, **kwargs):
        raise ValueError("kind='scatter' can only be used for DataFrames.")

    def hist(self, **kwargs):
        data = self._data.iloc[:, 1:]
        column = data.columns[0]
        return alt.Chart(data).mark_bar().encode(
            x=alt.X(column, title=None, bin=True),
            y=alt.Y('count()', title='Frequency'),
        )

    def box(self, **kwargs):
        data = self._data.iloc[:, 1:]
        return alt.Chart(data).transform_fold(
            list(data.columns), as_=['column', 'value']
        ).mark_boxplot().encode(
            x=alt.X('column:N', title=None),
            y='value:Q'
        )


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

    def _xy(self, mark, x=None, y=None, **kwargs):
        if x is None:
            x = self._data.columns[0]
        else:
            assert x in self._data.columns
        if y is None:
            y_values = list(self._data.columns[1:])
        else:
            assert y in self._data.columns
            y_values = [y]

        return alt.Chart(
            self._data,
            mark=mark
        ).transform_fold(
            y_values, as_=['column', 'value']
        ).encode(
            x=x,
            y=alt.Y('value:Q', title=None),
            color=alt.Color('column:N', title=None),
            tooltip=[x] + y_values,
        ).interactive()

    def line(self, x=None, y=None, **kwargs):
        return self._xy('line', x, y, **kwargs)

    def area(self, x=None, y=None, **kwargs):
        return self._xy('area', x, y, **kwargs)

    # TODO: bars should be grouped, not stacked.
    def bar(self, x=None, y=None, **kwargs):
        return self._xy('bar', x, y, **kwargs)

    def scatter(self, x, y, c=None, s=None, **kwargs):
        if x is None or y is None:
            raise ValueError("kind='scatter' requires 'x' and 'y' arguments.")
        encodings = {'x': x, 'y': y}
        if c is not None:
            encodings['color'] = c
        if s is not None:
            encodings['size'] = s
        columns = list(set(encodings.values()))
        encodings['tooltip'] = columns
        return alt.Chart(self._data[columns]).mark_point().encode(
            **encodings
        ).interactive()

    def hist(self, **kwargs):
        data = self._data.iloc[:, 1:]
        return alt.Chart(data).transform_fold(
            list(data.columns), as_=['column', 'value']
        ).mark_bar().encode(
            x=alt.X('value:Q', title=None, bin=True),
            y=alt.Y('count()', title='Frequency', stack=None),
            color=alt.Color('column:N')
        )

    def box(self, **kwargs):
        data = self._data.iloc[:, 1:]
        return alt.Chart(data).transform_fold(
            list(data.columns), as_=['column', 'value']
        ).mark_boxplot().encode(
            x=alt.X('column:N', title=None),
            y='value:Q'
        )


def plot(data, kind='line', **kwargs):
    """Pandas plotting interface for Altair."""
    plotter = _PandasPlotter.create(data)

    if hasattr(plotter, kind):
        plotfunc = getattr(plotter, kind)
    else:
        raise NotImplementedError(
            f"kind='{kind}' for data of type {type(data)}")

    return plotfunc(**kwargs)
