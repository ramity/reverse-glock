import numpy as np
import cv2
import os
import glob
import matplotlib.pyplot as plt
import math

# ===============================
# Configuration
# ===============================

IMG_DIR = "/photos/source/"
VOXEL_RES = 128
FOCAL_LENGTH_MM = 35
SENSOR_WIDTH_MM = 36
SENSOR_HEIGHT_MM = 24          # Full-frame sensor height
DIST_TO_OBJ = 400              # Camera distance
IMG_W, IMG_H = 1100, 733

K = np.array([[FOCAL_LENGTH_MM * IMG_W / SENSOR_WIDTH_MM, 0, IMG_W / 2], [0, FOCAL_LENGTH_MM * IMG_H / SENSOR_HEIGHT_MM, IMG_H / 2], [0, 0, 1]], dtype=np.float32)

# Camera poses (azimuth, tilt)
CAMERA_POSES = []
for az in range(0, 360, 15):
    for tilt in range(0, 60, 15):
        CAMERA_POSES.append((az, tilt))

# ===============================
# Camera Projection
# ===============================

def get_projection_matrix(azimuth_deg, tilt_deg):
    """
    Calculates the Projection Matrix P = K [R | t]
    """
    # Convert degrees to radians
    # Adjusting for "Second photo is to the left" (Counter-clockwise rotation)
    theta = math.radians(azimuth_deg) 
    phi = math.radians(tilt_deg)

    # 1. Calculate Camera Position (C) in Cartesian coordinates
    # Starting at Y+ (0, dist, 0)
    cx = -DIST_TO_OBJ * math.cos(phi) * math.sin(theta)
    cy = -DIST_TO_OBJ * math.cos(phi) * math.cos(theta)
    cz = -DIST_TO_OBJ * math.sin(phi)
    camera_pos = np.array([cx, cy, cz], dtype=float)

    # 2. Define Look-At Rotation
    # Forward vector (pointing at origin)
    forward = -camera_pos / np.linalg.norm(camera_pos)
    # Up vector (Z-axis is up)
    tmp_up = np.array([0, 0, 1.0])
    right = np.cross(tmp_up, forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)

    # Rotation matrix R (World to Camera)
    R = np.vstack([right, up, -forward]) 
    
    # 3. Translation vector t = -R * C
    t = -R @ camera_pos
    
    # 4. Final Projection Matrix
    Rt = np.column_stack((R, t))
    P = K @ Rt
    return P


# ===============================
# Space Carving
# ===============================

def space_carving():

    # Initialize voxel grid (1 = solid)
    voxels = np.ones((VOXEL_RES, VOXEL_RES, VOXEL_RES), dtype=bool)

    # Create voxel coordinates
    limit = 100
    x = np.linspace(-limit, limit, VOXEL_RES)
    y = np.linspace(-limit, limit, VOXEL_RES)
    z = np.linspace(-limit, limit, VOXEL_RES)

    xv, yv, zv = np.meshgrid(x, y, z, indexing='ij')

    points = np.vstack([
        xv.ravel(),
        yv.ravel(),
        zv.ravel(),
        np.ones_like(xv.ravel())
    ])

    img_files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
    img_files = img_files[24:]

    for i, img_path in enumerate(img_files):

        if i >= len(CAMERA_POSES):
            break

        print(f"Processing view {i+1}/{len(img_files)}")

        mask = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            continue

        mask[mask == 255] = 0
        mask[mask != 0] = 255

        # Find the biggest contour and fill it.
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)

        cv2.imwrite("mask.png", mask)

        # White (255) = object
        # mask = mask > 127

        P = get_projection_matrix(*CAMERA_POSES[i])

        # Project
        proj = P @ points

        depth = proj[2]
        valid = depth > 0

        proj[:2] /= depth

        u = proj[0].astype(int)
        v = proj[1].astype(int)

        valid &= (
            (u >= 0) & (u < IMG_W) &
            (v >= 0) & (v < IMG_H)
        )

        carve = np.zeros_like(valid)

        carve[valid] = mask[v[valid], u[valid]]

        voxels.ravel()[:] &= carve

        print("Remaining voxels:", np.sum(voxels))

        if np.sum(voxels) == 0:
            print("All voxels carved away.")
            break

        if i >= 23:
            return voxels

    return voxels


# ===============================
# Run
# ===============================

if __name__ == "__main__":

    voxels = space_carving()

    print("Final voxel count:", np.sum(voxels))

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.voxels(voxels, facecolors='teal', edgecolor='k', alpha=1)

    ax.set_aspect('equal')

    ax.set_title("3D Voxel Reconstruction")
    ax.view_init(elev=15, azim=45)

    plt.savefig("voxel.png")
