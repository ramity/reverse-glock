import cv2
import numpy as np
import math
from stl import mesh
from skimage import measure
import glob
import os

def get_camera_matrix(azimuth_deg, tilt_deg, distance, K):
    """Calculates Projection Matrix P = K [R | t]"""
    # Convert to radians; azimuth is CCW (to the left)
    theta = math.radians(azimuth_deg) 
    phi = math.radians(tilt_deg)

    # 1. Camera Position in Cartesian (Y+ is forward/0 deg)
    cx = distance * math.cos(phi) * math.sin(theta)
    cy = distance * math.cos(phi) * math.cos(theta)
    cz = distance * math.sin(phi)
    camera_pos = np.array([cx, cy, cz], dtype=float)

    # 2. Look-At Rotation (Camera faces origin)
    forward = -camera_pos / np.linalg.norm(camera_pos)
    tmp_up = np.array([0, 0, 1.0]) # Z is up
    right = np.cross(tmp_up, forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)

    R = np.vstack([right, up, -forward]) 
    t = -R @ camera_pos
    return K @ np.column_stack((R, t))

def carve_and_save_stl(image_paths, azimuths, tilts, K, distance, res=400, scale=200):

    total_views = len(azimuths) * len(tilts)

    # 1️⃣ Initialize Vote Grid (integer counts instead of bool)
    voxel_counts = np.zeros((res, res, res), dtype=np.uint16)

    # Create coordinate grid
    grid_range = np.linspace(-scale/2, scale/2, res)
    X, Y, Z = np.meshgrid(grid_range, grid_range, grid_range, indexing='ij')

    world_pts = np.vstack([
        X.ravel(),
        Y.ravel(),
        Z.ravel(),
        np.ones(X.size)
    ])

    print("Starting Vote Accumulation...")
    idx = 0

    for tilt in tilts:
        for azim in azimuths:

            if idx >= len(image_paths):
                break

            mask = cv2.imread(image_paths[idx], cv2.IMREAD_GRAYSCALE)
            if mask is None:
                idx += 1
                continue

            mask[mask == 255] = 0
            mask[mask != 0] = 255

            P = get_camera_matrix(azim, tilt, distance, K)
            h, w = mask.shape

            # Project voxels to 2D
            img_pts = P @ world_pts
            u = (img_pts[0] / img_pts[2]).astype(int)
            v = (img_pts[1] / img_pts[2]).astype(int)

            # Check bounds and mask hit
            # We only care about voxels currently marked as True
            valid_mask = (u >= 0) & (u < w) & (v >= 0) & (v < h)

            # Carve: If out of bounds or mask is black, set to False
            # This bitwise logic is fast on large arrays
            current_occupancy = np.zeros(X.size, dtype=bool)
            current_occupancy[valid_mask] = mask[v[valid_mask], u[valid_mask]]
            voxel_counts += current_occupancy.reshape(res, res, res).astype(np.uint16)

            idx += 1

    print("Filtering voxels by vote threshold...")

    # 2️⃣ Threshold votes
    vote_threshold = int(total_views * 1)
    voxels = voxel_counts >= vote_threshold

    print("Extracting surface via Marching Cubes...")

    # 3️⃣ Run Marching Cubes
    verts, faces, normals, values = measure.marching_cubes(
        voxels.astype(float), level=0.5
    )

    # Rescale vertices
    verts = (verts / res) * scale - (scale / 2)

    # 4️⃣ Create STL
    obj = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            obj.vectors[i][j] = verts[f[j], :]

    obj.save('reconstruction.stl')
    print("Saved to reconstruction.stl")

# --- Configuration ---
img_w, img_h = 1100, 733
f = 35 # Focal length
sensor_w = 36
sensor_h = 24
K_mat = np.array([[f * img_w / sensor_w, 0, img_w/2], [0, f * img_h / sensor_h, img_h/2], [0, 0, 1]], dtype=float)

# Example setup: 360 degrees in 15 deg steps (24 photos) 
# and 4 tilt levels (0, 15, 30, 45)
azim_list = range(0, 360, 15)
tilt_list = [0, 20, 40, 60]

# Generate dummy paths (Replace with your actual file list)
photo_dir = "/photos/source/"
file_paths = glob.glob(os.path.join(photo_dir, "*.png"))
file_paths = file_paths[24:]

carve_and_save_stl(file_paths, azim_list, tilt_list, K_mat, distance=400)
