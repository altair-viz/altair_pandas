import pytest
import pandas as pd


@pytest.fixture
def series():
    return pd.Series(range(5), name='data_name')


@pytest.fixture
def dataframe():
    return pd.DataFrame({'x': range(5), 'y': range(5)})


@pytest.mark.parametrize('kind', ['line', 'area', 'bar'])
def test_series_line_plot(series, kind, with_plotting_backend):
    chart = series.plot(kind=kind)
    spec = chart.to_dict()
    assert spec['mark'] == kind
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['y']['field'] == 'data_name'


def test_dataframe_line_plot(dataframe, with_plotting_backend):
    chart = dataframe.plot()
    spec = chart.to_dict()
    assert spec['mark'] == 'line'
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['y']['field'] == 'value'
    assert spec['encoding']['color']['field'] == 'column'
    assert spec['transform'][0]['fold'] == ['x', 'y']


def test_series_scatter_plot(series, with_plotting_backend):
    with pytest.raises(ValueError):
        series.plot.scatter('x', 'y')


def test_dataframe_scatter_plot(dataframe, with_plotting_backend):
    dataframe['c'] = range(len(dataframe))
    chart = dataframe.plot.scatter('x', 'y', c='y')
    spec = chart.to_dict()
    assert spec['mark'] == 'point'
    assert spec['encoding']['x']['field'] == 'x'
    assert spec['encoding']['y']['field'] == 'y'
    assert spec['encoding']['color']['field'] == 'y'


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
