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
    def __init__(self, data):
        if not isinstance(data, pd.Series):
            raise ValueError(f"data: expected pd.Series; got {type(data)}")
        self._data = data

    def _preprocess_data(self, with_index=True):
        if with_index:
            if isinstance(self._data.index, pd.MultiIndex):
                raise NotImplementedError("Multi-indexed data.")
            out = self._data.reset_index()
        else:
            out = self._data.to_frame()
        if not self._data.name:
            out.columns[-1] = 'value'
        return out

    def _xy(self, mark='line', **kwargs):
        data = self._preprocess_data(with_index=True)
        return alt.Chart(data, mark=mark).encode(
            x=alt.X(data.columns[0], title=None),
            y=alt.Y(data.columns[1], title=None),
            tooltip=list(data.columns)
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
        data = self._preprocess_data(with_index=False)
        column = data.columns[0]
        return alt.Chart(data).mark_bar().encode(
            x=alt.X(column, title=None, bin=True),
            y=alt.Y('count()', title='Frequency'),
        )

    def box(self, **kwargs):
        data = self._preprocess_data(with_index=False)
        return alt.Chart(data).transform_fold(
            list(data.columns), as_=['column', 'value']
        ).mark_boxplot().encode(
            x=alt.X('column:N', title=None),
            y='value:Q',
        )


class _DataFramePlotter(_PandasPlotter):
    """Functionality for plotting of pandas DataFrames."""
    def __init__(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"data: expected pd.DataFrame; got {type(data)}")
        self._data = data

    def _preprocess_data(self, with_index=True, usecols=None):
        data = self._data
        if usecols is not None:
            data = data[usecols]
        if with_index:
            if isinstance(self._data.index, pd.MultiIndex):
                raise NotImplementedError("Multi-indexed data.")
            return data.reset_index()
        return data

    def _xy(self, mark, x=None, y=None, **kwargs):
        data = self._preprocess_data(with_index=True)
        if x is None:
            x = data.columns[0]
        else:
            assert x in data.columns
        if y is None:
            y_values = list(data.columns[1:])
        else:
            assert y in data.columns
            y_values = [y]

        return alt.Chart(
            data,
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
        data = self._preprocess_data(with_index=False, usecols=columns)
        encodings['tooltip'] = columns
        return alt.Chart(data).mark_point().encode(
            **encodings
        ).interactive()

    def hist(self, **kwargs):
        data = self._preprocess_data(with_index=False)
        return alt.Chart(data).transform_fold(
            list(data.columns), as_=['column', 'value']
        ).mark_bar().encode(
            x=alt.X('value:Q', title=None, bin=True),
            y=alt.Y('count()', title='Frequency', stack=None),
            color=alt.Color('column:N')
        )

    def box(self, **kwargs):
        data = self._preprocess_data(with_index=False)
        return alt.Chart(data).transform_fold(
            list(data.columns), as_=['column', 'value']
        ).mark_boxplot().encode(
            x=alt.X('column:N', title=None),
            y='value:Q',
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
