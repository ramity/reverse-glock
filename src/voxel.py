import cv2
import numpy as np
from skimage import measure
from stl import mesh
import os

PHOTOS_DIRECTORY = "/photos/source"

def masks_to_stl(image_paths, output_filename="model.stl", threshold=127):
    """
    Converts a list of image mask paths into a 3D STL mesh.
    """
    # 1. Load images and stack into a 3D volume
    volume = []
    for path in image_paths:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        # Ensure binary mask
        # img[img == 255] = 0
        _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        # img[img != 0] = 1
        volume.append(binary)

    # Convert list to 3D numpy array (Z, Y, X)
    voxel_grid = np.array(volume)

    # 2. Apply Marching Cubes algorithm
    # level=127 finds the surface halfway between 0 and 255
    verts, faces, normals, values = measure.marching_cubes(voxel_grid, level=25)

    # 3. Create the mesh object
    obj_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            obj_mesh.vectors[i][j] = verts[f[j],:]

    # 4. Save to STL
    obj_mesh.save(output_filename)
    print(f"Mesh successfully saved to {output_filename}")

# Example Usage:
# image_files = [f"mask_{i}.png" for i in range(100)]
# masks_to_stl(image_files)

paths = os.listdir(PHOTOS_DIRECTORY)
paths = [file for file in paths if file.endswith(".png")]
paths = [os.path.join(PHOTOS_DIRECTORY, file) for file in paths]

masks_to_stl(paths)
