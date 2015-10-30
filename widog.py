# -*- coding:utf-8 -*-

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")
from collections import OrderedDict

import iw_parse
import sqlite3
import os
import requests

DB_FILE = 'widog.db'
########################################################################

########################################################################
class open_wifi:
    """管理开放wifi"""
    
    cache = OrderedDict()
    max_count = 1000
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
    def add(self,ssid,mac='n'):
        self.ssid = ssid
        if len(self.cache) >= self.max_count:
            self.reduce()
        if not self.cache.get(ssid):
            self.cache[ssid] = [len(self.cache),0,mac]
            #wifi信息中，含义为【信息编号，处理状态（0：未连接过），mac地址】
            self.conn(ssid)#连接开放wifi
        else:#缓存中已有，则不再重复添加
            pass
    def reduce(self):
        '''缓存满载时，清除前100条记录'''
        keys = self.cache.keys()
        for i in range(100):
            del self.cache[keys[i]]
    def conn(self,ssid):
        if  self.cache[self.ssid][1]  == 0 :
            os.popen('nmcli d disconnect wlan2')
            conn_cmd = 'nmcli device wifi connect "{0}"'.format(ssid)
            print conn_cmd,'连接wifi'
            cmd_echo =  os.popen(conn_cmd).read()
            if 'activated' in cmd_echo:#连接成功
                self.getportal()
                self.cache[self.ssid][1]  = 1
            
    def getportal(self):
        res  = requests.get('http://www.baidu.com')
        if '百度一下' in res.content:
            print '未发现portal'
        else :
            print self.ssid ,'发现portal'
            self.callworker()
        
        #print res.content
        pass
    def callworker(self):
        '''以某种方式通知采集人员'''
        pass
class widog_db:
    """widog数据库操作"""
    cur = None
    conn = None    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        #if not os.path.exists(DB_FILE):
            #self.crt_db()
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()
        self.conn.text_factory = str    
        self.crt_db()
        
    
    def crt_db(self):
        CRT_TAB = '''
            CREATE TABLE IF NOT EXISTS "wifi" (
                    "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    "ssid"  TEXT,
                    "mac"  TEXT NOT NULL ,
                    "encrypt"  TEXT,
                    "signal"  TEXT,
                    "channel"  TEXT,
                    "quality"  TEXT,
                    "longitude" TEXT,
                    "latitude" TEXT,
                    "time" TEXT,
                    "ext"  TEXT
                    );
        '''
        self.cur.execute(CRT_TAB)
        pass
    def upt_db(self,wifi_info):
        INS_STR = '''INSERT INTO wifi (ssid,mac,encrypt,signal,channel,quality) VALUES(?,?,?,?,?,?);'''
        SIG_STR = '''select id,signal from wifi where mac = ? ;'''
        UPT_STR = '''update wifi set ssid=?,mac=?,encrypt=?,signal=?,channel=?,quality=?  where id = ?;'''
        res = self.cur.execute(SIG_STR,(wifi_info[1],)).fetchone()
        #res_info =  self.cur
        crt_ssid = wifi_info[0].strip()
        if wifi_info[2].strip() == 'Open' and crt_ssid:
            print '报告老板！发现开放wifi：',crt_ssid
           
            
            open_wifi_cache.add(crt_ssid,wifi_info[1])
            #print str(open_wifi_cache.cache)
        if res:#数据库中已有存储记录
            old_id = res[0]
            old_sig = res[1]
            print '更新',wifi_info
            if int(old_sig) < int(wifi_info[3]):#信号增强，更新信息
                wifi_info.append(old_id)
                self.cur.execute(UPT_STR,wifi_info)
        else:
            print '添加：',wifi_info
            self.cur.execute(INS_STR,wifi_info)
        self.conn.commit()

def main(iterface = 'wlan2'):
    networks = iw_parse.get_interfaces(interface='wlan2')
    for net in  networks:
        ssid =  net.get('Name')
        mac_addr = net.get('Address')
        encrypt  = net.get('Encryption')
        signal  = net.get('Signal Level')[:-4]
        quality = net.get('Quality')
        channel = net.get('Channel')
        wifi_info = [ssid,mac_addr,encrypt,signal,channel,quality]
        db.upt_db(wifi_info)
        #print ssid ,mac_addr,signal,quality,channel,encrypt
        #print mac_addr,'\t',ssid


if __name__ == '__main__':
    print 'widog starting...'
    #print '\xE5\xB0\x8F\xE4\xBA\x91\xE4\xBA\x91'
    
    open_wifi_cache = open_wifi()
    db = widog_db()
    
    main()