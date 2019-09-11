import pytest
import numpy as np
import pandas as pd
import altair as alt


@pytest.fixture
def series():
    return pd.Series(range(5), name="data_name")


@pytest.fixture
def dataframe():
    return pd.DataFrame({"x": range(5), "y": range(5)})


def _expected_mark(kind):
    marks = {"barh": "bar", "hist": "bar", "box": "boxplot"}
    return marks.get(kind, kind)


@pytest.mark.parametrize(
    "data",
    [
        pd.Series(
            range(6), index=pd.MultiIndex.from_product([["a", "b", "c"], [1, 2]])
        ),
        pd.DataFrame(
            {"x": range(6)}, index=pd.MultiIndex.from_product([["a", "b", "c"], [1, 2]])
        ),
    ],
)
def test_multiindex(data, with_plotting_backend):
    chart = data.plot.bar()
    spec = chart.to_dict()
    assert list(chart.data.iloc[:, 0]) == [str(i) for i in data.index]
    assert spec["encoding"]["x"]["field"] == "index"
    assert spec["encoding"]["x"]["type"] == "nominal"


def test_nonstring_column_names(with_plotting_backend):
    data = pd.DataFrame(np.ones((3, 4)))
    chart = data.plot.scatter(x=0, y=1, c=2, s=3)

    # Ensure data is not modified
    assert list(data.columns) == list(range(4))
    # Ensure chart data has string columns
    assert set(chart.data.columns) == {str(i) for i in range(4)}

    spec = chart.to_dict()
    assert spec["encoding"]["x"]["field"] == "0"
    assert spec["encoding"]["y"]["field"] == "1"
    assert spec["encoding"]["color"]["field"] == "2"
    assert spec["encoding"]["size"]["field"] == "3"


@pytest.mark.parametrize("kind", ["line", "area", "bar", "barh"])
def test_series_basic_plot(series, kind, with_plotting_backend):
    chart = series.plot(kind=kind)
    spec = chart.to_dict()

    x, y = "x", "y"
    if kind == "bar":
        assert spec["mark"]["orient"] == "vertical"
    if kind == "barh":
        assert spec["mark"]["orient"] == "horizontal"
        x, y = y, x

    assert spec["mark"]["type"] == _expected_mark(kind)
    assert spec["encoding"][x]["field"] == "index"
    assert spec["encoding"][y]["field"] == "data_name"


@pytest.mark.parametrize("stacked", [True, False])
@pytest.mark.parametrize("subplots", [False, True])
@pytest.mark.parametrize("kind", ["line", "area", "bar", "barh"])
def test_dataframe_basic_plot(
    dataframe, kind, stacked, subplots, with_plotting_backend
):
    chart = dataframe.plot(kind=kind, stacked=stacked, subplots=subplots)
    spec = chart.to_dict()

    x, y = "x", "y"
    if kind == "bar":
        assert spec["mark"]["orient"] == "vertical"
    if kind == "barh":
        assert spec["mark"]["orient"] == "horizontal"
        x, y = y, x

    assert spec["mark"]["type"] == _expected_mark(kind)
    assert spec["encoding"][x]["field"] == "index"
    assert spec["encoding"][y]["field"] == "value"
    assert spec["encoding"][y]["stack"] == stacked
    assert spec["encoding"]["color"]["field"] == "column"
    assert spec["transform"][0]["fold"] == ["x", "y"]
    if subplots:
        assert spec["encoding"]["facet"]["field"] == "column"
        assert spec["columns"] == 1
    else:
        assert "facet" not in spec["encoding"]


def test_series_barh(series, with_plotting_backend):
    chart = series.plot.barh()
    spec = chart.to_dict()
    assert spec["mark"] == {"type": "bar", "orient": "horizontal"}
    assert spec["encoding"]["y"]["field"] == "index"
    assert spec["encoding"]["x"]["field"] == "data_name"


def test_dataframe_barh(dataframe, with_plotting_backend):
    chart = dataframe.plot.barh()
    spec = chart.to_dict()
    assert spec["mark"] == {"type": "bar", "orient": "horizontal"}
    assert spec["encoding"]["y"]["field"] == "index"
    assert spec["encoding"]["x"]["field"] == "value"
    assert spec["encoding"]["color"]["field"] == "column"
    assert spec["transform"][0]["fold"] == ["x", "y"]


def test_series_scatter_plot(series, with_plotting_backend):
    with pytest.raises(ValueError):
        series.plot.scatter("x", "y")


def test_dataframe_scatter_plot(dataframe, with_plotting_backend):
    dataframe["c"] = range(len(dataframe))
    chart = dataframe.plot.scatter("x", "y", c="y", s="x")
    spec = chart.to_dict()
    assert spec["mark"] == {"type": "point"}
    assert spec["encoding"]["x"]["field"] == "x"
    assert spec["encoding"]["y"]["field"] == "y"
    assert spec["encoding"]["color"]["field"] == "y"
    assert spec["encoding"]["size"]["field"] == "x"


@pytest.mark.parametrize("bins", [None, 10])
@pytest.mark.parametrize("orientation", ["vertical", "horizontal"])
def test_series_hist(series, bins, orientation, with_plotting_backend):
    chart = series.plot.hist(bins=bins, orientation=orientation)
    spec = chart.to_dict()
    x, y = ("x", "y") if orientation == "vertical" else ("y", "x")

    assert spec["mark"]["type"] == "bar"
    assert spec["mark"]["orient"] == orientation
    assert spec["encoding"][x]["field"] == "data_name"
    assert "field" not in spec["encoding"][y]
    exp_bin = True if bins is None else {"maxbins": bins}
    assert spec["encoding"][x]["bin"] == exp_bin


@pytest.mark.parametrize("bins", [None, 10])
@pytest.mark.parametrize("stacked", [None, True, False])
@pytest.mark.parametrize("orientation", ["vertical", "horizontal"])
def test_dataframe_hist(dataframe, bins, stacked, orientation, with_plotting_backend):
    chart = dataframe.plot.hist(bins=bins, stacked=stacked, orientation=orientation)
    spec = chart.to_dict()
    x, y = ("x", "y") if orientation == "vertical" else ("y", "x")
    assert spec["mark"]["type"] == "bar"
    assert spec["mark"]["orient"] == orientation
    assert spec["encoding"][x]["field"] == "value"
    assert "field" not in spec["encoding"][y]
    assert spec["encoding"]["color"]["field"] == "column"
    assert spec["transform"][0]["fold"] == ["x", "y"]
    exp_bin = True if bins is None else {"maxbins": bins}
    assert spec["encoding"][x]["bin"] == exp_bin
    assert spec["encoding"][y]["stack"] == (True if stacked else stacked)


@pytest.mark.parametrize("vert", [True, False])
def test_series_boxplot(series, vert, with_plotting_backend):
    chart = series.plot.box(vert=vert)
    spec = chart.to_dict()
    assert spec["mark"] == "boxplot"
    assert spec["transform"][0]["fold"] == ["data_name"]
    fields = ["column", "value"] if vert else ["value", "column"]
    assert spec["encoding"]["x"]["field"] == fields[0]
    assert spec["encoding"]["y"]["field"] == fields[1]


@pytest.mark.parametrize("vert", [True, False])
def test_dataframe_boxplot(dataframe, vert, with_plotting_backend):
    chart = dataframe.plot.box(vert=vert)
    spec = chart.to_dict()
    assert spec["mark"] == "boxplot"
    assert spec["transform"][0]["fold"] == ["x", "y"]
    fields = ["column", "value"] if vert else ["value", "column"]
    assert spec["encoding"]["x"]["field"] == fields[0]
    assert spec["encoding"]["y"]["field"] == fields[1]


def test_hist_series(series, with_plotting_backend):
    chart = series.hist()
    spec = chart.to_dict()
    assert spec["mark"]["type"] == "bar"
    assert spec["encoding"]["x"]["field"] == "data_name"
    assert "field" not in spec["encoding"]["y"]
    assert spec["encoding"]["x"]["bin"] == {"maxbins": 10}


def test_hist_frame(dataframe, with_plotting_backend):
    chart = dataframe.hist(layout=(-1, 1))
    spec = chart.to_dict()
    assert spec["repeat"] == ["x", "y"]
    assert spec["columns"] == 1
    assert spec["spec"]["mark"] == {"type": "bar"}
    assert spec["spec"]["encoding"]["x"]["field"] == {"repeat": "repeat"}
    assert spec["spec"]["encoding"]["x"]["bin"] is True
    assert "field" not in spec["spec"]["encoding"]["y"]


@pytest.mark.parametrize("kind", ["hist", "line", "bar", "barh"])
def test_dataframe_mark_properties(dataframe, kind, with_plotting_backend):
    chart = dataframe.plot(kind=kind, alpha=0.5, color="red")
    spec = chart.to_dict()
    assert spec["mark"]["type"] == _expected_mark(kind)
    assert spec["mark"]["opacity"] == 0.5
    assert spec["mark"]["color"] == "red"


@pytest.mark.parametrize("kind", ["hist", "line", "bar", "barh"])
def test_series_mark_properties(series, kind, with_plotting_backend):
    chart = series.plot(kind=kind, alpha=0.5, color="red")
    spec = chart.to_dict()
    assert spec["mark"]["type"] == _expected_mark(kind)
    assert spec["mark"]["opacity"] == 0.5
    assert spec["mark"]["color"] == "red"


@pytest.mark.parametrize("stacked", [True, False])
def test_dataframe_area(dataframe, stacked, with_plotting_backend):
    chart = dataframe.plot.area(stacked=stacked)
    spec = chart.to_dict()
    mark = (
        {"type": "area"} if stacked else {"type": "area", "line": True, "opacity": 0.5}
    )
    assert spec["mark"] == mark
    for k, v in {"x": "index", "y": "value", "color": "column"}.items():
        assert spec["encoding"][k]["field"] == v
    assert spec["transform"][0]["fold"] == ["x", "y"]


@pytest.mark.parametrize("alpha", [1.0, 0.2])
@pytest.mark.parametrize("color", [None, "x", "z"])
@pytest.mark.parametrize(
    "tooltip",
    [
        None,
        ["x", "y"],
        [alt.Tooltip("x", format="$.2f"), alt.Tooltip("z", format=".0%")],
    ],
)
def test_scatter_matrix(dataframe, alpha, color, tooltip, with_plotting_backend):
    from altair_pandas import scatter_matrix

    dataframe["z"] = ["A", "B", "C", "D", "E"]

    chart = scatter_matrix(dataframe, alpha=alpha, color=color, tooltip=tooltip)
    spec = chart.to_dict()

    cols = dataframe._get_numeric_data().columns.astype(str).tolist()
    for k, v in spec["repeat"].items():
        assert set(v) == set(cols)

    if color is None:
        assert "color" not in spec["spec"]["encoding"]
    elif color == "x":
        assert spec["spec"]["encoding"]["color"] == {
            "type": "quantitative",
            "field": "x",
        }

    assert spec["spec"]["encoding"]["opacity"] == {"value": alpha}

    if tooltip is None:
        assert set(el["field"] for el in spec["spec"]["encoding"]["tooltip"]) == {
            "x",
            "y",
            "z",
        }
    elif tooltip == ["x", "y"]:
        assert len(spec["spec"]["encoding"]["tooltip"]) == 2
        assert set(el["field"] for el in spec["spec"]["encoding"]["tooltip"]) == {
            "x",
            "y",
        }
    else:
        assert len(spec["spec"]["encoding"]["tooltip"]) == 2
        assert set(el["field"] for el in spec["spec"]["encoding"]["tooltip"]) == {
            "x",
            "z",
        }
        assert spec["spec"]["encoding"]["tooltip"][0]["format"] == "$.2f"


@pytest.mark.parametrize("colormap", ["viridis", "goldgreen"])
@pytest.mark.parametrize("color", ["x", "z"])
def test_scatter_colormap(dataframe, colormap, color, with_plotting_backend):
    from altair_pandas import scatter_matrix

    if color == "z":
        dataframe["z"] = ["A", "B", "C", "D", "E"]

    chart = scatter_matrix(dataframe, color=color, colormap=colormap)
    spec = chart.to_dict()

    assert spec["spec"]["encoding"]["color"]["scale"]["scheme"] == colormap


@pytest.mark.parametrize(
    "indx, data",
    {
        "index": pd.DataFrame(
            {"x": range(6)}, index=pd.MultiIndex.from_product([["a", "b", "c"], [1, 2]])
        ),
        "columns": pd.DataFrame(
            {"x": range(6)}, index=pd.MultiIndex.from_product([["a", "b", "c"], [1, 2]])
        ).T,
    }.items(),
)
def test_scatter_multiindex(indx, data, with_plotting_backend):
    from altair_pandas import scatter_matrix

    chart = scatter_matrix(data)
    spec = chart.to_dict()

    cols = (
        {"x"}
        if indx == "index"
        else ({"('b', 2)", "('b', 1)", "('c', 2)", "('a', 2)", "('c', 1)", "('a', 1)"})
    )

    for k, v in spec["repeat"].items():
        assert set(v) == cols
