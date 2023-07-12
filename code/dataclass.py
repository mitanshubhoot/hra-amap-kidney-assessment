import pickle
import trimesh
import numpy as np
import open3d as o3d

from typing import Any, Optional
from dataclasses import dataclass
from utils.conversions import pointcloud_to_numpy, numpy_to_pointcloud
from organ import Organ

@dataclass
class Transform: 
    scale: list = None
    rotate: list = None
    translate: list = None
    deformation_vector_field: Optional[np.ndarray] = np.zeros(shape=(3, 1))
    matrix: np.ndarray = None
    scale_center: Optional[float] = False
    rotate_center: bool = False
    translate_relative: bool = True

    def apply_scaling(self, geometry):
        if isinstance(geometry, o3d.geometry.PointCloud):
            return geometry.scale(self.scale, center=self.scale_center)
        else: 
            return geometry.apply_scale(self.scale)    
        
    def apply_translation(self, geometry):
        if isinstance(geometry, o3d.geometry.PointCloud):
            return geometry.translate(self.translate, relative=self.translate_relative)
        else: 
            return geometry.apply_translation(self.translate)  

    def apply_rotation(self, geometry):
        if isinstance(geometry, o3d.geometry.PointCloud):
            return geometry.rotate(self.rotate, center=self.rotate_center)
        else: 
            return geometry.apply_rotation(self.rotate) 
        
    def apply_matrix(self, geometry):
        if isinstance(geometry, o3d.geometry.PointCloud):
            return geometry.transform(self.matrix)
        else: 
            return geometry.apply_transform(self.matrix) 

    def __call__(self, geometry):
        if self.deformation_vector_field:
            assert isinstance(geometry, o3d.geometry.PointCloud), "DVF transformations only supported on pointclouds"
            geometry = pointcloud_to_numpy(geometry)
            geometry = ((self.scale * self.rotate) @ ((geometry + self.deformation_vector_field) + self.translate).T).T
            return numpy_to_pointcloud(geometry)
        
        # if a 4x4 matrix is provided, individual transformations will be overriden
        if self.matrix:
            return self.apply_matrix(geometry)

        else:
            if self.scale:
                geometry = self.apply_scaling(geometry)
            if self.rotate:
                geometry = self.apply_rotation(geometry)
            if self.translate:
                geometry = self.apply_translation(geometry)
        return geometry
    
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
    registeration: trimesh.base.Trimesh

    @classmethod
    def load(cls, path: str):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError

# @dataclass
# class PipelineOutput:
#     id: str
#     description: str
#     steps: dict[PipelineStep] = {}

