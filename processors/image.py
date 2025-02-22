from uuid import uuid4
from fastapi import UploadFile, HTTPException
import os, tifffile as tf, numpy as np

# internal module
from models import ImageMetadata


class ImageProcessor:
    BASE_DIR = "media"
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, image: ImageMetadata):
        self.image = image
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def stats(self):
        try:
            total_pixels = 0
            sum_values = 0
            sum_squares = 0
            min_value = np.inf
            max_value = -np.inf
            with tf.TiffFile(self.image.media_path) as tif:
                for page in tif.pages:
                    for chunk in page.asarray(out="memmap"):
                        chunk = chunk.astype(np.float64)
                        total_pixels += chunk.size
                        sum_values += np.sum(chunk)
                        sum_squares += np.sum(chunk**2)
                        min_value = min(min_value, np.min(chunk))
                        max_value = max(max_value, np.max(chunk))

            # Calculate final statistics
            mean = sum_values / total_pixels
            std_dev = np.sqrt((sum_squares / total_pixels) - (mean**2))

            return {
                "mean": mean.tolist(),
                "std_dev": std_dev.tolist(),
                "min": min_value.tolist(),
                "max": max_value.tolist(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def save_image(cls, file: UploadFile) -> str:
        filename = f"{uuid4().hex}.tiff"
        file_path = os.path.join(cls.BASE_DIR, filename)

        with open(file_path, "wb") as buffer:
            while chunk := await file.read(cls.CHUNK_SIZE):
                buffer.write(chunk)

        return file_path
