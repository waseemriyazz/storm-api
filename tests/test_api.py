import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app instance from your main application file
# Adjust the import path if your app instance is located elsewhere
from api.routes import app, get_settings
from core.config import Settings

# Create a TestClient instance
client = TestClient(app)

# --- Test Data ---
MOCK_TOPIC = "testing fastapi"
MOCK_ARTICLE_CONTENT = "This is a mock article about testing fastapi."


# --- Fixture to override settings dependency ---
# This allows us to provide mock settings for tests,
# ensuring we don't rely on a real .env file during testing.
@pytest.fixture
def override_settings():
    # Define mock settings values
    mock_settings = Settings(
        google_api_key="fake_google_key", serper_api_key="fake_serper_key"
    )

    # Define the dependency override function
    def get_mock_settings():
        return mock_settings

    # Apply the override
    app.dependency_overrides[get_settings] = get_mock_settings
    yield  # Test runs here
    # Clean up the override after the test
    app.dependency_overrides = {}


# --- Test Cases ---


# Use the fixture to ensure settings are mocked
def test_storm_endpoint_success_no_stream(override_settings):
    """
    Test the /storm endpoint for a successful non-streaming request.
    Mocks the actual run_storm function.
    """
    # Mock the core function that interacts with STORM/external APIs
    with patch("api.routes.run_storm") as mock_run_storm:
        # Configure the mock to return a simple string
        mock_run_storm.return_value = MOCK_ARTICLE_CONTENT

        # Make the request to the endpoint
        response = client.post("/storm", json={"topic": MOCK_TOPIC, "stream": False})

        # Assertions
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        expected_json = {"article": MOCK_ARTICLE_CONTENT}
        assert response.json() == expected_json

        # Verify that run_storm was called correctly
        mock_run_storm.assert_called_once_with(
            topic=MOCK_TOPIC,
            google_api_key="fake_google_key",  # Check against mocked settings
            serper_api_key="fake_serper_key",  # Check against mocked settings
        )


def test_storm_endpoint_empty_topic(override_settings):
    """
    Test the /storm endpoint with an empty topic string.
    Expects a 400 Bad Request error.
    """
    response = client.post("/storm", json={"topic": "", "stream": False})
    assert response.status_code == 400
    assert "Topic must be a non-empty string" in response.json()["detail"]


# TODO: Add tests for streaming response
# TODO: Add tests for internal server errors (mocking run_storm exception)
# TODO: Add tests for missing API keys in settings (modify fixture)
