#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize consecutive frames from two PKL files as an occupancy grid animation,
with automatic playback and saving as a GIF.
Supports loading existing camera parameters to maintain consistent viewpoint and window size.

Usage:
  python viz_occupancy_gif.py --type semantic --pkl1 first.npy --pkl2 second.npy --gif output.gif --camfile camera.json
"""
import argparse
import os
import pickle
import numpy as np
import torch
import open3d as o3d
import imageio

# Voxel & world parameters
VOXEL_SIZE = [0.4, 0.4, 0.4]
POINT_RANGE = [-40.0, -40.0, -1.0, 40.0, 40.0, 5.4]

# Semantic colors
colors_map = np.array([
    [222, 184, 135, 255], [0, 175, 0, 255], [47, 79, 79, 255],
    [220, 20, 60, 255], [255, 158, 0, 255], [255, 140, 0, 255],
    [233, 150, 70, 255], [0, 0, 230, 255], [255, 50, 0, 255],
    [222, 184, 135, 255], [0, 0, 230, 255], [170, 30, 80, 255],
    [255, 10, 99, 255], [0, 200, 200, 255], [75, 0, 75, 255],
])
SEM_COLORS = colors_map[:, :3] / 255.0
DENSE_COLOR = [0.624, 0.796, 0.565]

# Cube template
_HX, _HY, _HZ = [v / 2 for v in VOXEL_SIZE]
CORNERS = np.array([
    [-_HX, -_HY, -_HZ], [_HX, -_HY, -_HZ], [_HX, _HY, -_HZ], [-_HX, _HY, -_HZ],
    [-_HX, -_HY,  _HZ], [_HX, -_HY,  _HZ], [_HX, _HY,  _HZ], [-_HX, _HY,  _HZ]
], dtype=np.float32)
FACES = np.array([
    [0,1,2],[2,3,0], [4,5,6],[6,7,4],
    [0,1,5],[5,4,0], [2,3,7],[7,6,2],
    [1,2,6],[6,5,1], [0,3,7],[7,4,0]
], dtype=np.int32)

def load_frames(path):
    ext = os.path.splitext(path)[1]
    if ext == '.npy':
        data = np.load(path)
        if data.ndim == 5:
            data = data[0]
        if data.ndim == 4:
            return [data[i] for i in range(data.shape[0])]
        if data.ndim == 3:
            return [data]
    else:
        with open(path, 'rb') as f:
            return pickle.load(f)
    raise ValueError(f"Unsupported data shape: {data.shape}")

def grid_to_mesh(grid, uniform=False):
    mask = (grid != 0) if uniform else ((grid != 17) & (grid != 255))
    idx = torch.nonzero(torch.from_numpy(mask), as_tuple=True)
    verts, faces, colors = [], [], []
    off = 0
    for x, y, z in zip(*idx):
        x, y, z = x.item(), y.item(), z.item()
        cx = x * VOXEL_SIZE[0] + VOXEL_SIZE[0]/2 + POINT_RANGE[0]
        cy = y * VOXEL_SIZE[1] + VOXEL_SIZE[1]/2 + POINT_RANGE[1]
        cz = z * VOXEL_SIZE[2] + VOXEL_SIZE[2]/2 + POINT_RANGE[2]
        verts.append(CORNERS + [cx, cy, cz])
        faces.append(FACES + off)
        color = DENSE_COLOR if uniform else SEM_COLORS[int(grid[x, y, z]) % len(SEM_COLORS)]
        colors.append(np.tile(color, (8, 1)))
        off += 8
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(np.vstack(verts))
    mesh.triangles = o3d.utility.Vector3iVector(np.vstack(faces))
    mesh.vertex_colors = o3d.utility.Vector3dVector(np.vstack(colors))
    mesh.compute_vertex_normals()
    return mesh

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['semantic', 'dense'], required=True)
    parser.add_argument('--pkl1', required=True)
    parser.add_argument('--pkl2', required=True)
    parser.add_argument('--gif', required=True)
    parser.add_argument('--camfile', default='camera.json')
    args = parser.parse_args()

    # Load frames
    frames = load_frames(args.pkl1)[0:6] + load_frames(args.pkl2)
    print(len(frames))
    meshes = [grid_to_mesh(f, uniform=(args.type == 'dense')) for f in frames]

    # Try loading camera params for window sizing
    cam = None
    if os.path.isfile(args.camfile):
        cam = o3d.io.read_pinhole_camera_parameters(args.camfile)
        print(f"🔄 Loaded camera from {args.camfile}")
        width = cam.intrinsic.width
        height = cam.intrinsic.height
    else:
        width, height = 1024, 768

    # Create offscreen window
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False, width=width, height=height)

    images = []
    for mesh in meshes:
        vis.clear_geometries()
        vis.add_geometry(mesh)
        if cam:
            vis.get_view_control().convert_from_pinhole_camera_parameters(cam)
        vis.poll_events()
        vis.update_renderer()
        buf = np.asarray(vis.capture_screen_float_buffer(False))
        images.append((buf * 255).astype(np.uint8))

    # Save GIF
    os.makedirs(os.path.dirname(args.gif), exist_ok=True)
    imageio.mimsave(args.gif, images, duration=0.5)
    vis.destroy_window()
    print(f"✅ GIF saved as {args.gif}")

if __name__ == '__main__':
    main()
