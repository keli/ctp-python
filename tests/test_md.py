#!/usr/bin/env python
import ctp
import pytest
import sys
import time
import hashlib
import tempfile
import os, os.path
import threading


@pytest.fixture
def spi(front, broker, user, password):
    assert front and broker and user and password, "missing arguments"
    _spi = MdSpi(front, broker, user, password)
    th = threading.Thread(target=_spi.run)
    th.daemon = True
    th.start()
    secs = 5
    while secs:
        if not (_spi.connected and _spi.loggedin):
            secs -= 1
            time.sleep(1)
        else:
            break    
    return _spi


class MdSpi(ctp.CThostFtdcMdSpi):
    def __init__(self, front, broker_id, user_id, password):
        ctp.CThostFtdcMdSpi.__init__(self)

        self.front = front
        self.broker_id = broker_id
        self.user_id = user_id
        self.password = password

        self.request_id = 0
        self.connected = False
        self.loggedin = False
        self.subscribed = False
        self.data = None

        self.api = self.create()

    def create(self):
        dir = ''.join(('ctp', self.broker_id, self.user_id)).encode('UTF-8')
        dir = hashlib.md5(dir).hexdigest()
        dir = os.path.join(tempfile.gettempdir(), dir, 'Md') + os.sep
        if not os.path.isdir(dir): os.makedirs(dir)
        return ctp.CThostFtdcMdApi.CreateFtdcMdApi(dir)

    def run(self):
        self.api.RegisterSpi(self)
        self.api.RegisterFront(self.front)
        self.api.Init()        
        self.api.Join()

    def login(self):
        field = ctp.CThostFtdcReqUserLoginField()
        field.BrokerID = self.broker_id
        field.UserID = self.user_id
        field.Password = self.password
        self.request_id += 1
        self.api.ReqUserLogin(field, self.request_id)

    def OnFrontConnected(self):
        print("OnFrontConnected")
        self.connected = True
        self.login()

    def OnRspUserLogin(self, pRspUserLogin:'CThostFtdcRspUserLoginField', pRspInfo:'CThostFtdcRspInfoField', nRequestID:'int', bIsLast:'bool'):
        print("OnRspUserLogin", pRspInfo.ErrorID, pRspInfo.ErrorMsg)
        if pRspInfo.ErrorID == 0:
            self.loggedin = True

    def OnRspError(self, pRspInfo:'CThostFtdcRspInfoField', nRequestID:'int', bIsLast:'bool'):
        print("OnRspError:", pRspInfo.ErrorID, pRspInfo.ErrorMsg)

    def OnRspSubMarketData(self, pSpecificInstrument: 'CThostFtdcSpecificInstrumentField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        print("OnRspSubMarketData:", pRspInfo.ErrorID, pRspInfo.ErrorMsg)
        if pRspInfo.ErrorID == 0:
            self.subscribed = True

    def OnRtnDepthMarketData(self, pDepthMarketData: 'CThostFtdcDepthMarketDataField'):
        print("OnRtnDepthMarketData:", pDepthMarketData)
        self.data = pDepthMarketData            

    def __del__(self):
        self.api.RegisterSpi(None)
        self.api.Release()


def test_init(spi):
    assert spi.connected and spi.loggedin


def test_subscribe(spi, instrument, exchange):
    spi.api.SubscribeMarketData([instrument])
    secs = 5
    while secs:
        if not (spi.subscribed and spi.data):
            secs -= 1
            time.sleep(1)
        else:
            break    
    assert spi.subscribed and spi.data
