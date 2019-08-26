import altair as alt
import pandas as pd


def _valid_column(column_name):
    return str(column_name)


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
        # TODO: do this without copy?
        data = self._data
        if with_index:
            if isinstance(data.index, pd.MultiIndex):
                data = data.copy()
                data.index = pd.Index(
                    [str(i) for i in data.index], name=data.index.name)
            data = data.reset_index()
        else:
            data = data.to_frame()
        # Column names must all be strings.
        return data.rename(_valid_column, axis=1)

    def _xy(self, mark, **kwargs):
        data = self._preprocess_data(with_index=True)
        return alt.Chart(data, mark=mark).encode(
            x=alt.X(data.columns[0], title=None),
            y=alt.Y(data.columns[1], title=None),
            tooltip=list(data.columns)
        ).interactive()

    def line(self, **kwargs):
        return self._xy('line', **kwargs)

    def bar(self, **kwargs):
        return self._xy({'type': 'bar', 'orient': 'vertical'}, **kwargs)

    def barh(self, **kwargs):
        chart = self._xy({'type': 'bar', 'orient': 'horizontal'}, **kwargs)
        chart.encoding.x, chart.encoding.y = chart.encoding.y, chart.encoding.x
        return chart

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
        data = self._data.rename(_valid_column, axis=1)
        if usecols is not None:
            data = data[usecols]
        if with_index:
            if isinstance(data.index, pd.MultiIndex):
                data.index = pd.Index(
                    [str(i) for i in data.index], name=data.index.name)
            return data.reset_index()
        return data

    def _xy(self, mark, x=None, y=None, **kwargs):
        data = self._preprocess_data(with_index=True)

        if x is None:
            x = data.columns[0]
        else:
            x = _valid_column(x)
            assert x in data.columns

        if y is None:
            y_values = list(data.columns[1:])
        else:
            y = _valid_column(y)
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
        return self._xy(
            {'type': 'bar', 'orient': 'vertical'}, x, y, **kwargs)

    def barh(self, x=None, y=None, **kwargs):
        chart = self._xy(
            {'type': 'bar', 'orient': 'horizontal'}, x, y, **kwargs)
        chart.encoding.x, chart.encoding.y = chart.encoding.y, chart.encoding.x
        return chart

    def scatter(self, x, y, c=None, s=None, **kwargs):
        if x is None or y is None:
            raise ValueError("kind='scatter' requires 'x' and 'y' arguments.")
        encodings = {'x': _valid_column(x), 'y': _valid_column(y)}
        if c is not None:
            encodings['color'] = _valid_column(c)
        if s is not None:
            encodings['size'] = _valid_column(s)
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
