# Modify HEVC source code

**HEVC（High Efficiency Video Coding）** 是2013年提出的最新的视频编码标准，它的核心是将视频中的每一帧图像分割成 **Coding Tree Unit（CTU）** ，然后对每个CTU确定最佳的分割深度，关于具体的算法可以参考：
- [Overview of the High Efficiency Video Coding(HEVC) Standard](http://iphome.hhi.de/wiegand/assets/pdfs/2012_12_IEEE-HEVC-Overview.pdf)
- [H.265 Terms - CTU, CU, PU, TU](https://codesequoia.wordpress.com/2012/10/28/hevc-ctu-cu-ctb-cb-pb-and-tb/)
- [2.H.265/HEVC —— 帧内预测](https://www.jianshu.com/p/d19d7eb3844a)

在了解了一些HEVC内部的术语如CTU, CU, TU...后，我们来试着利用HEVC的源代码输出CTU的分割信息。

### 代码的下载和配置
首先，需要下载源代码，源代码是使用SVN托管的，因此需要用SVN下载，我们可以使用[TortoiseSVN](https://tortoisesvn.net/)进行下载。安装好TortoiseSVN后，打开SVN browser，在地址栏输入

[https://hevc.hhi.fraunhofer.de/svn/svn_HEVCSoftware/](https://hevc.hhi.fraunhofer.de/svn/svn_HEVCSoftware/)

就可以看到源代码的目录结构，然后选择export，就可以将源代码保存到本地。注意这个目录下面有很多个版本，我们这里选择```/trunk/```目录下的主版本导出。

导出到本地之后，进入```/build/```文件夹，里面就是编译所需的文件，支持不同的平台：

![compilation](https://upload-images.jianshu.io/upload_images/10634927-4df93e2f5ea8080a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我使用的是VS2015编译，打开这个工程之后，可以看到所有的项目，对应的源代码在```/source/```文件夹下：

![HEVC projects](https://upload-images.jianshu.io/upload_images/10634927-f5776f6447dd5640.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

选择F7或者Build Solution就可以进行编译，生成exe文件，但是如果你直接去运行的话会发现程序输出一段说明文字之后就结束了，这是因为我们需要先进行配置，指定输入的视频和其他的一些参数。

配置文件在```/cfg/```目录下，其中最主要的两个配置文件是```bitstream.cfg```和```encoder_intra_main.cfg```，我们把这两个文件复制到一个自定义工作目录下，比如```E:\HM\trunk\workspace```，接下来在Visual Studio中，右击解决方案中“TAppEncoder”->“设为启动项目”
再右击“TAppEncoder”->”属性”->”配置属性”->”调试” ，在工作目录栏指定工作目录路径```E:\HM\trunk\workspace```，在命令参数栏中填写```-c encoder_intra_main.cfg -c bitstream.cfg```，如图：

![config](https://upload-images.jianshu.io/upload_images/10634927-8567ab352158df69.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

对于```encoder_intra_main.cfg```，我们需要进行配置的参数就只有：
```
#======== Quantization =============
QP                            : 32          # Quantization parameter(0-51)
```
这个值从0到51都可以。而在```bitstream.cfg```中，我们需要配置以下的参数：

![bitstream.cfg](https://upload-images.jianshu.io/upload_images/10634927-5a4f085de801c0df.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```InputFile```后面写上输入的```.YUV```视频文件的绝对路径，```FramesToBeEncoded```是指你想编码多少帧，至于```FrameRate```, ```SourceWidth```, ```SourceHeight```这些信息都在视频文件名中，比如我这里使用的```BasketballDrill_832x480_50.yuv```，文件名中就能看出宽度、高度和帧率。

接下来就可以运行了，运行结束后，工作目录下会出现两个文件：str.bin和rec.yuv，其中rec.yuv是编码过程中重建的yuv图像，str.bin则是压缩后的码流。 

### YUV文件
首先提供一些YUV视频资源的下载地址：

- [JCTVC Test Sequences](http://www.ucodec.com/resources.html)
- [YUV Video Sequences](http://trace.eas.asu.edu/yuv/)
- [YUV files](http://www.sunrayimage.com/examples.html)
- [ SJTU 4K Video Sequences](http://medialab.sjtu.edu.cn/web4k/index.html)
- [Ultra Video Group](http://ultravideo.cs.tut.fi/#testsequences)

对于HEVC的测试输入，一般都是采用YUV文件，推荐安装一个YUV播放器：[YUView](http://ient.github.io/YUView/)，可以看到每一帧的图片。

YUV文件就是由一帧一帧的图像构成的，在之前提到的配置文件中的参数```FramesToBeEncoded```中，你指定的编码多少帧，HEVC就会取前面的多少帧进行编码。如果想提取出YUV文件中的每一帧，可以使用[FFmpeg](https://ffmpeg.org/)：
```
ffmpeg -video_size 832x480 -r 50 -pixel_format yuv420p -i BasketballDrill_832x480_50.yuv output-%d.png
```
当然，使用的时候这个命令中的视频大小、帧率、像素格式、视频名称都需要根据具体的视频修改。其中像素格式（-pixel_format）这个参数可能很多人不知道该选什么，在命令行中输入：
```
ffmpeg -pix_fmts
```
可以看到FFmpeg支持的格式，这里使用的```yuv420p```是一般采用的格式，420代表的是 YCbCr color space with 4:2:0 sampling.
 
> This separates a color representation into three components called Y, Cb, and Cr. The Y component is also called luma, and represents brightness. The two chroma components Cb and Cr represent the extent to which the color deviates from gray toward blue and red, respectively.

关于color space，可以参考：
[colorspace – FFmpeg](https://trac.ffmpeg.org/wiki/colorspace)

如果不想了解这么多，只想直接知道自己所使用的YUV应该对应哪种 pixel format，方法是使用YUView打开YUV文件，在右侧的```properties```中有一个**YUV Format**，然后用这个format，去对应：

|Most commonly used formats|pixel_format|
|-|-|
|8-bit 4:2:0|```yuv420p```|
|8-bit 4:2:2|```yuv422p```|
|8-bit 4:4:4|```yuv444p```|
|10-bit 4:2:0|```yuv420p10le```|
|10-bit 4:2:2|```yuv422p10le```|

参考自：[Chroma Subsampling – FFmpeg](https://trac.ffmpeg.org/wiki/Chroma%20Subsampling)

### CTU分割信息的输出
这一部分是在**Encoder**部分完成的，所以我们主要看TAppEncoder这个项目。在```TEncGOP.cpp```中，有一个```precompressSlice()```和一个```compressSlice()```函数，前者可以不用管，而后者则计算出了每个ctu的最佳分割深度，转到```compressSlice()```函数的定义，来到了```TEncSlice.cpp```，其中对ctu进行最佳深度计算的关键函数是```compressCtu()```这个函数。

在```compressCtu()```这个函数内部，当```xCompressCU()```这个函数运行完成之后，最佳的分割深度就已经得到了，此时，如果想要输出当前ctu最佳的分割，可以在```xCompressCU()```这个函数后面，加上下面的语句：
```
  xCompressCU( m_ppcBestCU[0], m_ppcTempCU[0], 0 DEBUG_STRING_PASS_INTO(sDebug) );
  //============== add code from here ===============
  TComDataCU* DepthCU = m_ppcBestCU[0];
  UInt tempDepth;
  ofstream outfile("PartitionInfo.txt", ios::in | ios::app);
  for (UInt iPartitionNum = 0; iPartitionNum < DepthCU->getTotalNumPart(); iPartitionNum++)
  {
	  if (iPartitionNum % 16 == 0) {
		  outfile << endl;
	  }
	  tempDepth = DepthCU->getDepth(g_auiRasterToZscan[iPartitionNum]);
	  outfile << " " << tempDepth;
  }
  outfile << endl;
  // =============code added end here===============
```
最佳的分割保存在```m_ppcBestCU[0]```里面，使用```getDepth()[i]```就可以得到。

接下来，如果我们不仅想输出所有的ctu分割信息，还想输出当前是第几个ctu，这时候就要去找哪个变量记录了当前ctu的编号，我们可以回到```compressCtu()```函数开始的地方，看到这个函数接收了一个参数```TComDataCU* pCtu```，而我们可以通过```pCtu->getCtuRsAddr()```这个语句得到当前CTU的编号，所以，可以在```xCompressCU()```之前，加上下面的语句：
```
//============== add code from here ===============
ofstream outfile("PartitionInfo.txt", ios::in | ios::app);
UInt temp_ctu_addr = pCtu->getCtuRsAddr();
outfile << "ctu:" << temp_ctu_addr << endl;
outfile.close();
// =============code added end here===============
xCompressCU(m_ppcBestCU[0], m_ppcTempCU[0], 0 DEBUG_STRING_PASS_INTO(sDebug));
```

除了输出当前ctu的编号，我们还想要输出当前编码到了第几帧（frame），这时仍然可以通过Debug的方式找到存储这一信息的变量。最终发现当前编码的frame数量存储在变量```m_iFrameRcvd```中，而这一变量是在```TAppEncTop.cpp```文件中。因此，如果要输出当前是第几帧，可以在```TAppEncTop.cpp```文件中找到
```
m_iFrameRcvd++;
```
这一语句，并在后面加入：
```
ofstream outfile("PartitionInfo.txt", ios::in | ios::app);
outfile<< "frame:" << m_iFrameRcvd << endl;
```
这样，我们就可以输出每个frame对应的每个ctu的分割信息了，像这样：

![PartitionInfo](https://upload-images.jianshu.io/upload_images/10634927-6b8660a4f818227a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


然后我们可以使用Matlab画出每一帧的PU分割信息，参考：
- [MatLab画PU分割模式图](https://blog.csdn.net/HEVC_LG/article/details/45341737)
- [HEVC里面CU与TU打印到屏幕及提取到txt文本](https://blog.csdn.net/sinat_33718563/article/details/53914719)
------
最后补充一下，HEVC在帧内预测的时候，对于每个depth，都要向下分成4个depth递归寻找最优分割，因此我们还可以把每个depth对应的RD-cost打印出来。Depth0会分成4个Depth1，Depth1会分成4个Depth2，Depth2分成4个Depth3，Depth3向下判断是8x8还是4x4的PU

打印出每种分割的RD-cost的好处就是，当我们训练好了神经网络模型，用模型生成CU分割深度信息的时候，我们可以用RD-cost来和HEVC编码器比较RD-cost变化了多少，而神经网络模型得到的分割方法的RD-cost的计算就可以用之前打印出来的每个depth的RD-cost

在```xCompressCU()```函数内部，有两个变量：```m_ppcBestCU```和```m_ppcTempCU```，想要得到当前深度的RD-cost可以通过调用它们的```getTotalCost()```方法，不过```m_ppcBestCU```只存放了最佳的分割深度，所以不能得到全面的RD-cost，因此只能调用```m_ppcTempCU```的```getTotalCost()```方法。但```m_ppcTempCU```在```xCompressCU()```函数内部并没有存放或者被赋值RD-cost信息，我们只能到```xCheckRDCostIntra()```函数内部来获取。

在```xCheckRDCostIntra()```函数内部，当前所在的深度存放在变量```uiDepth```中。我们可以在
```
rpcTempCU->getTotalCost() = m_pcRdCost->calcRdCost( rpcTempCU->getTotalBits(), rpcTempCU->getTotalDistortion() );
```
之后，添加如下代码，输出每一层深度的RD-cost：
```
  rpcTempCU->getTotalBits() = m_pcEntropyCoder->getNumberOfWrittenBits();
  rpcTempCU->getTotalBins() = ((TEncBinCABAC *)((TEncSbac*)m_pcEntropyCoder->m_pcEntropyCoderIf)->getEncBinIf())->getBinsCoded();
  rpcTempCU->getTotalCost() = m_pcRdCost->calcRdCost( rpcTempCU->getTotalBits(), rpcTempCU->getTotalDistortion() );
  // ==============added code to print depth and RDcost==========
  ofstream outfile("rdcost.txt", ios::in | ios::app);
  double temp_rdcost;
  temp_rdcost = rpcTempCU->getTotalCost();
  outfile << "depth:" << uiDepth << endl;
  outfile << temp_rdcost << endl;
  outfile.close();
  // ===============code added end here=====================
  xCheckDQP( rpcTempCU );
```

同样，我们还是需要输出是在哪一帧，以及哪个CTU。输出之后，在进行一些处理，就能方便地计算自己的模型的CU划分对应的RD-cost了。