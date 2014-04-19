import ybsmtlog
import xmlrpclib
Ip_Port = "http://192.168.4.233:8000"
client = xmlrpclib.ServerProxy(Ip_Port)
import operator
import YDI


def node_list():
    ybsmtlog.logger.info('recourse.py node_list()')
    try:
        print "start"
        node_list = client.proxy_getnodelists()
        print "end"
        ybsmtlog.logger.info('recourse.py node_list() return values node_list:%s',node_list)
    except Exception, e:
		ret = (u'YSNY连接异常')
        print data
        ybsmtlog.logger.critical('Connect proxy_getnodelist() failed, the error information:%s',str(e))
        return data



if __name__ == '__main__' :
    node_list()
