import altair as alt
import pandas as pd
import numpy as np


def _valid_column(column_name):
    """Return a valid column name."""
    return str(column_name)


def _get_layout(panels, layout=None):
    """Compute the layout for a gridded chart.

    Parameters
    ----------
    panels : int
        Number of panels in the chart.
    layout : tuple of ints
        Control the layout. Negative entries will be inferred
        from the number of panels.

    Returns
    -------
    nrows, ncols : int, int
        number of rows and columns in the resulting layout.

    Examples
    --------
    >>> _get_layout(6, (2, 3))
    (2, 3)
    >>> _get_layout(6, (1, -1))
    (1, 6)
    >>> _get_layout(6, (-1, 2))
    (3, 2)
    """
    if layout is None:
        layout = (-1, 2)
    if len(layout) != 2:
        raise ValueError("layout should have two elements")
    if layout[0] < 0 and layout[1] < 0:
        raise ValueError("At least one dimension of layout must be positive")
    if layout[0] < 0:
        layout = (int(np.ceil(panels / layout[1])), layout[1])
    if layout[1] < 0:
        layout = (layout[0], int(np.ceil(panels / layout[0])))
    if panels > layout[0] * layout[1]:
        raise ValueError(f"layout {layout[0]}x{layout[1]} must be larger than {panels}")
    return layout


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

    def _get_mark_def(self, mark, kwargs):
        if isinstance(mark, str):
            mark = {"type": mark}
        if isinstance(kwargs.get("alpha"), float):
            mark["opacity"] = kwargs.pop("alpha")
        if isinstance(kwargs.get("color"), str):
            mark["color"] = kwargs.pop("color")
        return mark


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
                    [str(i) for i in data.index], name=data.index.name
                )
            data = data.reset_index()
        else:
            data = data.to_frame()
        # Column names must all be strings.
        return data.rename(columns=_valid_column)

    def _xy(self, mark, **kwargs):
        data = self._preprocess_data(with_index=True)
        return (
            alt.Chart(data, mark=self._get_mark_def(mark, kwargs))
            .encode(
                x=alt.X(data.columns[0], title=None),
                y=alt.Y(data.columns[1], title=None),
                tooltip=list(data.columns),
            )
            .interactive()
        )

    def line(self, **kwargs):
        return self._xy("line", **kwargs)

    def bar(self, **kwargs):
        return self._xy({"type": "bar", "orient": "vertical"}, **kwargs)

    def barh(self, **kwargs):
        chart = self._xy({"type": "bar", "orient": "horizontal"}, **kwargs)
        chart.encoding.x, chart.encoding.y = chart.encoding.y, chart.encoding.x
        return chart

    def area(self, **kwargs):
        return self._xy(mark="area", **kwargs)

    def scatter(self, **kwargs):
        raise ValueError("kind='scatter' can only be used for DataFrames.")

    def hist(self, bins=None, orientation="vertical", **kwargs):
        data = self._preprocess_data(with_index=False)
        column = data.columns[0]
        if isinstance(bins, int):
            bins = alt.Bin(maxbins=bins)
        elif bins is None:
            bins = True
        if orientation == "vertical":
            Indep, Dep = alt.X, alt.Y
        elif orientation == "horizontal":
            Indep, Dep = alt.Y, alt.X
        else:
            raise ValueError("orientation must be 'horizontal' or 'vertical'.")

        mark = self._get_mark_def({"type": "bar", "orient": orientation}, kwargs)
        return alt.Chart(data, mark=mark).encode(
            Indep(column, title=None, bin=bins), Dep("count()", title="Frequency")
        )

    def hist_series(self, **kwargs):
        return self.hist(**kwargs)

    def box(self, vert=True, **kwargs):
        data = self._preprocess_data(with_index=False)
        chart = (
            alt.Chart(data)
            .transform_fold(list(data.columns), as_=["column", "value"])
            .mark_boxplot()
            .encode(x=alt.X("column:N", title=None), y="value:Q")
        )
        if not vert:
            chart.encoding.x, chart.encoding.y = chart.encoding.y, chart.encoding.x
        return chart


class _DataFramePlotter(_PandasPlotter):
    """Functionality for plotting of pandas DataFrames."""

    def __init__(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"data: expected pd.DataFrame; got {type(data)}")
        self._data = data

    def _preprocess_data(self, with_index=True, usecols=None):
        data = self._data.rename(columns=_valid_column)
        if usecols is not None:
            data = data[usecols]
        if with_index:
            if isinstance(data.index, pd.MultiIndex):
                data.index = pd.Index(
                    [str(i) for i in data.index], name=data.index.name
                )
            return data.reset_index()
        return data

    def _xy(self, mark, x=None, y=None, stacked=False, **kwargs):
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

        return (
            alt.Chart(data, mark=self._get_mark_def(mark, kwargs))
            .transform_fold(y_values, as_=["column", "value"])
            .encode(
                x=x,
                y=alt.Y("value:Q", title=None, stack=stacked),
                color=alt.Color("column:N", title=None),
                tooltip=[x] + y_values,
            )
            .interactive()
        )

    def line(self, x=None, y=None, **kwargs):
        return self._xy("line", x, y, **kwargs)

    def area(self, x=None, y=None, stacked=True, **kwargs):
        mark = "area" if stacked else {"type": "area", "line": True, "opacity": 0.5}
        return self._xy(mark, x, y, stacked, **kwargs)

    # TODO: bars should be grouped, not stacked.
    def bar(self, x=None, y=None, **kwargs):
        return self._xy({"type": "bar", "orient": "vertical"}, x, y, **kwargs)

    def barh(self, x=None, y=None, **kwargs):
        chart = self._xy({"type": "bar", "orient": "horizontal"}, x, y, **kwargs)
        chart.encoding.x, chart.encoding.y = chart.encoding.y, chart.encoding.x
        return chart

    def scatter(self, x, y, c=None, s=None, **kwargs):
        if x is None or y is None:
            raise ValueError("kind='scatter' requires 'x' and 'y' arguments.")
        encodings = {"x": _valid_column(x), "y": _valid_column(y)}
        if c is not None:
            encodings["color"] = _valid_column(c)
        if s is not None:
            encodings["size"] = _valid_column(s)
        columns = list(set(encodings.values()))
        data = self._preprocess_data(with_index=False, usecols=columns)
        encodings["tooltip"] = columns
        mark = self._get_mark_def("point", kwargs)
        return alt.Chart(data, mark=mark).encode(**encodings).interactive()

    def hist(self, bins=None, stacked=None, orientation="vertical", **kwargs):
        data = self._preprocess_data(with_index=False)
        if isinstance(bins, int):
            bins = alt.Bin(maxbins=bins)
        elif bins is None:
            bins = True
        if orientation == "vertical":
            Indep, Dep = alt.X, alt.Y
        elif orientation == "horizontal":
            Indep, Dep = alt.Y, alt.X
        else:
            raise ValueError("orientation must be 'horizontal' or 'vertical'.")

        mark = self._get_mark_def({"type": "bar", "orient": orientation}, kwargs)
        return (
            alt.Chart(data, mark=mark)
            .transform_fold(list(data.columns), as_=["column", "value"])
            .encode(
                Indep("value:Q", title=None, bin=bins),
                Dep("count()", title="Frequency", stack=stacked),
                color="column:N",
            )
        )

    def hist_frame(self, column=None, layout=(-1, 2), **kwargs):
        if column is not None:
            if isinstance(column, str):
                column = [column]
        data = self._preprocess_data(with_index=False, usecols=column)
        data = data._get_numeric_data()
        nrows, ncols = _get_layout(data.shape[1], layout)
        return (
            alt.Chart(data, mark=self._get_mark_def("bar", kwargs))
            .encode(
                x=alt.X(alt.repeat("repeat"), type="quantitative", bin=True),
                y=alt.Y("count()", title="Frequency"),
            )
            .repeat(repeat=list(data.columns), columns=ncols)
        )

    def box(self, vert=True, **kwargs):
        data = self._preprocess_data(with_index=False)
        chart = (
            alt.Chart(data)
            .transform_fold(list(data.columns), as_=["column", "value"])
            .mark_boxplot()
            .encode(x=alt.X("column:N", title=None), y="value:Q")
        )
        if not vert:
            chart.encoding.x, chart.encoding.y = chart.encoding.y, chart.encoding.x
        return chart


def plot(data, kind="line", **kwargs):
    """Pandas plotting interface for Altair."""
    plotter = _PandasPlotter.create(data)

    if hasattr(plotter, kind):
        plotfunc = getattr(plotter, kind)
    else:
        raise NotImplementedError(f"kind='{kind}' for data of type {type(data)}")

    return plotfunc(**kwargs)


def hist_frame(data, **kwargs):
    return _PandasPlotter.create(data).hist_frame(**kwargs)


def hist_series(data, **kwargs):
    return _PandasPlotter.create(data).hist_series(**kwargs)
