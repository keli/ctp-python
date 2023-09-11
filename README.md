# Python版CTP期货接口

这套接口使用swig为官方C++版CTP接口提供Python版API，同时支持Linux/Mac/Windows。

## 注意事项

- **本项目出于个人兴趣及分享目的，与上期所CTP官方无任何关系。本人不对使用这套库的任何后果负责。**
- 本人生产环境使用Linux，其他平台仅编译测试通过
- 已通过github workflow编译好发布至pypi
- Linux已测试环境：Debian stable amd64
- Mac已测试环境：Mac OS Ventura（M1 Mac Mini，API版本6.6.9以上，Intel Mac未测试）
- Windows已测试环境：Windows 11 64位（API版本6.6.9以上）
- api目录中结尾带`.c`的版本号为测评版
- CTP返回的GBK编码字符串已经全部自动转换为UTF-8
- 市场数据中的极大值代表无数据，为可读性起见打印整个结构体时会显示为None

## 安装方法

```
pip install ctp-python==6.6.9
```

如果在Windows下使用conda环境，那么使用前还需要安装libiconv
```
conda install -c conda-forge libiconv
```

- 只支持6.6.9及更新的CTP版本
- 已编译的二进制版本支持Python3.7 - 3.11
- 已编译的二进制版本支持平台：Windows amd64，Linux amd64，MacOS arm64 和 amd64
- 其他版本请自行尝试编译（前提是有对应的CTP C++链接库），具体方法见下

## 编译环境准备

#### Windows 11

1. 安装编译环境
```
winget install Microsoft.VisualStudio.2022.BuildTools
```
> 然后菜单栏搜索并打开Visual Studio Installer，修改Build Tools的配置，将使用C++的桌面开发勾选上并安装

2. 安装Python（以miniconda为例）
```
winget install miniconda3
conda init
```

3. 安装swig命令，以及iconv库
```
conda install -c conda-forge swig libiconv
```
>可能需要关闭并重新打开命令行

#### Mac OS

1. 先在App Store中找到并安装Xcode，然后再安装Xcode命令行工具
```
xcode-select --install
```
> 在弹出的窗口确认

2. 安装Python（推荐使用pyenv）
> 略

3. 安装swig命令（以homebrew为例）
```
brew install swig
```

#### Linux

> 使用系统自带包管理器安装swig和gcc/g++编译器即可

> 推荐使用pyenv安装管理python版本


## 安装说明

1. 克隆代码到本地
```
git clone git@github.com:keli/ctp-python.git
cd ctp-python
```

2. 编译安装
```
python setup.py install
```
> 或
```
pip install .
```

3. 版本选择（可选）

目前默认使用的是6.6.9 版本。如果需要链接和使用其他版本，只需要在编译安装前，设置API_VER环境变量为相应版本即可。

以6.6.9.c版为例:

> Linux/Mac(bash/zsh)：
```
export API_VER=6.6.9.c
```

> Windows：
```
set API_VER=6.6.9.c
```

## 测试

> 打开python shell，检查是否能正常import ctp

```
$ python
Python 3.11.3
Type "help", "copyright", "credits" or "license" for more information.
>>> import ctp
>>>
```

> 跑一下测试（以simnow服务器为例，需要在simnow网站注册用户）
```
pytest -s tests/test_trader.py --front=tcp://218.202.237.33:10203 --broker=9999 --user=<investor_id> --password=<password> --app=simnow_client_test --auth=0000000000000000
```


## Linux下穿透式监管信息采集常见问题

- 到底需要不需要LinuxDataCollect.so?

  自写CTP程序直连是不需要的，如果你不确定，那就是不需要

- 报错Decrypt handshake data failed

  CTP版本与服务器端不一致，首次跟期货公司采集的时候请用“评测版本”如6.3.13，后续生产环境请用“生产版本”如6.3.15

- 报错 dmidecode not found

  通常默认都有装，加一下dmidecode命令的相关路径到PATH，一般是/usr/sbin

- 报一堆 permission denied

  给dmidecode加下权限`sudo chmod a+s /usr/sbin/dmidecode`

- 拿不到硬盘序列号

  Debian系可以`sudo adduser username disk`把自己加到disk组（加完需要重新登录，输入`groups`确认自己已经在disk组里），或者直接给磁盘设备文件加读权限`sudo chmod a+r /dev/sda`

- 不知道什么情况，xx数据拿不到

  用以下python脚本自己慢慢试吧，当打印出来是第一行结果是0则成功了，否则是-1。第二行是取到的信息，格式为```(操作系统类型)@(信息采集时间)@(内网IP1)@(内网IP2)@(网卡MAC1)@(网卡MAC2)@(设备名)@(操作系统版本)@(Disk_ID)@(CPU_ID)@(BIOS_ID)```
  
  ```python
  import ctypes
  dll = ctypes.cdll.LoadLibrary('./thosttraderapi_se.so')
  info = (ctypes.c_char * 344)()
  length = ctypes.c_int()
  print(dll._Z21CTP_GetRealSystemInfoPcRi(info, ctypes.byref(length)))
  print(info.value)
  ```

## 其他常见问题

- 为什么报UTF-8和GBK的转码错误？

  这个是内存管理的问题而不是转码的问题，ctp库会释放掉它传给你的回调函数的内容，当你打印的时候这块内存已经free掉了，所以就报转码失败了。这个最理想的处理是改swig定义来自动把相应的结构体内容拷到python，但是我还没太搞清楚怎么在swig中做这件事。我自己的代码里面需要缓存起来的ctp结构只有很少的几处，直接在用户代码中手动拷贝到自己定义的python数据类型就可以了。


