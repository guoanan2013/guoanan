#!/user/bin/python
# -*- encoding: UTF-8 -*-


import sys
import xmlrpclib
sys.path.append('/opt/ybs/etc/')
#import ybsmtconfig as ybsmtconfig
import ybsmtconfig
import operator
import YDI


#Ip_Port1 = "http://192.168.4.235:8000"
#ybsmtconfig.YsnyServer = xmlrpclib.ServerProxy(Ip_Port1)

def target_list():
	ybsmtconfig.logger.info('target.py target_list()')
	ret = ''
	lu_list = []
	try:
		lu_list = ybsmtconfig.YsnyServer.proxy_getlulist()
		ybsmtconfig.logger.info('target.py target_list() return values target_list:%s',lu_list)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_getlulist() failed, the error information:%s',str(e))
		return ret, lu_list
	if lu_list['Head']==0:
		ybsmtconfig.logger.info('target.py target_list() success')
	else:
		ret = YDI.error_code(lu_list['Head'])
		ybsmtconfig.logger.error('target.py target_list() target_list error:%s',ret)
	return ret, lu_list['Body']


def get_online_targetip():
	ybsmtconfig.logger.info('target.py get_online_targetip()')
	ret = ''
	targetip = []
	try:
		temp_targetip = ybsmtconfig.YsnyServer.cluster_iplist()
		ybsmtconfig.logger.info('target.py cluster_iplist() return values online target ip:%s', targetip)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect cluster_iplist() failed, the error information:%s',str(e))
		return ret, targetip
	for ip in temp_targetip:
		temp = {}
		temp['ip'] = ip
		targetip.append(temp)
	return ret, targetip


def target_tails(lu_name,lu_ip):
	ybsmtconfig.logger.info('target.py target_tails() lu_name:%s lu_ip:%s',lu_name,lu_ip)
	ret = ''
	lu_details_temp = {'initiator_blacklist':{}, 'lun_info':{}, 'lu_info':{}}
	try:
		lu_details = ybsmtconfig.YsnyServer.proxy_getludetails(lu_name,lu_ip)
		ybsmtconfig.logger.info('target.py target_tails() return values lu_details:%s',lu_details)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_getludetails() failed, the error information:%s',str(e))
		return ret, lu_details_temp
	if lu_details['Head'] == 0:
		if lu_details['Body'].has_key('lu_info'):
			temp = lu_details['Body']['lu_info'][0]
			lu_details['Body']['lu_info'] = temp
		ybsmtconfig.logger.info('target.py target_tails() success')
		return ret, lu_details['Body']
	else:
		ret = YDI.error_code(lu_details['Head'])
		ybsmtconfig.logger.error('target.py target_tails() error_info:%s',ret)
		return ret, lu_details_temp

def onlineloder_list(lu_name,lu_ip):
	ybsmtconfig.logger.info('target.py onlineloder_list() lu_name:%s lu_ip:%s',lu_name,lu_ip)
	ret = ''
	result = []
	try:
		onlineloder_list = ybsmtconfig.YsnyServer.proxy_getinitiatoronlinelist(lu_name,lu_ip)
		ybsmtconfig.logger.info('target.py onlineloder_list() onlineloder_list:%s',onlineloder_list)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_getinitiatoronlinelist() failed, the error information:%s',str(e))
		return ret, result
	if onlineloder_list['Head'] == 0:
		ybsmtconfig.logger.info('target.py onlineloder_list() success')
		if len(onlineloder_list['Body'])==0:
			ret = 'There is no onlineloder information!'
			ybsmtconfig.logger.info('target.py onlineloder_list() no onlineloder')
	else:
		ret = YDI.error_code(lu_list['Head'])
		ybsmtconfig.logger.error('target.py onlineloder_list() error_info:%s', ret)
	return ret, onlineloder_list['Body']

def add_lun(addlun_info):
	ybsmtconfig.logger.info('target.py add_lun() addlun_info:%s', addlun_info)
	ret = ''
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_addlun(addlun_info['lu_name'],addlun_info['lun_info'],addlun_info['lu_ip'])
		print ret
		ybsmtconfig.logger.info('target.py add_lun() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_addlun() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0:
		ret = (u'增加LUN成功')
		result = 'success'
		ybsmtconfig.logger.info('target.py add_lun() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py add_lun() error_info:%s',ret)
	return ret, result

def delete_lun(deletelun_info):
	ybsmtconfig.logger.info('target.py delete_lun() deletelun_info:%s', deletelun_info)
	ret = ''
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_deletelun(deletelun_info['lu_name'],deletelun_info['lunname_info'],deletelun_info['lu_ip'])
		ybsmtconfig.logger.info('target.py delete_lun() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_deletelun() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0:
		ret = (u'删除LUN成功')
		result = 'success'
		ybsmtconfig.logger.info('target.py delete_lun() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py delete_lun() delete_info:%s',ret)
	return ret, result


def set_setipfilter(ipfilterinfo):
	ret = ybsmtconfig.YsnyServer.proxy_setipfilter('success','192.168.4.68','192.168.4.0/24')
	return ret

def addlu(lu_info, lun_info, black_info):
	ybsmtconfig.logger.info('target.py addlu() lu_info:%s lun_info:%s black_info:%s',lu_info,lun_info,black_info)
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_addlu(lu_info['lu_name'],lu_info['lu_ip'],lu_info['chap_name'],lu_info['selvalue'],lun_info,lu_info['lu_passwd'],black_info)
		ybsmtconfig.logger.info('target.py addlu() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_addlu() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0:
		ret = (u'增加LU成功')
		result = 'success'
		ybsmtconfig.logger.info('target.py addlu() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.critical('Connect proxy_addlu() failed, the error information:%s', ret)
	return ret, result

def delete_lu(lu_name,lu_ip):
	ybsmtconfig.logger.info('target.py delete_lu() lu_name:%s lu_ip:%s',lu_name,lu_ip)
	ret = ''
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_deletelu(lu_name,lu_ip)
		ybsmtconfig.logger.info('target.py delete_lu() return values:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_delete_lu() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0 :
		ret = (u'删除LU成功')
		result = 'success'
		ybsmtconfig.logger.info('target.py delete_lu() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py delete_lu() error_code:%s',ret)
	return ret, result

def delete_black(lu_name,black_name,lu_ip):
	ybsmtconfig.logger.info('target.py delete_black() lu_name:%s,black_name:%s,lu_ip:%s',lu_name,black_name,lu_ip)
	ret = ''
	try:
		ret = ybsmtconfig.YsnyServer.proxy_delinitiator_blacklist(lu_name,black_name,lu_ip)
		ybsmtconfig.logger.info('target.py delete_black() lu_name:%s,black_name:%s,lu_ip:%s return values:%s',lu_name,black_name,lu_ip,ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('target.py delete_black() Exception:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'删除黑名单成功')
		ybsmtconfig.logger.info('target.py delete_black() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py delete_black() error_code:%s',ret)
	return ret

def add_black(lu_name,black_name,lu_ip):
	ybsmtconfig.logger.info('target.py add_black() lu_name:%s,black_name:%s,lu_ip:%s',lu_name,black_name,lu_ip)
	ret = ''
	try:
		ret = ybsmtconfig.YsnyServer.proxy_addinitiator_blacklist(lu_name,black_name,lu_ip)
		ybsmtconfig.logger.info('target.py add_black() lu_name:%s,black_name:%s,lu_ip:%s return values:%s',lu_name,black_name,lu_ip,ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('target.py add_black() Exception:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'增加黑名单成功')
		ybsmtconfig.logger.info('target.py add_black() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py add_black() error_code:%s',ret)
	return ret
	
	
def recover_target_list(src_ip,des_ip):
	ybsmtconfig.logger.info('target.py recover_target_list() src_ip:%s,des_ip:%s',src_ip,des_ip)
	ret = ''
	try:
		ret = ybsmtconfig.YsnyServer.proxy_recoverlulist(src_ip,des_ip)
		ybsmtconfig.logger.info('target.py proxy_recoverlulist() src_ip:%s,des_ip:%s return values:%s',src_ip,des_ip,ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('target.py proxy_recoverlulist()  Exception:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'恢复节点目标器成功')
		ybsmtconfig.logger.info('target.py proxy_recoverlulist() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py proxy_recoverlulist() error_code:%s',ret)
	return ret
	
	
def modify_ip_chap(lu_name, lu_ip, new_chap, chap_name):
	ybsmtconfig.logger.info('target.py modify_ip_chap() lu_name:%s, lu_ip:%s, new_chap:%s, chap_name:%s',lu_name, lu_ip, new_chap, chap_name)
	ret = ''
	try:
		ret = ybsmtconfig.YsnyServer.proxy_modifyipchap(lu_name,lu_ip,chap_name,new_chap)
		ybsmtconfig.logger.info('target.py proxy_modifyipchap() return value:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('target.py proxy_modifyipchap()  Exception:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'修改目标器口令成功')
		ybsmtconfig.logger.info('target.py proxy_modifyipchap() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py proxy_modifyipchap() error_code:%s',ret)
	return ret


def iscsi_service():
	ybsmtconfig.logger.info('target.py iscsi_service()')
	ret = ''
	result = []
	try:
		iscsi_list = ybsmtconfig.YsnyServer.proxy_showiscsi()
		ybsmtconfig.logger.info('target.py iscsi_service() iscsi_list:%s',iscsi_list)
	except Exception, e:
		ret = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('Connect iscsi_service() failed, the error information:%s',str(e))
		return ret, result
	if iscsi_list['Head'] == 0:
		ybsmtconfig.logger.info('target.py iscsi_service() success')
		if len(iscsi_list['Body'])==0:
			ret = (u'当前不存在iSCSI在线加载器列表！')
			ybsmtconfig.logger.info('target.py iscsi_service() no onlineloder')
		else:
			for list in iscsi_list['Body']:
				if list['tgt_status'] == '1':
					list['tgt_status'] = (u'启动')
				else:
					list['tgt_status'] = (u'停止')
	else:
		ret = YDI.error_code(lu_list['Head'])
		ybsmtconfig.logger.error('target.py iscsi_service() error_info:%s', ret)
	return ret, iscsi_list['Body']


def iscsi_service_exchange(lu_ip, tgt_status):
	ybsmtconfig.logger.info('target.py iscsi_service_exchange() lu_ip=%s, tgt_status=%s', lu_ip, tgt_status)
	ret = ''
	try:
		if tgt_status:
			ret = ybsmtconfig.YsnyServer.proxy_stoptarget(lu_ip)
			ybsmtconfig.logger.info('target.py proxy_stoptarget() return value:%s',ret)
		else:
			ret = ybsmtconfig.YsnyServer.proxy_starttarget(lu_ip)
			ybsmtconfig.logger.info('target.py proxy_starttarget() return value:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('target.py proxy_stoptarget()  Exception:%s',str(e))
		return ret
	if ret == 0:
		ret = (u'修改目标器服务状态成功！')
		ybsmtconfig.logger.info('target.py proxy_stoptarget() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.error('target.py proxy_stoptarget() error_code:%s',ret)
	return ret

#proxy_starttarget(lu_ip)
#proxy_stoptarget(lu_ip)


if __name__ == '__main__' :

	ret = target_list()
	print ret
	print dir(ybsmtconfig)

	#lu_list=ybsmtconfig.YsnyServer.proxy_getlulist()
	#print lu_list()
	#ret=target_list()
	#print ret
