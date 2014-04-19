#!/user/bin/python
# -*- encoding: UTF-8 -*-

import sys
sys.path.append('/opt/ybs/etc')
#import ybsmtconfig as ybsmtconfig
import ybsmtconfig
import xmlrpclib
import YDI

#Ip_Port = "http://192.168.4.235:8080"
# = xmlrpclib.ServerProxy(Ip_Port)

def monitor_node():
	data = ''
	ybsmtconfig.logger.info('monitor_test.py monitor_node()')
	try:
		ybsmtconfig.logger.debug('monitor_test.py monitor_inquire_online_list()')
		data = ybsmtconfig.MonitorServer.serverrpcser.monitor_inquire_online_list()
		#print data
		ybsmtconfig.logger.debug('monitor_test.py monitor_inquire_online_list() return vales:%s',data)
		if data['head']==0:
			HOST = data['body']
			ybsmtconfig.logger.debug('serverrpcser.monitor_inquire_nodes() HOST:%s',HOST)
			ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_inquire_nodes(HOST)
			#print ret
			ybsmtconfig.logger.debug('serverrpcser.monitor_inquire_nodes() return values:%s', ret)
			if ret['head']==0:
				data = []
				for t in ret['body']:
					node = {}
					node['ip'] = t['ip']
					node['disk'] = {}
					node['disk']['total'] = str('%.2f' % t['disk']['total']) + 'G'
					node['disk']['used'] = str('%.2f' % t['disk']['used']) + 'G'
					node['disk']['percent'] = str('%.2f' % (100 * t['disk']['used'] / t['disk']['total'])) + '%'
					node['cpu'] = str('%.2f' % t['cpu']) + '%'
					node['memory'] = str('%.2f' % (100 * t['mem']['used'] / t['mem']['total'])) + '%'
					data.append(node)
				ybsmtconfig.logger.info('Get node list successfully!')
				return data
			else:
				data = YDI.error_code(ret['head'])
				ybsmtconfig.logger.error('Failed to get node information, error information:%s', data)
				return data
		else:
			data = YDI.error_code(data['head'])
			ybsmtconfig.logger.error('Failed to get online list, error information:%s', data)
			return data
	except Exception, e:
		data = (u'YMAS连接异常')
		ybsmtconfig.logger.critical('Connect serverrpcser.monitor_inquire_nodes() failed, the error information:%s', str(e))
		return data


def monitor_cluster():
	ybsmtconfig.logger.info('monitor_test.py monitor_cluster()')
	#data = []
	try:
		ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_inquire_cluster()
		ybsmtconfig.logger.info('serverrpcser.monitor_inquire_cluster() return values:%s',ret)
	except Exception, e:
		data = (u'YMAS连接异常')
		print str(e)
		ybsmtconfig.logger.critical('Connect ybsmtconfig.MonitorServerxy_getlulist() failed, the error information:%s',str(e))
		return data
	if ret['head']==0:
		d = {}
		d['cpu'] = str('%.2f' % ret['body']['cpu']) + '%'
		d['mem_used'] = str('%.2f' % ret['body']['mem_used']) + 'G'
		d['num'] = str(ret['body']['num'])
		d['disk_total'] = str('%.2f' % ret['body']['disk_total']) + 'G'
		d['disk_used'] = str('%.2f' % ret['body']['disk_used']) + 'G'
		d['percent'] = str('%.2f' % (100 * ret['body']['disk_used'] / ret['body']['disk_total'])) + '%'
		data = []
		data.append(d)
		ybsmtconfig.logger.info('Get cluster information successfully!')
		return data
	else:
		data = YDI.error_code(ret['head'])
		ybsmtconfig.logger.error('Failed to get cluster information, error information:%s', data)
		return data


if __name__ == '__main__' :
	ret = monitor_node()
	#aa = monitor_cluster()
	#print aa
	print ret