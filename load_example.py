import torch
import torch.utils.data as data
from torchvision import datasets, transforms
import os
import pickle
import numpy as np
from PIL import Image
import math

LOAD_DIR = "."
BATCH_SIZE=256

transform = transforms.Compose([
    transforms.ToTensor(),  # 将图片转换为Tensor,归一化至[0,1]
    transforms.Normalize(mean=[.5, .5, .5], std=[.5, .5, .5])  # 标准化至[-1,1]
])

def from_ctufile(load_type,video_number,frame_number,ctu_number,layer2):
    # https://pytorch-cn.readthedocs.io/zh/latest/package_references/Tensor/
    ctu_file = "{}/dataset/pkl/{}/v_{}.pkl".format(LOAD_DIR,load_type,video_number)
    f_pkl = open(ctu_file,'rb')
    video_dict = pickle.load(f_pkl)
    f_pkl.close()
    ctu_info = video_dict[frame_number][ctu_number]
    if layer2 == 0:
        label_list = [ctu_info[0],ctu_info[1],ctu_info[4],ctu_info[5]]
    elif layer2 == 1:
        label_list = [ctu_info[2],ctu_info[3],ctu_info[6],ctu_info[7]]
    elif layer2 == 2:
        label_list = [ctu_info[8],ctu_info[9],ctu_info[12],ctu_info[13]]
    else:
        label_list = [ctu_info[10],ctu_info[11],ctu_info[12],ctu_info[15]]
    label = torch.tensor(label_list)
    return label

class ImageSet(data.Dataset):
    def __init__(self,root):
        # 所有图片的绝对路径
        self.img_files = []
        self.root = root
        for img in os.listdir(root):
            ctu_numbers_per_frame = img.split('_')[3]
            for ctu_number in range(int(ctu_numbers_per_frame)):
                for layer2 in range(4):
                    self.img_files.append((img,ctu_number,layer2))
        self.transforms=transform

    def __getitem__(self, index):
        img = Image.open(os.path.join(self.root,self.img_files[index][0]))
        video_number = self.img_files[index][0].split('_')[1]
        frame_number = self.img_files[index][0].split('_')[2]
        ctu_number = self.img_files[index][1]
        layer2 = self.img_files[index][2]
        img_width, _ = img.size
        img_row = ctu_number // math.ceil(img_width / 64)
        img_colonm = ctu_number % math.ceil(img_width / 64)
        start_pixel_x = img_colonm * 64 + (layer2 % 2)*32
        start_pixel_y = img_row * 64 + (layer2 // 2)*32
        cropped_img = img.crop((start_pixel_x, start_pixel_y, start_pixel_x + 32, start_pixel_y + 32)) # 依次对抽取到的帧进行裁剪
        img.close()
        if "train" in self.root:
            load_type = "train"
        elif "validation" in self.root:
            load_type = "validation"
        else:
            load_type = "test"
        if self.transforms:
            data = self.transforms(cropped_img)
        else:
            img = np.asarray(cropped_img)
            data = torch.from_numpy(img)
        cropped_img.close()
        label = from_ctufile(load_type,video_number,frame_number,str(ctu_number),layer2)
        return data,label

    def __len__(self):
        return len(self.img_files)

train_loader = data.DataLoader(ImageSet("{}/dataset/img/train/".format(LOAD_DIR)),batch_size=BATCH_SIZE,shuffle=True)
