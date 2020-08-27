"""
This script provides a local test routine so you can verify the algorithm works before pushing it to evaluation.

It runs your detector on several local images and verify whether they have obvious issues, e.g:
    - Fail to start
    - Wrong output format

It also prints out the runtime for the algorithms for your references.


The participants are expected to implement a face forgery detector class. The sample detector illustrates the interface.
Do not modify other part of the evaluation toolkit otherwise the evaluation will fail.

Author: Yuanjun Xiong, Zhengkui Guo, Yuanhan Zhang
Contact: celebaspoof@gmail.com

CelebA-Spoof 
"""

import time
import sys
import logging

import numpy as np
from client import get_image, verify_output

logging.basicConfig(level=logging.INFO)


from tsn_predict import TSNPredictor as CelebASpoofDetector


def run_test(detector_class, image_iter):
    """
    In this function we create the detector instance. And evaluate the wall time for performing CelebASpoofDetector.
    """

    # initialize the detector
    logging.info("Initializing detector.")
    try:
        detector = detector_class()
    except:
        # send errors to the eval frontend
        raise
    logging.info("Detector initialized.")


    # run the images one-by-one and get runtime
    output_probs = {}
    eval_cnt = 0

    logging.info("Starting runtime evaluation")
    for image_id, image in image_iter:
        time_before = time.time()
        try:
            prob = detector.predict(image)

            for idx,i in enumerate(image_id):
                output_probs[i] = float(prob[idx][1])
        except:
            # send errors to the eval frontend
            logging.error("Image id failed: {}".format(image_id))
            raise


        eval_cnt += len(image)

        if eval_cnt % 10 == 0:
            logging.info("Finished {} images".format(eval_cnt))

    logging.info("""
    ================================================================================
    All images finished, showing verification info below:
    ================================================================================
    """)

    # verify the algorithm output
    verify_output(output_probs)


if __name__ == '__main__':
    celebA_spoof_image_iter = get_image()
    run_test(CelebASpoofDetector, celebA_spoof_image_iter)
