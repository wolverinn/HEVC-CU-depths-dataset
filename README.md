# HEVC-CU-depths-dataset
A dataset that contains the Coding Unit image files and their corresponding depths for HEVC intra-prediction.

### What's in the dataset?

In HEVC intra-prediction, each I-frame is divided into 64x64 Coding Tree Units (CTU). For each 64x64 CTU, there's a depth prediction represented by a 16x16 matrix. The elements in the matrix are 0, 1, 2 or 3, indicating depth 0/1/2/3 for a 4x4 block in the CTU.

The dataset contains images and corresponding labels. There're three folders: ```train```, ```validation```, ```test```

- Image files: Each image may have different size, and is one frame extracted from a video. When you use it, you can split the image into several 64x64 images or 32x32 and so on.
- Labels: The labels are in the ```pkl``` folder. For one CTU, which is a 64x64 image file, the label will be a Python list with a length of 16. Why a length 16 vector instead of a 16x16 matrix? Because there's redundant information for a 16x16 matrix, and it can be reduced to a 16x1 vector. So, for a 64x64 CTU, it has 16 labels, each label corresponds to a 16x16 image block in the CTU.

If you split the image files into 64x64 CTUs, the size of the train dataset is around 110K images. The size of the validation dataset is around 40K images.

### How to relate images and labels

The name of a image file is like: ```v_0_42_104_.jpg```, which means ```v_VideoNumber_FrameNumber_CtuNumber_.jpg```.

You can use the VideoNumber to find the corresponding ```.pkl``` file, like ```v_0.pkl```. Then, when you load the pickle file, you will get a Python dict:
```
{
    "2":{
        "0":[...]
        "1":[...]
        .
        .
        .
        "103":[...]
    }
    "27":{
        ...
    }
}
```

To get the label you want for a certain 64x64 CTU, you can index the dict by: ```label_vector = video_dict[FrameNumber][CtuNumber]```, for example: ```label_vector = video_dict["42"]["104"]```. The ```label_vector``` will be a length 16 Python list.

### Example for loading the dataset

Here's an example for loading the dataset in deep learning projects implemented in PyTorch. Find the example in ```load_example.py```

### How to use the dataset in deep learning?

You can refer to these documents:

- [A deep convolutional neural network approach for complexity reduction on intra-mode HEVC](https://ieeexplore.ieee.org/document/8019316)
- [Fast CU Depth Decision for HEVC Using Neural Networks](https://ieeexplore.ieee.org/document/8361836)

In HEVC intra-prediction, for each 64x64 CTU, it will take the encoder a lot of time to find the best CU depths, which is the 16x16 matrix. So we can use a deep learning approach to predict the CU depths for a 64x64 CTU.

### Advanced Option: build your own dataset

I provide my source code for generating the dataset here. You can modify my code ```gen_dataset.py``` to build your own dataset. Here are some tips:

TIP 1: Download YUV file resources

YUV files are used as input of HEVC encoder, and as output, you will get the 16x16 matrix, which you can later process. At the same time, you can use FFmpeg to extract each frame from YUV files.

Here are some sites to find YUV resources:

- [JCTVC Test Sequences](http://www.ucodec.com/resources.html)
- [YUV Video Sequences](http://trace.eas.asu.edu/yuv/)
- [YUV files](http://www.sunrayimage.com/examples.html)
- [ SJTU 4K Video Sequences](http://medialab.sjtu.edu.cn/web4k/index.html)
- [Ultra Video Group](http://ultravideo.cs.tut.fi/#testsequences)

TIP 2: Check the directories in the code for:
- The directory of image files and pickle files
- The directory of YUV files
- The directory of the config files for HEVC encoder
- The directory to store temporary frames extracted from YUV files

It will take some time to generate the dataset. Be prarared.