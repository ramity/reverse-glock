FROM nvidia/cuda:13.1.1-devel-ubuntu24.04

WORKDIR /app

RUN apt update
RUN apt upgrade -y

# Install pip (Python3 is included in ubuntu without pip)
RUN apt install -y python3-pip

# Helper tool for querying installed libraries.
RUN apt install -y pkg-config

# Install python libraries
RUN pip install numpy --break-system-packages
RUN pip install pillow --break-system-packages
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130 --break-system-packages
RUN pip install tqdm --break-system-packages
RUN pip install scikit-image --break-system-packages
RUN pip install numpy-stl --break-system-packages

# OpenCV dependencies
RUN apt install -y cmake g++ wget zip unzip
RUN apt install -y ffmpeg libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libx264-dev

# Download OpenCV code
RUN mkdir /root/opencv
RUN wget -O /root/opencv/opencv.zip https://github.com/opencv/opencv/archive/4.x.zip
RUN wget -O /root/opencv/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.x.zip
RUN unzip /root/opencv/opencv.zip -d /root/opencv/
RUN unzip /root/opencv/opencv_contrib.zip -d /root/opencv/
RUN mkdir /root/opencv/build

# Configure OpenCV
RUN cd /root/opencv/build && cmake -DWITH_FFMPEG=1 -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.x/modules ../opencv-4.x

# Build and install OpenCV
RUN cd /root/opencv/build && make -j$(nproc)
RUN cd /root/opencv/build && make install

RUN pip install open3d --break-system-packages
RUN pip install matplotlib --break-system-packages

ENTRYPOINT sleep infinity
