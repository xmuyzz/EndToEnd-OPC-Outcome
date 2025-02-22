import sys
import os
import pydicom
import glob
import SimpleITK as sitk
import pandas as pd
import numpy as np
from interpolate import interpolate
from crop_image import crop_top, crop_top_image_only, crop_full_body
from registration import nrrd_reg_rigid
import SimpleITK as sitk
import shutil



def interpolation():
    """
    interpolation
    """
    print('\n --- start interpolation ---')

    proj_dir = '/mnt/kannlab_rfa/Zezhong/HeadNeck/data/BWH_TOT'
    raw_img_dir = proj_dir + '/raw_img'
    respace_img_dir = proj_dir + '/respace_img'
    if not os.path.exists(respace_img_dir):
        os.makedirs(respace_img_dir)

    # df = pd.read_csv(proj_dir + '/bwh_clinical.csv')
    # IDs = df['patient_id'].astype(int).to_list()

    # print(IDs)
    # print(len(IDs))

    img_dirs = [i for i in sorted(glob.glob(raw_img_dir + '/*nrrd'))]
    img_ids = []
    count = 0
    for img_dir in img_dirs:
        img_id = img_dir.split('/')[-1].split('.')[0]
        #print(img_id)
        #if int(img_id) in IDs:
        count += 1
        print(count, img_id)
        img_interp = interpolate(
            patient_id=img_id, 
            path_to_nrrd=img_dir, 
            interpolation_type='linear', #"linear" for image
            new_spacing=(1, 1, 3), 
            return_type='sitk_obj', 
            output_dir=respace_img_dir,
            save_img_format='nii.gz')


def reg_crop(crop_shape):

    respace_img_dir = '/mnt/kannlab_rfa/Zezhong/HeadNeck/data/BWH_TOT/respace_img'
    crop_img_dir = '/mnt/kannlab_rfa/Zezhong/HeadNeck/data/BWH_TOT/crop_img'
    if not os.path.exists(crop_img_dir):
        os.makedirs(crop_img_dir)

    img_dirs = [i for i in sorted(glob.glob(respace_img_dir + '/*nii.gz'))]
    img_ids = []
    bad_ids = []
    count = 0
    for img_dir in img_dirs:
        img_id = img_dir.split('/')[-1].split('.')[0]
        count += 1
        print(count, img_id)
        img = sitk.ReadImage(img_dir, sitk.sitkFloat32)
        # --- crop full body scan ---
        z_img = img.GetSize()[2]
        if z_img > 200:
            img = crop_full_body(img, int(z_img * 0.65))
        # --- registration for image and seg ---    
        fixed_img_dir = os.path.join(respace_img_dir, '10020741814.nii.gz')
        fixed_img = sitk.ReadImage(fixed_img_dir, sitk.sitkFloat32)
        try:
            # register images
            reg_img, fixed_img, moving_img, final_transform = nrrd_reg_rigid( 
                patient_id=img_id, 
                moving_img=img, 
                output_dir='', 
                fixed_img=fixed_img,
                image_format='nii.gz')
            # crop
            crop_top_image_only(
                patient_id=img_id,
                img=reg_img,
                crop_shape=crop_shape,
                return_type='sitk_object',
                output_dir=crop_img_dir,
                image_format='nii.gz')
        except Exception as e:
            bad_ids.append(img_id)
            print(img_id, e)
    print('bad ids:', bad_ids)
                    

if __name__ == '__main__':

    crop_shape = (160, 160, 64)
    #crop_shape = (172, 172, 76)
    step = 'reg_crop'

    if step == 'respace':
        interpolation()
    elif step == 'reg_crop':
        reg_crop(crop_shape)

    




