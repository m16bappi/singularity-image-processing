import pytest
from fastapi.testclient import TestClient
# from sqlmodel import create_engine, SQLModel, Session

from main import app

# Todo: Will split test DB
# TEST_DB_URL = "sqlite:///./test.db"
# engine = create_engine(TEST_DB_URL, echo=True)


# @pytest.fixture(scope="module")
# def test_session():
#     """Fixture to provide a temporary test session."""
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         yield session


@pytest.fixture(scope="module")
def client():
    """Fixture to create a test FastAPI client."""
    return TestClient(app)


@pytest.fixture
def sample_tiff(tmp_path):
    """Fixture to generate a sample TIFF file for testing."""
    import numpy as np
    import tifffile as tf

    tiff_path = tmp_path / "test_image.tif"
    image_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
    tf.imwrite(str(tiff_path), image_data)
    return tiff_path


def test_upload_image(client: TestClient, sample_tiff):
    """Test uploading an image."""
    with open(sample_tiff, "rb") as f:
        response = client.post("images/upload", files={"file": f})
    assert response.status_code == 200
    assert "media_path" in response.json()


def test_get_images(client: TestClient):
    """Test fetching the list of images."""
    response = client.get("images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_image_metadata(client: TestClient):
    """Test fetching metadata of an uploaded image."""
    response = client.get("images/1/metadata")
    assert response.status_code == 200
    assert "image_shape" in response.json()


def test_get_image_statistics(client: TestClient):
    """Test fetching image statistics."""
    response = client.get("images/1/statistics")
    assert response.status_code == 200
    assert "mean" in response.json()
    assert "std_dev" in response.json()


def test_perform_pca(client: TestClient):
    """Test performing PCA on an image."""
    response = client.get("images/1/analyze")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/tiff"
