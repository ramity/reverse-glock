import cv2
import numpy as np
import open3d as o3d
import os

focal_length = 35
image_width = 1100
image_height = 733
sensor_width = 36
sensor_height = 24

PHOTO_ROWS = 4
PHOTO_COLS = 24
ROTATIONS = range(0, 360, 15)
TILTS = range(0, 60, 15)
PHOTO_DIRECTORY = "/photos/source"

# Initiate SIFT detector and BFMatcher.
sift = cv2.SIFT_create()
bf = cv2.BFMatcher()

# Load and preprocess the photos.
files = os.listdir(PHOTO_DIRECTORY)
files = [image for image in files if image.endswith(".png")]
files = files[24:]
images = [cv2.imread(os.path.join(PHOTO_DIRECTORY, file)) for file in files]
grayscales = [cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) for image in images]

# Create arrays of keypoint and descriptors.
keypoints = []
descriptors = []
for col in range(PHOTO_COLS):
    for row in range(PHOTO_ROWS):
        index = (PHOTO_COLS * row) + col
        kp, des = sift.detectAndCompute(grayscales[index], None)
        keypoints.append(kp)
        descriptors.append(des)

# Consider horizontal matches.
horizontal_matches = []
for row in range(PHOTO_ROWS):
    for col in range(PHOTO_COLS - 1):
        index = (PHOTO_COLS * row) + col
        matches = bf.knnMatch(descriptors[index], descriptors[index + 1], k=2)
        for m, n in matches:
            if m.distance < 0.6 * n.distance:
                horizontal_matches.append([m])

# Consider vertical matches.
vertical_matches = []
for col in range(PHOTO_COLS):
    for row in range(PHOTO_ROWS - 1):
        index = (PHOTO_COLS * row) + col
        matches = bf.knnMatch(descriptors[index], descriptors[index + PHOTO_COLS], k=2)
        for m, n in matches:
            if m.distance < 0.6 * n.distance:
                vertical_matches.append([m])

print(f"Horizontal matches: {len(horizontal_matches)}")
print(f"Vertical matches: {len(vertical_matches)}")

# Draw matches.
# img3 = cv2.drawMatchesKnn(grayscales[2], kp1, grayscales[3], kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
# cv2.imwrite(f"matches_0000.png", img3)

test = images[4]
test[test == [255, 255, 255]] = 0
cv2.imwrite(f"test.png", test)

# Draw a crosshair over the center of the image.
# cv2.line(grayscales[0], (grayscales[0].shape[1]//2, 0), (grayscales[0].shape[1]//2, grayscales[0].shape[0]), (255, 0, 0), 1)
# cv2.line(grayscales[0], (0, grayscales[0].shape[0]//2), (grayscales[0].shape[1], grayscales[0].shape[0]//2), (255, 0, 0), 1)
# cv2.imwrite(f"crosshair_0000.png", grayscales[0])

def get_projection_matrix(K, rotation_deg, tilt_deg, distance=400):
    # Convert degrees to radians
    theta = np.radians(rotation_deg)
    phi = np.radians(tilt_deg)
    
    # Calculate Camera Position (Cartesian)
    # Assuming Z is up, X-Y is the turntable plane
    cx = distance * np.cos(phi) * np.sin(theta)
    cy = distance * np.cos(phi) * np.cos(theta)
    cz = distance * np.sin(phi)
    
    camera_pos = np.array([cx, cy, cz])
    target = np.array([0, 0, 0])
    up = np.array([0, 0, 1])
    
    # Create Look-At Matrix (Extrinsics)
    z_axis = (camera_pos - target) / np.linalg.norm(camera_pos - target)
    x_axis = np.cross(up, z_axis)
    x_axis /= np.linalg.norm(x_axis)
    y_axis = np.cross(z_axis, x_axis)
    
    R = np.vstack([x_axis, y_axis, z_axis]) # Rotation
    t = -R @ camera_pos # Translation
    
    # Extrinsic matrix [R|t]
    Rt = np.column_stack((R, t))
    return K @ Rt

# --- Setup ---
# Replace with your actual K matrix from calibration
K =  np.array([[focal_length * image_width / sensor_width, 0, image_width / 2], [0, focal_length * image_height / sensor_height, image_height / 2], [0, 0, 1]], dtype=np.float32)

all_points_3d = []
sift = cv2.SIFT_create()
bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

# --- Processing Loop (Simplified for two adjacent images) ---
# In a real scenario, you would loop through all 120 images and match pairs
def process_pair(index, ang1, tilt1, ang2, tilt2, matches):
    pts1 = matches[:, 0, :].T
    pts2 = matches[:, 1, :].T

    # Get Projection Matrices
    P1 = get_projection_matrix(K, ang1, tilt1)
    P2 = get_projection_matrix(K, ang2, tilt2)

    # Triangulate
    points_4d = cv2.triangulatePoints(P1, P2, pts1, pts2)
    points_3d = points_4d[:3] / points_4d[3]
    return points_3d.T

print(horizontal_matches[0][0])

test = process_pair(0, 0, 0, 15, 0, horizontal_matches[0])
print(test)

def create_stl(point_array, output_file="model.stl"):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_array)
    
    # Clean noise
    pcd, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    
    # Estimate Normals & Mesh
    pcd.estimate_normals()
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)
    
    o3d.io.write_triangle_mesh(output_file, mesh)
    print(f"Saved {output_file}")
