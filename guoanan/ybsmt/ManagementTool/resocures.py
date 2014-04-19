#!/user/bin/pythhon
# -*- encoding: UTF-8 -*-

import sys
import os
sys.path.append('/opt/ybs/etc/')
import ybsmtconfig
import operator
import YDI


def node_list():
	ybsmtconfig.logger.info('recourse.py node_list()')
	ret = ''
	data = []
	try:
		node_list = ybsmtconfig.YsnyServer.proxy_getnodelist()
		ybsmtconfig.logger.info('recourse.py node_list() return values node_list:%s',node_list)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_getnodelist() failed, the error information:%s',str(e))
		return ret, data
	if node_list['Head']==0:
		ybsmtconfig.logger.info('recourse.py node_list() return values success')
		data = node_list['Body']
		for i,d in enumerate(data):
			if d.has_key('Id'):
				d['Used'] = int(d['Used']) / (1024 * 1024)
				d['Used'] = str(d['Used']) + 'M'
				d['Size'] = int(d['Size']) / (1024 * 1024 * 1024)
				d['Size'] = str(d['Size']) + 'G'
				d['Id'] = str(i)
			else:
				t = {}
				t['status'] = d['status']
				t['IP'] = d['IP']
				t['Used'] = '-'
				t['Id'] = str(i)
				t['Size'] = '-'
				data[i] = t
		if len(data)==0:
			return ret, data
		return ret, data
		
	else:
		ret = YDI.error_code(node_list['Head'])
		ybsmtconfig.logger.info('recourse.py node_list() error_code:%s',data)
		return ret, data

def add_node(ip):
	ybsmtconfig.logger.info('recourse.py add_node() node_ip:%s',ip)
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_addnode(ip)
		ybsmtconfig.logger.info('recourse.py add_node() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_addnode() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0:
		ret = (u'增加节点成功')
		result = 'success'
		ybsmtconfig.logger.info('recourse.py add_node() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('recourse.py add_node() error_code:%s',ret)
	return ret, result

def charge_ip(ip):
	str = os.popen('ifconfig').read()
	sindex='inet addr:'
	while str.find(sindex) != -1:
		str = str[str.find(sindex)+len(sindex):]
		str_IP = str[:str.find(' ')]
		str = str[str.find(' '):]
		if str_IP == ip:
			return 1
	return 0

def change_node(ip, staus):
	ret=''
	result = 'failed'
	temp = charge_ip(ip)
	if temp:
		ret = (u'禁止改变控制节点状态')
		return ret, result
	if staus=="online":
		ybsmtconfig.logger.info('recourse.py change_node() node_ip:%s node_status',ip,staus)
		try:
			ret = ybsmtconfig.YsnyServer.proxy_setnodeoffline(ip)
			ybsmtconfig.logger.info('recourse.py change_node() return value:%s',ret)
		except Exception, e:
			ret = (u'YSNY连接异常')
			ybsmtconfig.logger.critical('Connect proxy_setnodeoffline() failed, the error information:%s', str(e))
			return ret, result
		if ret == 0:
			try:
				node_list = []
				node_list.append(ip)
				ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_delete_node(node_list)
				ybsmtconfig.logger.info('recourse.py change_node() return value:%s',ret)
			except Exception, e:
				ret = (u'YSNY连接成功，YMAS连接失败')
				return ret, result
			if ret == 0:
				ret = (u'节点下线成功')
				result = 'success'
				ybsmtconfig.logger.info('recourse.py change_node() %s', ret)
			else:
				ret = YDI.error_code(ret)
				ybsmtconfig.logger.info('recourse.py change_node() error_code:%s',ret)
			return ret, result
		else:
			ret = YDI.error_code(ret)
			ybsmtconfig.logger.info('recourse.py change_node() error_code:%s',ret)
		return ret, result
	elif staus=="offline":
		ybsmtconfig.logger.info('recourse.py change_node() node_ip:%s node_status',ip,staus)
		try:
			ret = ybsmtconfig.YsnyServer.proxy_setnodeonline(ip)
			ybsmtconfig.logger.info('recourse.py change_node() return value:%s',ret)
		except Exception, e:
			ret = (u'YSNY连接异常')
			ybsmtconfig.logger.critical('Connect proxy_setnodeonline() failed, the error information:%s', str(e))
			return ret, result
		if ret == 0:
			try:
				node_list = []
				node_list.append(ip)
				ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_add_node(node_list)
				ybsmtconfig.logger.info('recourse.py change_node() return value:%s',ret)
			except Exception, e:
				ret = (u'YSNY连接成功，YMAS连接失败')
				return ret, result
			if ret == 0:
				ret = (u'节点上线状态成功')
				result = 'success'
				ybsmtconfig.logger.info('recourse.py change_node() %s', ret)
			else:
				ret = YDI.error_code(ret)
				ybsmtconfig.logger.info('recourse.py change_node() error_code:%s',ret)
			return ret, result
		else:
			ret = YDI.error_code(ret)
			ybsmtconfig.logger.info('recourse.py change_node() error_code:%s',ret)
		return ret, result

def delete_node(ip):
	ybsmtconfig.logger.info('recourse.py delete_node() node_ip:%s',ip)
	result = 'failed'
	print 'def delete_node(ip):'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_deletenode(ip)
		ybsmtconfig.logger.info('recourse.py proxy_deletenode() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_deletenode() failed, the error information:%s', str(e))
		return ret, result
	if ret == 0:
		ret = (u'删除节点成功')
		result = 'success'
		ybsmtconfig.logger.info('recourse.py delete_node success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('recourse.py delete_node() error_code:%s',ret)
	return ret, result


def zone_info():
	ybsmtconfig.logger.info('target.py zone_info()')
	ret = ''
	result = []
	try:
		zone = ybsmtconfig.YsnyServer.proxy_showzoneinfo()
		ybsmtconfig.logger.info('target.py proxy_showzoneinfo() zone:%s',zone)
	except Exception, e:
		ret = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('Connect proxy_showzoneinfo() failed, the error information:%s',str(e))
		return ret, result
	if zone['Head'] == 0:
		ybsmtconfig.logger.info('target.py proxy_showzoneinfo() success')
		if len(zone['Body'])==0:
			ret = (u'当前不存在节点区域配置信息！')
			ybsmtconfig.logger.info('target.py proxy_showzoneinfo() no information!')
	else:
		ret = YDI.error_code(zone['Head'])
		ybsmtconfig.logger.error('target.py proxy_showzoneinfo() error_info:%s', ret)
	return ret, zone['Body']


def set_zone(node_id, node_ip, new_id):
	ybsmtconfig.logger.info('target.py set_zone() node_id=%s, node_ip=%s, new_id=%s', node_id, node_ip, new_id)
	ret = ''
	try:
		ret = ybsmtconfig.YsnyServer.proxy_setnodezone(node_id, node_ip, new_id)
		ybsmtconfig.logger.info('recourse.py add_node() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('Connect proxy_addnode() failed, the error information:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'区域配置成功！')
		ybsmtconfig.logger.info('recourse.py add_node() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('recourse.py add_node() error_code:%s',ret)
	return ret


def cache():
	ybsmtconfig.logger.info('recourse.py cache()')
	ret = ''
	result = []
	try:
		cache = ybsmtconfig.YsnyServer.proxy_showcacheinfo()
		ybsmtconfig.logger.info('target.py proxy_showcacheinfo() cache:%s',cache)
	except Exception, e:
		ret = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('Connect proxy_showcacheinfo() failed, the error information:%s',str(e))
		return ret, result
	if cache['Head'] == 0:
		ybsmtconfig.logger.info('target.py proxy_showcacheinfo() success')
		if len(cache['Body'])==0:
			ret = (u'当前不存在节点缓存配置信息！')
			ybsmtconfig.logger.info('target.py proxy_showcacheinfo() no information!')
		else:
			for c in cache['Body']:
				if c['cache_status'] == '1':
					c['cache_status'] = (u'开启')
				else:
					c['cache_status'] = (u'禁用')
	else:
		ret = YDI.error_code(cache['Head'])
		ybsmtconfig.logger.error('target.py proxy_showcacheinfo() error_info:%s', ret)
	return ret, cache['Body']


def cache_change(cache_info):
	ybsmtconfig.logger.info('recourse.py cache_change() %s', cache_info)
	ret = ''
	try:
		if cache_info['cache_status']:
			ret = ybsmtconfig.YsnyServer.proxy_opencache(cache_info['node_ip'], cache_info['cache_dir'], cache_info['cache_size'], cache_info['cache_flag'])
			ybsmtconfig.logger.info('recourse.py proxy_opencache() return values:%s',ret)
		else:
			ret = ybsmtconfig.YsnyServer.proxy_closecache(cache_info['node_ip'], cache_info['cache_dir'], cache_info['cache_size'], cache_info['cache_flag'])
			ybsmtconfig.logger.info('recourse.py proxy_closecache() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('Connect proxy_closecache() failed, the error information:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'缓存配置成功！')
		ybsmtconfig.logger.info('recourse.py cache_change() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('recourse.py cache_change() error_code:%s',ret)
	return ret


def shutdown_cluster():
	ybsmtconfig.logger.info('recourse.py close_cluster()')
	try:
		ret = ybsmtconfig.YsnyServer.proxy_shutdowncluster()
		ybsmtconfig.logger.info('recourse.py proxy_shutdowncluster() return values:%s', ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_deletenode() failed, the error information:%s', str(e))
		return ret
	if ret == 0:
		ret = (u'关闭集群成功')
		ybsmtconfig.logger.info('recourse.py shut down cluster success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('recourse.py proxy_shutdowncluster() error_code:%s',ret)
	return ret


if __name__ == '__main__' :
	ret = ybsmtconfig.YsnyServer.proxy_addnode('ip')
	print ret
	#node_list()
