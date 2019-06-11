import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--front", action="store", default="", help="front uri"
    )
    parser.addoption(
        "--broker", action="store", default="9999", help="broker ID"
    )
    parser.addoption(
        "--user", action="store", default="", help="user ID"
    )
    parser.addoption(
        "--password", action="store", default="", help="password"
    )
    parser.addoption(
        "--app", action="store", default="", help="app ID"
    )
    parser.addoption(
        "--auth", action="store", default="0000000000000000", help="app ID"
    )
    parser.addoption(
        "--instrument", action="store", default="IF1907", help="instrument ID"
    )
    parser.addoption(
        "--exchange", action="store", default="CFE", help="exchange ID"
    )

@pytest.fixture
def front(request):
    return request.config.getoption("--front")

@pytest.fixture
def broker(request):
    return request.config.getoption("--broker")

@pytest.fixture
def user(request):
    return request.config.getoption("--user")

@pytest.fixture
def password(request):
    return request.config.getoption("--password")

@pytest.fixture
def app(request):
    return request.config.getoption("--app")

@pytest.fixture
def auth(request):
    return request.config.getoption("--auth")

@pytest.fixture
def instrument(request):
    return request.config.getoption("--instrument")

@pytest.fixture
def exchange(request):
    return request.config.getoption("--exchange")