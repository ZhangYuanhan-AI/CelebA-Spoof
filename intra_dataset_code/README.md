# Code for Intra-dataset Benchmark in CelebA-Spoof

![image-20200827183455502](../fig/intra_dataset_test.png#pic_center)

This is the code of  inference stage  for Intra-dataset Benchmark.

## Dependencies

- python 3
- opencv-python
- numpy
- json
- \> = Pytorch 0.4.1

## Usage

- **Step 1**. Change line 13 - line 17 of client.py.

  ```python
  #================================================================================
  # Please change following path to your OWN
  # 'metas/intra_test/test_label.json' is the label file which we have already upload in [here](https://github.com/Davidzhangyuanhan/CelebA-Spoof#dataset-downloads)
  LOCAL_ROOT = './'
  LOCAL_IMAGE_LIST_PATH = 'metas/intra_test/test_label.json'
  #================================================================================
  ```

- **Step 2.** Run it !!

  ```python
  python main.py
  ```
  
- **Step 3**. Enjoy a cup of coffee and Wait for the output as below.

  ```python
      ================================================================================
      All images finished, showing verification info below:
      ================================================================================
  INFO:root:TPR@FPR=10E-3: 0.9887188604567486
  INFO:root:TPR@FPR=5E-3: 0.9729294981691959
  INFO:root:TPR@FPR=10E-4: 0.8641818528160519
  INFO:root:Done
  ```

