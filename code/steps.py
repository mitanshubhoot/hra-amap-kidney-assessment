import subprocess
import numpy as np
import open3d as o3d

from decorators import step
from dataclass import Transform
from utils.conversions import pointcloud_to_numpy, numpy_to_pointcloud, txt_to_numpy
from utils.preprocess import scale, mean, compute_features

@step(name='Normalize ICP', description='Scale organs to a common range about the centre')
def normalize_rigid(source, target):
    # scale
    source_scale, target_scale = scale(source, kind='unit'), scale(target, kind='unit')

    # create transform
    source_transform = Transform(scale=(1/source_scale), scale_center=source.get_center())
    target_transform = Transform(scale=(1/target_scale), scale_center=target.get_center())

    # apply
    source, target = source_transform(source), target_transform(target)

    # store outputs
    outputs = {'Source': source, 'Target': target}
    
    # store transforms
    transforms = {'Source': source_transform, 'Target': target_transform}
    
    return (outputs, transforms)

@step(name='Global Registration', description='Initial, fast registration before rigid registration')
def global_registration(source, target, params):
    distance_threshold = params['voxel_size'] * params['global_distance_threshold_factor']
    
    # downsample
    source = source.voxel_down_sample(params['voxel_size'])
    target = target.voxel_down_sample(params['voxel_size'])

    # compute features
    source_fpfh_features = compute_features(source, params)
    target_fpfh_features = compute_features(target, params)

    # register
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(source, 
                                                                                      target, 
                                                                                      source_fpfh_features,
                                                                                      target_fpfh_features, 
                                                                                      True, 
                                                                                      distance_threshold,
                                                                                      o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 
                                                                                      3,
                                                                                      [o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(params['global_edge_length_threshold_factor']), 
                                                                                       o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)], 
                                                                                      o3d.pipelines.registration.RANSACConvergenceCriteria(params['global_max_iterations'], params['global_max_correspondence']))
    

    # store transforms (no need to apply transform since this will be directly used to refine the registation)
    transforms = {'Source': Transform(matrix=result.transformation), 
                  'Target': None}    
    
    return (None, transforms)

@step(name='Rigid Registration', description='Registeration using only rigid transformations (scale, translation and rotation)')
def refine_registration(source, target, params, transform):
    distance_threshold = params['voxel_size'] * params['refine_distance_threshold_factor']

    # register
    result = o3d.pipelines.registration.registration_icp(source, 
                                                         target, 
                                                         distance_threshold, 
                                                         transform['Source'], 
                                                         o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    # create transform
    transform = Transform(matrix=result.transformation)
    
    # apply transform
    source = transform(source)
    
    # store outputs
    outputs = {'Source': source, 
              'Target': None}
    
    # store transforms
    transforms = {'Source': transform, 
                  'Target': None}
    
    return (outputs, transforms)

@step(name='Normalize BCPD', description='Normalize location and scale before nonrigid registration')
def normalize_nonrigid(source, target):
    # calculate scale
    source_scale, target_scale = scale(source, kind='stddev'), scale(target, kind='stddev')

    # calculate mean
    source_mean, target_mean = mean(source), mean(target)

    # create transform
    source_transform = Transform(scale=(1/source_scale), translate=-source_mean)
    target_transform = Transform(scale=(1/target_scale), translate=-target_mean)

    # apply
    source, target = source_transform(source), target_transform(target)

    # store outputs
    outputs = {'Source': source, 
              'Target': target}
    
    # store transforms
    transforms = {'Source': source_transform, 
                  'Target': target_transform}
    
    return (outputs, transforms)


@step(name='Non-rigid Registration', description='Registration using rigid and non-rigid (local deformations) with BCPD algorithm')
def nonrigid_registration(source, target, params):
    # convert to array
    source_array = pointcloud_to_numpy(source)
    target_array = pointcloud_to_numpy(target)

    # save the source and target point clouds as .txt
    np.savetxt(f"../../source.txt", source_array, delimiter=',')
    np.savetxt(f"../../target.txt", target_array, delimiter=',')

    # register using BCPD
    result = subprocess.run(['./bcpd', 
                             '-x', f"../source.txt", 
                             '-y', f"../target.txt", 
                             '-J', '300', '-K', '70', '-p', '-u', 'n', '-c', str(params['distance_threshold']), '-r', str(params['seed']), '-n', str(params['max_iterations']), '-l', str(params['lambda']), '-b', str(params['beta']),
                             '-s', 'A'], 
                             cwd="../../bcpd",
                             capture_output=True)
    
    # read transformations
    dvf = np.genfromtxt('../../bcpd/output_u.txt') - source_array
    translation = txt_to_numpy('../../bcpd/output_t.txt')
    scale = txt_to_numpy('../../bcpd/output_s.txt')
    rotation = txt_to_numpy('../../bcpd/output_r.txt')
    
    # create transform
    transform = Transform(scale=scale, rotate=rotation, translate=translation, deformation_vector_field=dvf)

    # apply transform
    source = transform(source)

    # store outputs
    outputs = {'Source': source, 
               'Target': None, 
               'Registered': numpy_to_pointcloud(txt_to_numpy('../../bcpd/output_y.txt'))}
    
    # store transforms
    transforms = {'Source': Transform(scale=scale, rotate=rotation, translate=translation, deformation_vector_field=dvf),
                  'Target': None}
    
    return (outputs, transforms)


@step(name='Denormalization BCPD', description='Denormalize the organ after projection')
def denormalize_nonrigid(source, target, transforms):
    # get scale
    source_scale, target_scale = transforms['Source'].scale, transforms['Target'].scale

    # calculate mean
    source_mean, target_mean = transforms['Source'].mean, transforms['Target'].mean

    # create transform
    source_transform = Transform(scale=source_scale, translate=source_mean)
    target_transform = Transform(scale=target_scale, translate=target_mean)

    # apply
    source, target = source_transform(source), target_transform(target)

    # store outputs
    outputs = {'Source': source, 
              'Target': target}
    
    # store transforms
    transforms = None
    
    return (outputs, transforms)

@step(name='Denormalization ICP', description='Denormalize the organ after projection')
def denormalize_rigid(source, target, transforms):
    # get scale
    source_scale, target_scale = transforms['Source'].scale, transforms['Target'].scale

    # get scale center
    source_center, target_center = transforms['Source'].scale_center, transforms['Target'].scale_center

    # create transform
    source_transform = Transform(scale=source_scale, scale_center=source_center)
    target_transform = Transform(scale=target_scale, scale_center=target_center)

    # apply
    source, target = source_transform(source), target_transform(target)

    # store outputs
    outputs = {'Source': source, 
              'Target': target}
    
    # store transforms
    transforms = None
    
    return (outputs, transforms)


