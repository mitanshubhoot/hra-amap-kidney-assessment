import trimesh
import numpy as np
import open3d as o3d

from pathlib import Path

from utils.transforms import pointcloud_to_mesh, ply_to_mesh, nii_to_mesh, vtk_to_mesh

def load(file_name: str, file_type: str) -> trimesh.Trimesh:
    """Loads a mesh from a local path"""
    if file_type in ['.glb', '.fbx', '.stl', '.obj']:
        mesh = trimesh.load(file_name, file_type, force='mesh')
    elif file_type == '.pcd':
        mesh = pointcloud_to_mesh(o3d.io.read_point_cloud(f"{file_name}{file_type}"))
    elif file_type == '.ply':
        mesh = ply_to_mesh(o3d.io.read_triangle_mesh(f"{file_name}{file_type}"))
    elif file_type in ['.nii', '.nii.gz']:
        mesh = nii_to_mesh(f"{file_name}{file_type}")
    elif file_type == '.vtk':
        mesh = vtk_to_mesh(f"{file_name}{file_type}")

    return (mesh.faces, mesh.vertices)