import trimesh
import numpy as np
import open3d as o3d

from typing import Union

def numpy_to_pointcloud(numpy_array: np.ndarray) -> o3d.geometry.PointCloud:
    """Converts a numpy array to an open3d compatible point cloud"""
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(numpy_array)
    return pcd

def load(path: str) -> Union[o3d.geometry.PointCloud, np.ndarray]:
    raise NotImplementedError