import pytest
import numpy as np
import pandas as pd


@pytest.fixture
def series():
    return pd.Series(range(5), name='data_name')


@pytest.fixture
def dataframe():
    return pd.DataFrame({'x': range(5), 'y': range(5)})


@pytest.mark.parametrize('data', [
    pd.Series(
        range(6),
        index=pd.MultiIndex.from_product([['a', 'b', 'c'], [1, 2]])
    ),
    pd.DataFrame(
        {'x': range(6)},
        index=pd.MultiIndex.from_product([['a', 'b', 'c'], [1, 2]])
    )
])
def test_multiindex(data, with_plotting_backend):
    chart = data.plot.bar()
    spec = chart.to_dict()
    assert list(chart.data.iloc[:, 0]) == [str(i) for i in data.index]
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['x']['type'] == 'nominal'


def test_nonstring_column_names(with_plotting_backend):
    data = pd.DataFrame(np.ones((3, 4)))
    chart = data.plot.scatter(x=0, y=1, c=2, s=3)

    # Ensure data is not modified
    assert list(data.columns) == list(range(4))
    # Ensure chart data has string columns
    assert set(chart.data.columns) == {str(i) for i in range(4)}

    spec = chart.to_dict()
    assert spec['encoding']['x']['field'] == '0'
    assert spec['encoding']['y']['field'] == '1'
    assert spec['encoding']['color']['field'] == '2'
    assert spec['encoding']['size']['field'] == '3'


@pytest.mark.parametrize('kind', ['line', 'area', 'bar'])
def test_series_basic_plot(series, kind, with_plotting_backend):
    chart = series.plot(kind=kind)
    spec = chart.to_dict()
    if isinstance(spec['mark'], dict):
        assert spec['mark']['type'] == kind
    else:
        assert spec['mark'] == kind
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['y']['field'] == 'data_name'


@pytest.mark.parametrize('kind', ['line', 'area', 'bar'])
def test_dataframe_basic_plot(dataframe, kind, with_plotting_backend):
    chart = dataframe.plot(kind=kind)
    spec = chart.to_dict()
    if isinstance(spec['mark'], dict):
        assert spec['mark']['type'] == kind
    else:
        assert spec['mark'] == kind
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['y']['field'] == 'value'
    assert spec['encoding']['color']['field'] == 'column'
    assert spec['transform'][0]['fold'] == ['x', 'y']


def test_series_barh(series, with_plotting_backend):
    chart = series.plot.barh()
    spec = chart.to_dict()
    assert spec['mark'] == {'type': 'bar', 'orient': 'vertical'}
    assert spec['encoding']['y']['field'] == 'index'
    assert spec['encoding']['x']['field'] == 'data_name'


def test_dataframe_barh(dataframe, with_plotting_backend):
    chart = dataframe.plot.barh()
    spec = chart.to_dict()
    assert spec['mark'] == {'type': 'bar', 'orient': 'vertical'}
    assert spec['encoding']['y']['field'] == 'index'
    assert spec['encoding']['x']['field'] == 'value'
    assert spec['encoding']['color']['field'] == 'column'
    assert spec['transform'][0]['fold'] == ['x', 'y']


def test_series_scatter_plot(series, with_plotting_backend):
    with pytest.raises(ValueError):
        series.plot.scatter('x', 'y')


def test_dataframe_scatter_plot(dataframe, with_plotting_backend):
    dataframe['c'] = range(len(dataframe))
    chart = dataframe.plot.scatter('x', 'y', c='y', s='x')
    spec = chart.to_dict()
    assert spec['mark'] == 'point'
    assert spec['encoding']['x']['field'] == 'x'
    assert spec['encoding']['y']['field'] == 'y'
    assert spec['encoding']['color']['field'] == 'y'
    assert spec['encoding']['size']['field'] == 'x'


def test_series_hist(series, with_plotting_backend):
    chart = series.plot.hist()
    spec = chart.to_dict()
    assert spec['mark'] == 'bar'
    assert spec['encoding']['x']['field'] == 'data_name'
    assert 'field' not in spec['encoding']['y']


def test_dataframe_hist(dataframe, with_plotting_backend):
    chart = dataframe.plot.hist()
    spec = chart.to_dict()
    assert spec['mark'] == 'bar'
    assert spec['encoding']['x']['field'] == 'value'
    assert 'field' not in spec['encoding']['y']
    assert spec['encoding']['color']['field'] == 'column'
    assert spec['transform'][0]['fold'] == ['x', 'y']


def test_series_boxplot(series, with_plotting_backend):
    chart = series.plot.box()
    spec = chart.to_dict()
    assert spec['mark'] == 'boxplot'
    assert spec['encoding']['x']['field'] == 'column'
    assert spec['encoding']['y']['field'] == 'value'
    assert spec['transform'][0]['fold'] == ['data_name']


def test_dataframe_boxplot(dataframe, with_plotting_backend):
    chart = dataframe.plot.box()
    spec = chart.to_dict()
    assert spec['mark'] == 'boxplot'
    assert spec['encoding']['x']['field'] == 'column'
    assert spec['encoding']['y']['field'] == 'value'
    assert spec['transform'][0]['fold'] == ['x', 'y']
