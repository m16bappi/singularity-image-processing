# Image Processing API - Documentation

This API is designed for uploading, processing, and analyzing TIFF images using FastAPI. It supports Principal Component Analysis (PCA) for dimensionality reduction and efficient TIFF image handling.

## Features
- Upload large TIFF images
- Extract image metadata (size, dimensions, bit depth, etc.)
- Perform PCA for dimensionality reduction while keeping the (X, Y, Z, T, C) format
- Memory-efficient processing using `memmap`
- Return optimized images via API without saving

## Project Structure
```
fastapi-image-api/
├── processors/ 
│   ├── image.py      
├── models/            
│   ├── image.py      
├── routes/            
│   ├── image.py      
├── tests/             
│   ├── test_image_api.py      
│   ├── test_image_processor.py 
├── main.py            
├── README.md         
└── requirements.txt
```

## Installation & Setup

### Clone the Repository
```
git clone https://github.com/m16bappi/singularity-image-processing.git
cd singularity-image-processing
```

### Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Run the FastAPI Application
```
fastapi dev main.py
```

### Get API docs Swagger
```
http://127.0.0.1:8000/docs
```

## API Endpoints

### Upload an Image
- **Endpoint:** `POST images/upload`
- **Request:** Multipart file upload (`image/tiff`)
- **Response Example:**
```
{
    "id": 1,
    "file_size_bytes": 2048000,
    "image_shape": [256, 256, 3],
    "dtype": "uint8",
    "bit_depth": 16
}
```

### Get Image Metadata
- **Endpoint:** `GET images/{id}/metadata`
- **Response Example:**
```
{
    "file_size_bytes": 2048000,
    "image_shape": [3, 5, 64, 64, 3],
    "dtype": "uint8",
    "bit_depth": 16,
    "number_of_pages": 15
}
```

### Get Image Stats
- **Endpoint:** `GET images/{id}/statistics`
- **Response Example:**
```
{
    "mean": 172.0023,
    "std_dev": 53.0012,
    "min": "0",
    "max": "255",
}
```

### Perform PCA on Image
- **Endpoint:** `GET images/{id}/analyze`
- **Request Parameters:** `n_components` (optional, default: `3`)
- **Response:** Returns PCA-processed TIFF file directly
```
curl -X 'GET' 'http://127.0.0.1:8000/images/{id}/analyze' -o reduced_pca_output.tiff
```

## How PCA Works
1. Loads TIFF as a memory-mapped file (`memmap`) to handle large files efficiently.
2. Extracts the `(X, Y, Z, T, C)` shape.
3. Applies PCA only on `C` (channels) while preserving `(X, Y, Z, T)`.
4. Returns the processed TIFF file via API.

## How to Test

### Run all tests
```
pytest -v
```

## Technology Stack
| Technology       | Purpose                         |
|-----------------|---------------------------------|
| FastAPI         | Web framework for building API |
| tifffile        | Handling TIFF images          |
| scikit-learn    | Dimensionality reduction       |
| NumPy           | Numerical computations        |
| Pytest          | Testing framework             |
