#!/user/bin/python
# -*- encoding: UTF-8 -*-

import sys
#import xmlrpclib
sys.path.append('/opt/ybs/etc')
import ybsmtconfig
import time
import MySQLdb
from datetime import datetime

import operator
import YDI

#database setting message
db = {}
db['host'] = 'localhost'
db['user'] = 'root'
db['passwd'] = '1'
db['charset'] = 'utf8'



HOST=[]
HOST.append('192.168.4.74')
HOST.append('192.168.4.73')

h1=['192.168.4.75']

h2=['192.168.4.74']

alarm_ip = []

def save_alarm_setting(cpu, mem, disk):
	ybsmtconfig.logger.info('alarm.py alarm_setting() cpu:%s mem:%s disk:%s', cpu, mem, disk)
	try:
		ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_save_alarm_setting(cpu, mem, disk)
		ybsmtconfig.logger.info('Get return value ret:%s', ret)
	except Exception, e:
		data = (u'YMAS连接异常！')
		ybsmtconfig.logger.critical('Connect serverrpcser.monitor_save_alarm_setting() failed, the error information:%s', str(e))
		return data
	if ret == 0:
		data = (u'保存报警配置成功！')
		ybsmtconfig.logger.info('Save alarm setting successfully!')
	else:
		data = YDI.error_code(ret)
		ybsmtconfig.logger.error('Failed to save alarm setting, error information is %s', data)
	return data



def save_alarm_email_test(smtp_server_addr, smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr, email_topic):
	ybsmtconfig.logger.info('alarm.py save_alarm_email() mtp_server_addr:%s, smtp_server_username:%s, smtp_server_password:%s, send_email_addr:%s, recv_email_addr:%s, topic:%s', smtp_server_addr, smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr, email_topic)
	try:
		ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_save_alarm_email(smtp_server_addr,smtp_server_username,smtp_server_password,send_email_addr,recv_email_addr, email_topic)
		ybsmtconfig.logger.info('Get return value ret:%s', ret)
	except Exception, e:
		data = (u'YMAS连接异常！')
		ybsmtconfig.logger.critical('Connect serverrpcser.monitor_save_alarm_email() failed, the error information:%s', str(e))
		return data
	if ret == 0:
		ybsmtconfig.logger.info('Save alarm email successfully!')
		data = (u'保存报警邮件信息成功！')
		return data
	else:
		data = YDI.error_code(ret)
		ybsmtconfig.logger.error('Failed to save alarm email, error information is %s', data)
		return data


def test_email(smtp_server_addr, smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr, email_topic, email_content):
	ybsmtconfig.logger.info('alarm.py test_email() smtp_server_addr:%s, smtp_server_username:%s, smtp_server_password:%s, send_email_addr:%s, recv_email_addr:%s, topic:%s, email_content:%s',smtp_server_addr, smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr, email_topic, email_content)
	try:
		ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_test_alarm_email(smtp_server_addr, smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr, email_topic, email_content)
		ybsmtconfig.logger.info('Get return values ret:%s', ret)
	except Exception, e:
		data = (u'YMAS连接异常！')
		ybsmtconfig.logger.critical('Connect serverrpcser.monitor_test_alarm_email() failed, the error information:%s', str(e))
		return data
	if ret == 'S':
		ybsmtconfig.logger.info('Test alarm email successfully!')
		data = (u'发送邮件成功！')
		return data
	else:
		data = (u'发送邮件失败，请确认邮件配置或尝试重新发送！')
		ybsmtconfig.logger.error('Failed to test alarm email!')
		return data


def get_T_AlarmRecords():
	global db, alarm_ip
	ret = ''
	alarm_records = []
	alarm_ip = []
	
	ybsmtconfig.logger.info('Get alarm records from YBSDataBase.T_AlarmRecords in database!')
	try:
		cxn = MySQLdb.connect(host = db['host'], user = db['user'], passwd = db['passwd'], charset = db['charset'])
		cxn.select_db('YBSDataBase')
		cur = cxn.cursor()
		cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords")
		#select * from  T_AlarmRecords WHERE triggerTm LIKE'2013-10-28%';
		temp = cur.fetchall()
		for t in temp:
			#print t
			record = {}
			record['AlarmID'] = t[0]
			record['triggerTm'] = t[2]
			record['NodeAddress'] = t[1]
			record['emailContent'] = t[12]
			record['state'] = (u'已处理')
			record['pickTm'] = t[14]
			if record['pickTm'] is None:
				record['state'] = (u'未处理')
			if alarm_ip.count(record['NodeAddress']) is 0:
				alarm_ip.append(record['NodeAddress'])
			#print t[2]
			#print t[12]
			alarm_records.append(record)
		ybsmtconfig.logger.info('Get alarm records from YBSDataBase.T_AlarmRecords:%s', alarm_records)
	except MySQLdb.Error, e:
		ybsmtconfig.logger.critical('Mysql Error %d: %s', e.args[0], e.args[1])
		ret = (u'数据库连接异常')
	cxn.close()
	cur.close()
	return ret, alarm_records, alarm_ip


def search_T_AlarmRecords(search_ip, search_date_start, search_context, search_date_end, search_status):
	global db, alarm_ip
	ret = ''
	alarm_records = []
	search_status = str(search_status)
	ybsmtconfig.logger.info('search alarm records from YBSDataBase.T_AlarmRecords in database!')
	try:
		cxn = MySQLdb.connect(host = db['host'], user = db['user'], passwd = db['passwd'], charset = db['charset'])
		cxn.select_db('YBSDataBase')
		cur = cxn.cursor()
		if search_ip is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords WHERE NodeAddress=%s", search_ip)
		if search_date_start is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords WHERE triggerTm LIKE%s", search_date_start)
		if search_context is not '%':
			search_context = 'Alarm(' + str(search_context) + ')' + '%'
			cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords WHERE emailContent LIKE%s", search_context)
		if search_date_end is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords WHERE pickTm LIKE%s", search_date_end)
		if search_status is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords")
		#cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords WHERE %s LIKE %s AND %s LIKE %s AND %s LIKE %s", 'NodeAddress', search_ip, 'triggerTm', search_date_start, 'pickTm', search_date_end)
		#select * from  T_AlarmRecords WHERE triggerTm LIKE'2013-10-28%';
		temp = cur.fetchall()
		for t in temp:
			#print t
			record = {}
			record['AlarmID'] = t[0]
			record['triggerTm'] = t[2]
			record['NodeAddress'] = t[1]
			record['emailContent'] = t[12]
			record['state'] = (u'已处理')
			state = '1'
			record['pickTm'] = t[14]
			if record['pickTm'] is None:
				record['state'] = (u'未处理')
				state = '0'
			if state is search_status or search_status is '%':
				alarm_records.append(record)
			print record
			#print t[2]
			#print t[12]
		ybsmtconfig.logger.info('Search alarm records from YBSDataBase.T_AlarmRecords:%s', alarm_records)
	except MySQLdb.Error, e:
		ybsmtconfig.logger.critical('Mysql Error %d: %s', e.args[0], e.args[1])
		ret = (u'数据库连接异常！')
	cxn.close()
	cur.close()
	return ret, alarm_records, alarm_ip


def handle_T_AlarmRecords(AlarmID):
	global db, alarm_ip
	ret = ''
	alarm_records = []
	alarm_ip = []
	
	ybsmtconfig.logger.info('Handle alarm records from YBSDataBase.T_AlarmRecords in database!')
	try:
		cxn = MySQLdb.connect(host = db['host'], user = db['user'], passwd = db['passwd'], charset = db['charset'])
		cxn.select_db('YBSDataBase')
		cur = cxn.cursor()
		cur.execute("UPDATE T_AlarmRecords SET pickTm=now() WHERE AlarmID=%s", AlarmID)
		temp = cur.fetchall()
		cxn.commit()
		print temp
		#select * from  T_AlarmRecords WHERE triggerTm LIKE'2013-10-28%';
		cur.execute("SELECT * FROM YBSDataBase.T_AlarmRecords")
		temp = cur.fetchall()
		for t in temp:
			#print t
			record = {}
			record['AlarmID'] = t[0]
			record['triggerTm'] = t[2]
			record['NodeAddress'] = t[1]
			record['emailContent'] = t[12]
			record['state'] = (u'已处理')
			record['pickTm'] = t[14]
			if record['pickTm'] is None:
				record['state'] = (u'未处理')
			if alarm_ip.count(record['NodeAddress']) is 0:
				alarm_ip.append(record['NodeAddress'])
			#print t[2]
			#print t[12]
			alarm_records.append(record)
		ybsmtconfig.logger.info('Get alarm records from YBSDataBase.T_AlarmRecords:%s', alarm_records)
	except MySQLdb.Error, e:
		ybsmtconfig.logger.critical('Mysql Error %d: %s', e.args[0], e.args[1])
		ret = (u'数据库连接异常！')
	cxn.close()
	cur.close()
	return ret, alarm_records, alarm_ip


def get_alarm_setting():
	ybsmtconfig.logger.info('alarm_test.py get_alarm_setting()')
	try:
		print sys.path
		ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_get_alarm_setting()
		ybsmtconfig.logger.info('alarm_test.py get_alarm_setting() return values:%s',ret)
	except Exception, e:
		ybsmtconfig.logger.info('alarm_test.py get_alarm_setting() return values:%s',str(e))
		print e
		data = (u'YMAS连接异常！')
		return data
	if ret['head'] == 0:
		setting = ret['body']
		for t in setting:
			if setting[t]['status'] == 1:
				setting[t]['status'] = 'checked'
			else:
				setting[t]['status'] = ''
			if setting[t]['popwin'] == 1:
				setting[t]['popwin'] = 'checked'
			else:
				setting[t]['popwin'] = ''
			if setting[t]['sendemail'] == 1:
				setting[t]['sendemail'] = 'checked'
			else:
				setting[t]['sendemail'] = ''
			if setting[t]['voice'] == 1:
				setting[t]['voice'] = 'checked'
			else:
				setting[t]['voice'] = ''
		#print ret
		#print setting
		ybsmtconfig.logger.error('Return alarm setting: %s', setting)
		return setting
	else:
		data = YDI.error_code(ret['head'])
		ybsmtconfig.logger.error('Failed to get alarm setting, error information is %s', data)
		return data


def get_alarm_email():
	ybsmtconfig.logger.info('alarm_test.py get_alarm_email()')
	data = {}
	try:
		ret = ybsmtconfig.MonitorServer.serverrpcser.monitor_get_alarm_email()
		print ret
		ybsmtconfig.logger.info('alarm_test.py get_alarm_setting() return values:%s',ret)
	except Exception, e:
		data = (u'YMAS连接异常！')
		ybsmtconfig.logger.info('alarm_test.py get_alarm_setting() return values:%s',str(e))
		return data
	if ret['head'] == 0:
		data = ret['body']
	else:
		data = YDI.error_code(ret['head'])
		ybsmtconfig.logger.error('Failed to get alarm email, error information is %s', data)
	return data


if __name__ == '__main__' :
	 get_alarm_setting()








