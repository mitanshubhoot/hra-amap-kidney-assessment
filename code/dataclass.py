import pickle
import trimesh
import numpy as np
import open3d as o3d

from typing import Any, Optional
from dataclasses import dataclass
from utils.preprocess import mean
from utils.conversions import to_array, to_pointcloud, to_mesh
from organ import Organ

from scipy.spatial.transform import Rotation  


@dataclass
class Transform: 
    scale: float = 1.0
    rotate: Optional[np.ndarray | tuple] = (0, 0, 0)
    translate: tuple = (0, 0, 0)
    deformation_vector_field: Optional[np.ndarray] = None
    matrix: np.ndarray = None
    rotate_axes: str = 'xyz'

    def __post_init__(self):
        if isinstance(self.matrix, np.ndarray):
            pass
        else:
            # check if rotation is a matrix or tuple of angles
            if isinstance(self.rotate, tuple):
                # find rotation matrix from angles if tuple
                rotation_matrix = Rotation.from_euler(seq=self.rotate_axes, angles=self.rotate, degrees=True).as_matrix()
            else: 
                rotation_matrix = self.rotate     
            # construct a 4x4 transformation matrix
            self.matrix = np.empty((4, 4))
            self.matrix[:3, :3] = rotation_matrix * self.scale
            self.matrix[:3, 3] = self.translate
            self.matrix[3, :] = [0, 0, 0, 1]

    def transform(self, geometry, invert=False):
        if isinstance(geometry, o3d.geometry.PointCloud):
            return geometry.transform(self.matrix if not invert else self.inverse)
        else: 
            return geometry.apply_transform(self.matrix if not invert else self.inverse)
        
    def invert(self, geometry):
        if isinstance(self.deformation_vector_field, np.ndarray):
            raise ValueError("Inversion not supported on DVF transformations")
        self.inverse = np.linalg.inv(self.matrix)
        geometry = self.transform(geometry, invert=True)
        if self.centered:
            array = to_array(geometry) + self.mean
            geometry = to_pointcloud(array) if isinstance(geometry, o3d.geometry.PointCloud) else to_mesh(array, geometry.faces)
        return geometry
    
    def center(self, geometry):
        self.mean = mean(geometry)
        array = to_array(geometry) - self.mean
        geometry = to_pointcloud(array) if isinstance(geometry, o3d.geometry.PointCloud) else to_mesh(array, geometry.faces)
        self.centered = True
        return geometry

    def __call__(self, geometry, center=False):
        if center:
            geometry = self.center(geometry)
        if isinstance(self.deformation_vector_field, np.ndarray):
            assert isinstance(geometry, o3d.geometry.PointCloud), "DVF transformations only supported on pointclouds"
            geometry = to_array(geometry)
            geometry = ((self.scale * self.rotate) @ ((geometry + self.deformation_vector_field) + self.translate).T).T
            return to_pointcloud(geometry)
        else:
            return self.transform(geometry)
        
@dataclass
class PipelineStep:
    name: str
    description: Optional[str] = None
    input: o3d.geometry.PointCloud = None
    output: o3d.geometry.PointCloud = None
    transform: Optional[dict[Transform]] = None
    logs: Optional[str] = None

@dataclass
class Projection:
    id: str
    description: str
    source: Organ
    target: Organ
    transformations: list[dict[Transform]]
    registration: trimesh.base.Trimesh

    @classmethod
    def load(cls, path: str):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError
