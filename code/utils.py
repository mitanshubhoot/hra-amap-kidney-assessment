import trimesh
import numpy as np
import open3d as o3d

from typing import Union


def mesh_to_pointcloud(mesh: trimesh.base.Trimesh) -> o3d.geometry.PointCloud:
    """Converts a trimesh mesh object to an open3d compatible point cloud"""
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(mesh.vertices))
    pcd.estimate_normals()
    return pcd

def numpy_to_pointcloud(numpy_array: np.ndarray) -> o3d.geometry.PointCloud:
    """Converts a numpy array to an open3d compatible point cloud"""
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(numpy_array)
    pcd.estimate_normals()
    return pcd

def pointcloud_to_mesh(pointcloud: o3d.geometry.PointCloud, faces: np.ndarray) -> o3d.geometry.PointCloud:
    """Converts a open3d point cloud object to trimesh mesh object"""
    return trimesh.Trimesh(vertices=pointcloud.points, faces=faces)

def load(file_path: str) -> Union[o3d.geometry.PointCloud, trimesh.base.Trimesh]:
    """Loads a 3D asset from a local path"""
    raise NotImplementedError

