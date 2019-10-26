import os
from PIL import Image
import math
import pickle
import shutil

# this script needs to be in the same directory of the encoder.exe: WORKSPACE_PATH, config file must be in the config folder of the WORKSPACE
BUILD_TYPE = "test" # train, test, validation
YUV_FILE_PATH = ".\\yuv-file\\{}".format(BUILD_TYPE)
IMG_PATH = ".\\dataset\\img\\{}".format(BUILD_TYPE)
WORKSPACE_PATH = os.getcwd()
CtuInfo_FILENAME = "BasketballdrillCU.txt"

def gen_cfg(yuv_filename):
    FrameRate = yuv_filename.split('_')[2].strip(".yuv")
    SourceWidth = yuv_filename.split('_')[1].split('x')[0]
    SourceHeight = yuv_filename.split('_')[1].split('x')[1]
    with open('.\\config\\bitstream.cfg','w') as f:
        f.write("InputFile : {}\\{}\n".format(YUV_FILE_PATH,yuv_filename))
        f.write("InputBitDepth : 8\n")
        f.write("InputChromaFormat : 420\n")
        f.write("FrameRate : {}\n".format(FrameRate))
        f.write("FrameSkip : 0\n")
        f.write("SourceWidth : {}\n".format(SourceWidth))
        f.write("SourceHeight : {}\n".format(SourceHeight))
        f.write("FramesToBeEncoded : 50000\n")
        f.write("Level : 3.1")

def dump_ctu_file(video_number,frame_number):
    # 将抽取到的帧的所有ctu分割信息保存到pickle：{"frame_number_1":{"ctu_number_1":[...];"ctu_number_2":[...]};"frame_number_2":...}
    frame_detected = 0
    ctu_number = "0"
    temp_ctu = []
    f_pkl = open("v_{}.pkl".format(video_number), 'rb')
    video_dict = pickle.load(f_pkl)
    f_pkl.close()
    video_dict[frame_number] = {}
    with open(CtuInfo_FILENAME,'r') as f:
        for i,line in enumerate(f):
            if frame_detected == 0:
                if "frame" in line:
                    current_frame = line.split(':')[1]
                    if int(frame_number) == int(current_frame):
                        frame_detected = 1
            elif "frame" in line:
                break
            elif "ctu" in line:
                temp_ctu = []
                ctu_number = int(line.split(':')[1])
                line_count = 0
                video_dict[frame_number][str(ctu_number)] = []
            else:
                # 每个CTU提取出长度为16的列表方便处理
                line_depths = line.split(' ')
                if line_count % 4 == 0:
                    for index in range(4):
                        temp_ctu.append(int(line_depths[4*index]))
                        video_dict[frame_number][str(ctu_number)] = temp_ctu
                line_count += 1
    if video_dict[frame_number] == {}:
        video_dict.pop(frame_number)
    f_pkl = open("v_{}.pkl".format(video_number), 'wb')
    pickle.dump(video_dict, f_pkl)
    f_pkl.close()

def crop_image_to_ctu(video_number):
    frames = len(os.listdir("{}\\temp-frames".format(WORKSPACE_PATH))) # 当前视频一共有多少帧
    random_frames = [2,27]
    n = int((50+frames/40)//4)
    for i in range(frames//n):
        f_index = 27 + n*(i+1)
        if f_index > frames or f_index >= 50000:
            break
        else:
            random_frames.append(f_index) # 随机抽取帧，有一个公式得出抽取的帧的编号
    f_pkl = open("v_{}.pkl".format(video_number), 'wb')
    video_dict = {}
    pickle.dump(video_dict, f_pkl)
    f_pkl.close()
    for image_file in os.listdir("{}\\temp-frames".format(WORKSPACE_PATH)):
        frame_number = int(image_file.split('_')[2])-1 # ffmpeg生成帧编号是从1开始，这里减1将编号变成从0开始和ctu分割信息对应
        if frame_number in random_frames:
            img = Image.open(os.path.join("{}\\temp-frames".format(WORKSPACE_PATH),image_file))
            img_width, img_height = img.size
            ctu_number_per_img = math.ceil(img_width / 64) * math.ceil(img_height / 64)
            img.close()
            shutil.copy(os.path.join("{}\\temp-frames".format(WORKSPACE_PATH),image_file),"{}\\v_{}_{}_{}_.jpg".format(IMG_PATH,video_number,str(frame_number),str(ctu_number_per_img)))
            dump_ctu_file(video_number, str(frame_number)) # 将当前帧的所有ctu分割信息保存到新的文件，只保存抽取的帧的信息
        os.remove(os.path.join("{}\\temp-frames".format(WORKSPACE_PATH),image_file)) # 裁剪过后的帧就删掉
    print("Total frames extracted from video_{} : {}".format(video_number,len(random_frames)))

encoding_cmd = "TAppEncoder.exe -c .\\config\\encoder_intra_main.cfg -c .\\config\\bitstream.cfg"
for i,yuv_filename in enumerate(os.listdir(YUV_FILE_PATH)):
    #if i <= 6:
     #   continue
    gen_cfg(yuv_filename) # 生成运行HEVC编码器需要的配置文件，包括帧率，宽高等参数，参数从文件名中读取
    os.system(encoding_cmd) #调用编码器输出ctu分割信息
    # 使用ffmpeg从YUV文件中分割出每一帧
    # ffmpeg -video_size 352x288 -r 20 -pixel_format yuv420p -i E:\HM\trunk\workspace\yuv-resources\train\paris_352x288_20.yuv E:\HM\trunk\workspace\temp-frames\v_0_%d_.jpg
    gen_frames_cmd = "ffmpeg -video_size {} -r {} -pixel_format yuv420p -i {}\\{} {}\\temp-frames\\v_{}_%d_.jpg".format(yuv_filename.split('_')[1],yuv_filename.split('_')[2].strip(".yuv"),YUV_FILE_PATH,yuv_filename,WORKSPACE_PATH,str(i))
    os.system(gen_frames_cmd)
    print("processing yuv file: {}".format(yuv_filename))
    crop_image_to_ctu(str(i)) # 从当前视频分割出的所有帧中随机抽取帧并裁剪成64x64的图片
    f = open("log.txt",'a')
    f.write("{}\n".format(yuv_filename))
    f.close()
    os.remove(CtuInfo_FILENAME)