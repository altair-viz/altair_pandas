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
