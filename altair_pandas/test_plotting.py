import pytest
import pandas as pd


@pytest.fixture
def with_altair_backend():
    pd.set_option('plotting.backend', 'altair_pandas')
    yield pd
    pd.set_option('plotting.backend', 'matplotlib')


def test_series_line_plot(with_altair_backend):
    data = pd.Series(range(5), name='data_name')
    chart = data.plot()
    spec = chart.to_dict()
    assert spec['mark'] == 'line'
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['y']['field'] == 'data_name'


def test_dataframe_line_plot(with_altair_backend):
    data = pd.DataFrame({'x': range(5), 'y': range(5)})
    chart = data.plot()
    spec = chart.to_dict()
    assert spec['mark'] == 'line'
    assert spec['encoding']['x']['field'] == 'index'
    assert spec['encoding']['y']['field'] == 'value'
    assert spec['encoding']['color']['field'] == 'column'
    assert spec['transform'][0]['fold'] == ['x', 'y']