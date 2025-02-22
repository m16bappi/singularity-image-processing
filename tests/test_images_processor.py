import pytest
import numpy as np
import tifffile as tf
from processors import ImageProcessor
from models import ImageMetadata


@pytest.fixture
def sample_image(tmp_path):
    """Fixture to generate a sample TIFF file."""
    file_path = tmp_path / "sample.tif"
    image_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
    tf.imwrite(str(file_path), image_data)
    return ImageMetadata(media_path=str(file_path))


def test_metadata(sample_image):
    """Test metadata extraction."""
    processor = ImageProcessor(sample_image)
    metadata = processor.metadata()

    assert metadata["image_shape"] == (10, 10, 3)
    assert metadata["dtype"] == "uint8"
    assert metadata["bit_depth"] is not None


def test_stats(sample_image):
    """Test statistics computation."""
    processor = ImageProcessor(sample_image)
    stats = processor.stats()

    assert "mean" in stats
    assert "std_dev" in stats
    assert "min" in stats
    assert "max" in stats


def test_perform_pca(sample_image):
    """Test PCA transformation."""
    processor = ImageProcessor(sample_image)
    response = processor.perform_pca(n_components=2)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/tiff"
