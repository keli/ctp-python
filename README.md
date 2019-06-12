# ctp-python
穿透式监管版本CTP接口的Python封装

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

目前默认使用的是6.3.13版本。如果需要链接和使用6.3.15版，需要加一点步骤:

1. 修改setup.py中的API_VER的值为'6.3.15'

2. 用swig重新生成一下源码

```
cd ctp-python
swig -python -py3 -c++ -threads -I./api/6.3.15 -o ctp_wrap.cpp ctp.i
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
- 目前只在simnow上的终端厂商测试环境测通了trader。
- simnow以及大部分券商的测试环境是用的6.3.13版本，版本不同将无法调用OnFrontConnected。
- simnow的终端厂商测试环境只能测一下trader登录，其他的功能都没有。

## 有用的参考链接
- [公告：SIMNOW平台将开启终端厂商穿透测试环境](http://www.simnow.com.cn/notification/id/32.action)
- [什么是穿透式监管，需要投资者做什么](http://www.360doc.com/content/19/0514/11/8392_835597706.shtml) 
- [看完这篇，彻底搞定期货穿透式CTP API接入](https://www.vnpy.com/forum/topic/603-kan-wan-zhe-pian-che-di-gao-ding-qi-huo-chuan-tou-shi-ctp-apijie-ru)
