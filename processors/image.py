import os, io
import numpy as np
import tifffile as tf
from uuid import uuid4
from sklearn.decomposition import PCA
from fastapi import UploadFile, HTTPException, Response

# Internal module
from models import ImageMetadata


class ImageProcessor:
    BASE_DIR = "media"
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, image: ImageMetadata):
        self.image = image
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def metadata(self):
        try:
            with tf.TiffFile(self.image.media_path) as tif:
                first_page = tif.pages[0]
                metadata = {
                    "file_size_bytes": os.path.getsize(self.image.media_path),
                    "image_shape": tif.series[0].shape if tif.series else None,
                    "dtype": str(tif.series[0].dtype) if tif.series else None,
                    "bit_depth": first_page.bitspersample if first_page else None,
                    "number_of_pages": len(tif.pages),
                }
                return metadata
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Metadata extraction error: {str(e)}"
            )

    def stats(self):
        try:
            with tf.TiffFile(self.image.media_path) as image:

                total_pixels, sum_values, sum_squares = 0, 0, 0
                min_value, max_value = np.inf, -np.inf

                for page in image.pages:
                    """
                    Todo: We can use multi-thread here for processing faster
                    """
                    for chunk in page.asarray(out="memmap"):
                        chunk = chunk.astype(np.float64)
                        total_pixels += chunk.size
                        sum_values += np.sum(chunk)
                        sum_squares += np.sum(chunk**2)
                        min_value = min(min_value, np.min(chunk))
                        max_value = max(max_value, np.max(chunk))

                mean = sum_values / total_pixels
                std_dev = np.sqrt((sum_squares / total_pixels) - (mean**2))

                return {
                    "mean": mean,
                    "std_dev": std_dev,
                    "min": min_value,
                    "max": max_value,
                }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Statistics calculation error: {str(e)}"
            )

    def perform_pca(self, n_components=2):
        try:
            with tf.TiffFile(self.image.media_path) as image:
                image = image.asarray()

                if image.ndim < 3:
                    raise HTTPException(
                        status_code=400, detail="Image must have at least 3 dimensions"
                    )

                original_shape = image.shape
                num_pixels = np.prod(original_shape[:-1])
                num_channels = original_shape[-1]

                reshaped_image = image.reshape(num_pixels, num_channels)

                pca = PCA(n_components=n_components)
                reduced_image = pca.fit_transform(reshaped_image)

                new_shape = original_shape[:-1] + (n_components,)
                reduced_image = reduced_image.reshape(new_shape)

                buffer = io.BytesIO()
                tf.imwrite(buffer, reduced_image.astype(np.float32))
                return Response(content=buffer.getvalue(), media_type="image/tiff")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"PCA processing error: {str(e)}"
            )

    @classmethod
    async def save_image(cls, file: UploadFile) -> str:
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        try:
            extension = os.path.splitext(file.filename)[-1]
            filename = f"{uuid4().hex}{extension}"
            file_path = os.path.join(cls.BASE_DIR, filename)

            with open(file_path, "wb") as buffer:
                while chunk := await file.read(cls.CHUNK_SIZE):
                    buffer.write(chunk)

            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File saving error: {str(e)}")
