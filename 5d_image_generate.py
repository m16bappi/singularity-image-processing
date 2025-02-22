import numpy as np
import tifffile as tf

# Step 1: Create a small synthetic 5D image
X, Y, Z, T, C = 64, 64, 5, 3, 2  # Small dimensions
image_5d = np.random.randint(0, 256, size=(X, Y, Z, T, C), dtype=np.uint8)

# Step 2: Save the image as a TIFF file
tf.imwrite("small_5d_image.tiff", image_5d)

# Step 3: Load the TIFF file
image = tf.imread("small_5d_image.tiff")
print("Loaded shape:", image.shape)  # Should print (64, 64, 5, 3, 2)

# Step 4: Process the 5D image (e.g., extract a slice)
slice_2d = image[:, :, 2, 1, 0]  # Extract a 2D slice (X, Y) at Z=2, T=1, C=0
print("2D slice shape:", slice_2d.shape)
