import json
import cv2
import os
import time
import sys

import logging

import numpy as np



#================================================================================
# Please change following path to your OWN
LOCAL_ROOT = './'
LOCAL_IMAGE_LIST_PATH = 'metas/intra_test/test_label.json'
#================================================================================


def read_image(image_path):
    """
    Read an image from input path

    params:
        - image_local_path (str): the path of image.
    return:
        - image: Required image.
    """

    image_path = LOCAL_ROOT + image_path

    img = cv2.imread(image_path)
    # Get the shape of input image
    real_h,real_w,c = img.shape
    assert os.path.exists(image_path[:-4] + '_BB.txt'),'path not exists' + ' ' + image_path
    
    with open(image_path[:-4] + '_BB.txt','r') as f:
        material = f.readline()
        try:
            x,y,w,h,score = material.strip().split(' ')
        except:
            logging.info('Bounding Box of' + ' ' + image_path + ' ' + 'is wrong')   

        try:
            w = int(float(w))
            h = int(float(h))
            x = int(float(x))
            y = int(float(y))
            w = int(w*(real_w / 224))
            h = int(h*(real_h / 224))
            x = int(x*(real_w / 224))
            y = int(y*(real_h / 224))

            # Crop face based on its bounding box
            y1 = 0 if y < 0 else y
            x1 = 0 if x < 0 else x 
            y2 = real_h if y1 + h > real_h else y + h
            x2 = real_w if x1 + w > real_w else x + w
            img = img[y1:y2,x1:x2,:]

        except:
            logging.info('Cropping Bounding Box of' + ' ' + image_path + ' ' + 'goes wrong')   

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img



def get_image(max_number=None):
    """
    This function returns a iterator of image.
    It is used for local test of participating algorithms.
    Each iteration provides a tuple of (image_id, image), each image will be in RGB color format with array shape of (height, width, 3)
    
    return: tuple(image_id: str, image: numpy.array)
    """
    with open(LOCAL_ROOT+LOCAL_IMAGE_LIST_PATH) as f:
        image_list = json.load(f)
    logging.info("got local image list, {} image".format(len(image_list.keys())))
    Batch_size = 1024
    logging.info("Batch_size=, {}".format(Batch_size))
    n = 0
    final_image = []
    final_image_id = []
    for idx,image_id in enumerate(image_list):
        # get image from local file
        try:
            image = read_image(image_id)
            final_image.append(image)
            final_image_id.append(image_id)
            n += 1
        except:
            logging.info("Failed to read image: {}".format(image_id))
            raise

        if n == Batch_size or idx == len(image_list) - 1:
            np_final_image_id = np.array(final_image_id)
            np_final_image = np.array(final_image)
            n = 0
            final_image = []
            final_image_id = []
            yield np_final_image_id, np_final_image


#Get the threshold under several fpr
def get_thresholdtable_from_fpr(scores,labels, fpr_list):
    """Calculate the threshold score list from the FPR list

    Args:
      score_target: list of (score,label)

    Returns:
      threshold_list: list, the element is threshold score calculated by the
      corresponding fpr
    """
    threshold_list = []
    live_scores = []
    for score, label in zip(scores,labels):
        if label == 0:
            live_scores.append(float(score))
    live_scores.sort(reverse=True)
    live_nums = len(live_scores)
    for fpr in fpr_list:
        i_sample = int(fpr * live_nums)
        i_sample = max(1, i_sample)
        threshold_list.append(live_scores[i_sample - 1])
    return threshold_list

#Get the threshold under thresholds
def get_tpr_from_threshold(scores,labels, threshold_list):
    """Calculate the recall score list from the threshold score list.

    Args:
      score_target: list of (score,label)
      threshold_list: list, the threshold list

    Returns:
      recall_list: list, the element is recall score calculated by the
                   correspond threshold
    """
    tpr_list = []
    hack_scores = []
    for score, label in zip(scores,labels):
        if label == 1:
            hack_scores.append(float(score))
    hack_scores.sort(reverse=True)
    hack_nums = len(hack_scores)
    for threshold in threshold_list:
        hack_index = 0
        while hack_index < hack_nums:
            if hack_scores[hack_index] <= threshold:
                break
            else:
                hack_index += 1
        if hack_nums != 0:
            tpr = hack_index * 1.0 / hack_nums
        else:
            tpr = 0
        tpr_list.append(tpr)
    return tpr_list



def verify_output(output_probs):
    """
    This function prints the groundtruth and prediction for the participant to verify, calculates average FPS.

    params:
    - output_probs (dict): dict of probability of every video
    - output_times (dict): dict of processing time of every video
    - num_frames (dict): dict of number of frames extracting from every video
    """
    with open (LOCAL_ROOT+LOCAL_IMAGE_LIST_PATH,'r') as f:
        gts = json.load(f)

    scores = []
    labels = []
    for k in output_probs:
        #import pdb;pdb.set_trace()
        if k in gts:
            scores.append(output_probs[k])
            # 43 is the index of Live/Spoof label
            labels.append(gts[k][43])

    fpr_list = [0.01, 0.005, 0.001]
    threshold_list = get_thresholdtable_from_fpr(scores,labels, fpr_list)
    tpr_list = get_tpr_from_threshold(scores,labels, threshold_list)
      
    # Show the result into score_path/score.txt  
    logging.info('TPR@FPR=10E-3: {}\n'.format(tpr_list[0]))
    logging.info('TPR@FPR=5E-3: {}\n'.format(tpr_list[1]))
    logging.info('TPR@FPR=10E-4: {}\n'.format(tpr_list[2]))

    logging.info("Done")


