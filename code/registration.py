import subprocess

import numpy as np
import open3d as o3d

from utils.transforms import txt_to_numpy, numpy_to_pointcloud

def compute_features(organ, params):
        # downsample
        organ.downsampled_pointcloud = organ.pointcloud.voxel_down_sample(params['voxel_size'])

        # estimate normals
        radius_normal = params['voxel_size'] * 2
        organ.downsampled_pointcloud.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, 
                                                                                           max_nn=params['max_nn']))

        # compute features
        radius_feature = params['voxel_size'] * 5
        organ.fpfh_features = o3d.pipelines.registration.compute_fpfh_feature(organ.downsampled_pointcloud, 
                                                                              o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, 
                                                                                                                   max_nn=params['max_nn']))

        return organ


def global_registration(source, target, params):
    distance_threshold = params['voxel_size'] * params['global_distance_threshold_factor']
    source, target = compute_features(source, params), compute_features(target, params)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(source.downsampled_pointcloud, 
                                                                                      target.downsampled_pointcloud, 
                                                                                      source.fpfh_features,
                                                                                      target.fpfh_features, 
                                                                                      True, 
                                                                                      distance_threshold,
                                                                                      o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 
                                                                                      3,
                                                                                      [o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(params['global_edge_length_threshold_factor']), 
                                                                                       o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)], 
                                                                                      o3d.pipelines.registration.RANSACConvergenceCriteria(params['global_max_iterations'], params['global_max_correspondence']))
    source.global_registration = result.transformation
    return source
                                                                                

def refine_registration(source, target, params):
    distance_threshold = params['voxel_size'] * params['refine_distance_threshold_factor']
    result = o3d.pipelines.registration.registration_icp(source.pointcloud, 
                                                         target.pointcloud, 
                                                         distance_threshold, 
                                                         source.global_registration, 
                                                         o3d.pipelines.registration.TransformationEstimationPointToPlane())
    source.refine_registration = result.transformation
    return source


def rigid_registration(source, target, params):
    # first we do a quick global registration using RANSAC
    source = global_registration(source, target, params)

    # then we refine the registration using ICP Point to Plane
    source = refine_registration(source, target, params)

    # apply and record the transform
    source.transformed_rigid = source.pointcloud.transform(source.refine_registration)

    return source


def nonrigid_registration(source, target, params):
    # save the source and target point clouds 
    np.savetxt(f"{source.file_name}.txt", np.array(source.transformed_rigid.points), delimiter=',')
    np.savetxt(f"{target.file_name}.txt", np.array(target.pointcloud.points), delimiter=',')

    # run BCPD
    result = subprocess.run(['./bcpd', 
                             '-x', f"../{target.file_name}.txt", 
                             '-y', f"../{source.file_name}.txt", 
                             '-J', '300', '-K', '70', '-p', '-c', str(params['distance_threshold']), '-r', str(params['seed']), '-n', str(params['max_iterations']), '-l', str(params['lambda']), '-b', str(params['beta']),
                             '-s', 'A'], 
                             cwd="../../bcpd",
                             capture_output=True)
    
    # record transformations
    source.dvf = txt_to_numpy('../../bcpd/output_v.txt')
    source.translation_nonrigid = txt_to_numpy('../../bcpd/output_t.txt')
    source.scale_nonrigid = txt_to_numpy('../../bcpd/output_s.txt')
    source.rotation_nonrigid = txt_to_numpy('../../bcpd/output_r.txt')
    
    # record transform
    source.transformed_nonrigid = numpy_to_pointcloud(txt_to_numpy('../../bcpd/output_y.txt'))

    return source