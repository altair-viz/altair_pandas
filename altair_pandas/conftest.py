import pytest
import pandas as pd


def pytest_addoption(parser):
    parser.addoption(
        "--backend_name",
        action="store",
        default="altair_pandas",
        help="Plotting backend to use.",
    )


@pytest.fixture(scope="session")
def with_plotting_backend(request):
    default = pd.get_option("plotting.backend")
    pd.set_option("plotting.backend", request.config.getoption("backend_name"))
    yield
    try:
        pd.set_option("plotting.backend", default)
    except ImportError:
        pass  # matplotlib is not installed.
