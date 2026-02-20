from transformers import AutoImageProcessor, GLPNForDepthEstimation
from PIL import Image
import os
import cv2
import torch
import matplotlib.pyplot as plt

PHOTOS_DIRECTORY = "/photos/source"

paths = os.listdir(PHOTOS_DIRECTORY)
files = [file for file in paths if file.endswith(".png")]
images = [cv2.imread(os.path.join(PHOTOS_DIRECTORY, file)) for file in files]

image_processor = AutoImageProcessor.from_pretrained("vinvino02/glpn-kitti")
model = GLPNForDepthEstimation.from_pretrained("vinvino02/glpn-kitti")

for index, image in enumerate(images):

    # prepare image
    mask = (image == [255, 255, 255])
    image[mask] = 0

    # prepare image for the model
    inputs = image_processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    # interpolate to original size
    post_processed_output = image_processor.post_process_depth_estimation(
        outputs,
        target_sizes=[(image.shape[0], image.shape[1])],
    )

    # Create a mask where image pixel is 255 (background)
    mask = (image != [255, 255, 255])
    mask = mask[:, :, 0]

    # visualize the prediction
    predicted_depth = post_processed_output[0]["predicted_depth"]
    depth = predicted_depth * 255 / predicted_depth.max()
    depth = depth.detach().cpu().numpy()
    # depth = depth[mask]
    # depth = depth.reshape(image.shape[0], image.shape[1])
    depth = Image.fromarray(depth.astype("uint8"))

    # Save the depth map
    plt.imsave(f"/photos/depth/{index:03d}.png", depth, cmap="magma")
