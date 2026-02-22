# Digitally Reverse Engineering a Gen 6 G19

![alt text](docs/curated_render_right_a.png)

> 3D model adversarially created using unlabeled 2d photos from glock.com.

https://www.printables.com/model/1610005-reverse-engineered-gen-6-g19

# Table of Contents

- [Introduction](#introduction)
- [Steps](#steps)
- [Tools](#tools)
- [Analysis](#analysis)
- [Results](#results)
  - [Meshroom](#meshroom)
  - [Voxel Carving](#voxel-carving)
    - [Binary voxel carving](#binary-voxel-carving)
    - [Voting approach](#voting-approach)
    - [Curated masks](#curated-masks)
- [Conclusion](#conclusion)
- [Future Work](#future-work)
- [Fails](#fails)
- [Unused photos](#unused-photos)

# Introduction

Glock.com simulates a 3d viewer by providing photos in a subset of angles and rotations. I had the thought, "Is it possible to use those photos to make a 3d model?" This paper explores applying voxel carving to create a 3d model in an adversarial setting without being provided knowledge of camera parameters. While there's room for improvement, the results are strong for a proof of concept.

# Steps

1. Generate the URL set
2. Download the photos
3. Generate the 3D model

# Tools

- [Firefox](https://firefox.com)
- [Meshroom](https://alicevision.org/)
- [Docker](https://www.docker.com/)

# Analysis

- First 24 photos are very close to the following 24 photos, so I just skip them.
- Angles of 15 degrees

```
Assuming focal length of 35mm and sensor size of 36mm x 24mm.
Given slide size reference of 174mm, 463px.
(174mm * 35mm * 1100px) / (463px * 36mm) = 401.9mm
Rounding down and assuming a camera-object distance of 400mm.
```

| tilt/rotation | 0 | 15 | 30 | 45 | 60 | 75 | 90 | 105 | 120 | 135 | 150 | 165 | 180 | 195 | 210 | 225 | 240 | 255 | 270 | 285 | 300 | 315 | 330 | 345 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6.5 | 024.png | 025.png | 026.png | 027.png | 028.png | 029.png | 030.png | 031.png | 032.png | 033.png | 034.png | 035.png | 036.png | 037.png | 038.png | 039.png | 040.png | 041.png | 042.png | 043.png | 044.png | 045.png | 046.png | 047.png |
| 25 | 048.png | 049.png | 050.png | 051.png | 052.png | 053.png | 054.png | 055.png | 056.png | 057.png | 058.png | 059.png | 060.png | 061.png | 062.png | 063.png | 064.png | 065.png | 066.png | 067.png | 068.png | 069.png | 070.png | 071.png |
| 40 | 072.png | 073.png | 074.png | 075.png | 076.png | 077.png | 078.png | 079.png | 080.png | 081.png | 082.png | 083.png | 084.png | 085.png | 086.png | 087.png | 088.png | 089.png | 090.png | 091.png | 092.png | 093.png | 094.png | 095.png |
| 60 | 096.png | 097.png | 098.png | 099.png | 100.png | 101.png | 102.png | 103.png | 104.png | 105.png | 106.png | 107.png | 108.png | 109.png | 110.png | 111.png | 112.png | 113.png | 114.png | 115.png | 116.png | 117.png | 118.png | 119.png |

# Results

## Meshroom

The initial low effort prototype using meshroom's "photogrametry + object turntable" pipeline.

![meshroom result](docs/meshroom_result.png)

## Voxel Carving

### Binary voxel carving

Captures the most detail but loses information from glares.

[STL](results/binary-reconstruction-400-res.stl)

![carve render left low a](docs/carve_render_left_low_a.png)

> Low detail A

![carve render left low b](docs/carve_render_left_low_b.png)

> Low detail B

![carve render left high](docs/carve_render_left_high.png)

> High detail

### Voting approach

Sacrifices detail for more complete shape.

[STL](results/voting-reconstruction-500-res.stl)

![voting render front](docs/voting_render_front.png)

> Voting front

![voting render right a](docs/voting_render_right_a.png)

> Voting right A

![voting render right b](docs/voting_render_right_b.png)

> Voting right B

### Curated masks

Try as I might, there's no replacement for good data. In this section, I manually output the masks, edited them to remove glares and other artifacts, and performed binary voxel carving. The results were significantly better than the other methods. Well enough that it's clear there's an ever so slight distoration that isn't being accounted for in the camera matrix. I also discovered some of the tilt angles were off during this section, so the previous results could be improved.

[STL](results/curated_reconstruction.stl)

![curated render left a](docs/curated_render_left_a.png)

> Curated left A

![curated render left b](docs/curated_render_left_b.png)

> Curated left B

![curated render right a](docs/curated_render_right_a.png)

> Curated right A

![curated render right b](docs/curated_render_right_b.png)

> Curated right B

# Conclusion

It was possible to create a 3d model using only the photos provided via glock.com.

I was really impressed with the results of the voxel carving approach. It was able to capture a lot of detail from the pistol. Binary carving is a very powerful technique, but it is very sensitive to the quality of the input images.

# Future Work

- Improving segmentation would massively improve the 3d model
- Dialing in the camera parameters would improve the 3d model
- Improve the voting algorithm for the carving approach
- Continue the direction of using AI produced depth maps

# Fails

![voxel fail a](docs/voxel_fail_a.png)

![voxel fail b](docs/voxel_fail_b.png)

![voxel fail c](docs/voxel_fail_c.png)

![voxel fail d](docs/voxel_fail_d.png)

![voxel fail e](docs/voxel_fail_e.png)

![mesh fail a](docs/mesh_fail_a.png)

![mesh fail b](docs/mesh_fail_b.png)

![mesh fail c](docs/mesh_fail_c.png)

> Biblically accurate glock

![mesh fail d](docs/mesh_fail_d.png)

![mesh fail e](docs/mesh_fail_e.png)

> Glonk

# Unused photos

![depth map 0000](docs/depth_map_0000.png)

![depth map](docs/depth_map.png)

![matches example](docs/matches_example.png)
