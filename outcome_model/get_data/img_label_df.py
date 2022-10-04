import numpy as np
import os
import glob
import pandas as pd
import SimpleITK as sitk
from sklearn.model_selection import KFold


def img_label_df(proj_dir, tumor_type, input_img_type, save_img_type):


    """
    create df for data and pat_id to match labels
    
    Args:
        proj_dir {path} -- project dir;
        out_dir {path} -- output dir;
        save_img_type {str} -- image type: nii or npy;
 
    Returns:
        Dataframe with image dirs and labels;
    
    Raise errors:
        None;

    """

    pn_masked_img_dir = os.path.join(proj_dir, 'data/pn_masked_img')
    pn_raw_img_dir = os.path.join(proj_dir, 'data/pn_raw_img')
    p_masked_img_dir = os.path.join(proj_dir, 'data/p_masked_img')
    p_raw_img_dir = os.path.join(proj_dir, 'data/p_raw_img')
    n_masked_img_dir = os.path.join(proj_dir, 'data/n_masked_img')
    n_raw_img_dir = os.path.join(proj_dir, 'data/n_raw_img')
    pro_data_dir = os.path.join(proj_dir, 'pro_data')

    # create df for data and pat_id to match labels
    #----------------------------------------------
    if tumor_type == 'primary_node':
        if input_img_type == 'masked_img':
            # saved csv file name
            save_fn = 'df_img_label_pn_masked.csv'
            if save_img_type == 'npy':
                img_dirs = [path for path in sorted(glob.glob(pn_masked_img_dir + '/*npy'))]
            elif save_img_type == 'nii':
                img_dirs = [path for path in sorted(glob.glob(pn_masked_img_dir + '/*nii.gz'))]
        elif input_img_type == 'raw_img':
            # saved csv file name
            save_fn = 'df_img_label_pn_raw.csv'
            if save_img_type == 'npy':
                img_dirs = [path for path in sorted(glob.glob(pn_raw_img_dir + '/*npy'))]
            elif save_img_type == 'nii':
                img_dirs = [path for path in sorted(glob.glob(pn_raw_img_dir + '/*nii.gz'))]
    if tumor_type == 'primary':
        if input_img_type == 'masked_img':
            # saved csv file name
            save_fn = 'df_img_label_p_masked.csv'
            if save_img_type == 'npy':
                img_dirs = [path for path in sorted(glob.glob(p_masked_img_dir + '/*npy'))]
            elif save_img_type == 'nii':
                img_dirs = [path for path in sorted(glob.glob(p_masked_img_dir + '/*nii.gz'))]
        elif input_img_type == 'raw_img':
            # saved csv file name
            save_fn = 'df_img_label_p_raw.csv'
            if save_img_type == 'npy':
                img_dirs = [path for path in sorted(glob.glob(p_raw_img_dir + '/*npy'))]
            elif save_img_type == 'nii':
                img_dirs = [path for path in sorted(glob.glob(p_raw_img_dir + '/*nii.gz'))]    
    if tumor_type == 'node':
        if input_img_type == 'masked_img':
            # saved csv file name
            save_fn = 'df_img_label_n_masked.csv'
            if save_img_type == 'npy':
                img_dirs = [path for path in sorted(glob.glob(n_masked_img_dir + '/*npy'))]
            elif save_img_type == 'nii':
                img_dirs = [path for path in sorted(glob.glob(n_masked_img_dir + '/*nii.gz'))]
        elif input_img_type == 'raw_img':
            # saved csv file name
            save_fn = 'df_img_label_n_raw.csv'
            if save_img_type == 'npy':
                img_dirs = [path for path in sorted(glob.glob(n_masked_img_dir + '/*npy'))]
            elif save_img_type == 'nii':
                img_dirs = [path for path in sorted(glob.glob(n_masked_img_dir + '/*nii.gz'))]

    fns = []
    for img_dir in img_dirs:
        ID = img_dir.split('/')[-1].split('.')[0]
        fns.append(ID)
    print('pat_id:', len(fns))
    print('img_dir:', len(img_dirs))
    df_img = pd.DataFrame({'patid': fns, 'img_dir': img_dirs})
    print('total img number:', df_img.shape[0])
    print(df_img[0:10])

    # create matching label df
    #--------------------------
    df = pd.read_csv(os.path.join(pro_data_dir, 'label.csv'))
    print('total label number:', df.shape)
    ## add img paths to the label df
    pat_ids = []
    for pat_id in df['pat_id']:
        if pat_id not in fns:
            pat_ids.append(pat_id)
    df_label = df[~df['pat_id'].isin(pat_ids)]
    print('total label number:', df_label.shape)
    print(df_label[0:10])

    # create df for data and pat_id to match labels
    #----------------------------------------------
    fns = []
    for img_dir in img_dirs:
        ID = img_dir.split('/')[-1].split('.')[0]
        fns.append(ID)
    print('pat_id:', len(fns))
    print('img_dir:', len(img_dirs))
    df_img = pd.DataFrame({'pat_id': fns, 'img_dir': img_dirs})
    print('total img number:', df_img.shape[0])
    print(df_img[0:10])

    # merge df_img and df_label using matching patient ID
    #----------------------------------------------------
    df = pd.merge(df_label, df_img, on='pat_id')
    print('total df size:', df.shape)
    print(df[0:20])
    df.to_csv(os.path.join(pro_data_dir, save_fn), index=False)
    print('complete img and lable df have been saved!!!')
    





