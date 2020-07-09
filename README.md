# ctp-python
穿透式监管版本CTP接口的Python封装


这套封装是本人在生产环境使用的。主要原因是其他作者经常弃坑，虽然封装得更好吧，但是动不动就不更新了。
考虑到一般在ctp之上还会有应用层的封装，也没必要做得太讲究，尽可能跟C++版保持一致，容易跟上新版本就好。

用前请仔细阅读文档。本人不对使用这套库的任何后果负责。

## 安装说明

克隆代码到本地
```
git@github.com:keli/ctp-python.git
cd ctp-python
```

安装
```
python setup.py install
```

目前默认使用的是6.3.15版本。如果需要链接和使用6.3.13版，需要加一点步骤:

1. 修改setup.py中的API_VER的值为'6.3.13'

2. 用swig重新生成一下源码

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
- 目前只支持了Python 3，测试环境Linux
- simnow已经启用6.3.15版本

## 常见问题

- 为什么报UTF-8和GBK的转码错误？

这个是内存管理的问题而不是转码的问题，ctp库会释放掉它传给你的回调函数的内容，当你打印的时候这块内存已经free掉了，所以就报转码失败了。这个最理想的处理是改swig定义来自动把相应的结构体内容拷到python，但是我还没太搞清楚怎么在swig中做这件事。我自己的代码里面需要缓存起来的ctp结构只有很少的几处，所以直接在用户代码中手动转成自己定义的python数据类型了。

## 有用的参考链接
- [什么是穿透式监管，需要投资者做什么](http://www.360doc.com/content/19/0514/11/8392_835597706.shtml) 
- [看完这篇，彻底搞定期货穿透式CTP API接入](https://www.vnpy.com/forum/topic/603-kan-wan-zhe-pian-che-di-gao-ding-qi-huo-chuan-tou-shi-ctp-apijie-ru)
