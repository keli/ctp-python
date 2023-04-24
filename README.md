# CTP接口的Python封装

这套封装是本人在生产环境使用的，支持穿透式监管。自己封装的主要原因是其他作者经常弃坑，虽然封装得更好吧，但是动不动就不更新了。
考虑到一般在ctp之上还会有应用层的封装，也没必要做得太讲究，尽可能跟C++版保持一致，容易跟上新版本就好。

使用前请仔细阅读文档。目前支持Linux和Mac OS（6.6.9及以上），尚不支持Windows系统。本人不对使用这套库的任何后果负责。

## 安装说明

克隆代码到本地
```
git clone git@github.com:keli/ctp-python.git
cd ctp-python
```

安装
```
python setup.py install
```

目前默认使用的是6.6.9版本。如果需要链接和使用其他版本，只需要以下两步，以6.3.13版为例:

1. 修改setup.py中的API_VER的值为'6.3.13'

2. 用swig重新生成一下源码，注意指向api目录中的相应版本目录

```
cd ctp-python
swig -python -py3 -c++ -threads -I./api/6.3.13 -o ctp_wrap.cpp ctp.i
python setup.py install
```

跑一下测试

```
pytest -s tests/test_trader.py --front=tcp://180.168.146.187:13030 --broker=<broker_id> --user=<investor_id> --password=<password> --app=<app_id> --auth=<auth_code>
```

## 其他事项

- 本项目中CTP返回的GBK编码字符串已经全部自动转换为UTF-8
- 市场数据中的极大值代表无数据，为可读性起见打印整个结构体时会显示为None
- 目前只支持了Python 3，测试环境Linux和M1 Mac

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

