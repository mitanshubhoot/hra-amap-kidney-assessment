import json
import yaml
import trimesh
import open3d as o3d

from pathlib import Path
from datetime import datetime

from utils.transforms import pointcloud_to_mesh, ply_to_mesh, nii_to_mesh, vtk_to_mesh

def load(file_name: str, file_type: str) -> trimesh.Trimesh:
    """Loads a mesh from a local path"""
    if file_type in ['.glb', '.stl', '.obj']:
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

def make_export_dirs(export_dir: str):
     # create a timestamp string using the current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # create the parent directory with the timestamp
    parent_dir = Path(f'{export_dir}-{timestamp}')
    parent_dir.mkdir()
    
    # create the subdirectories inside the parent directory
    sub_dirs = ['mesh', 'projections', 'correspondence']
    for sub_dir in sub_dirs:
        sub_dir_path = parent_dir / sub_dir
        Path(sub_dir_path).mkdir(parents=True, exist_ok=True)

    return parent_dir

def read_json(path: str) -> dict:
    """Reads a JSON file, returns a Python Dict object"""
    with open(path) as f:
        file = json.load(f)
    return file

def read_yaml(path: str) -> dict:
    """Reads a YAML file, returns a Python Dict object"""
    with open(path, "r") as f:
        file = yaml.safe_load(f)
    return file
