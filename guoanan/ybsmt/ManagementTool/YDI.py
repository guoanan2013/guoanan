#!/user/bin/python
# -*- encoding: UTF-8 -*-

import sys
sys.path.append('/opt/ybs/etc/')
import ybsmtconfig
from datetime import datetime
import time
import sys
import MySQLdb
#import ybsmtconfig
#time.localtime(time.time())
#print time.strftime('%Y-%m-%d %H:%M:%s',time.localtime(time.time()))

def get_version():
	ybsmtconfig.logger.info('YDI.py get_version()')
	error_info = ''
	data = {}
	try:
		v1 = ybsmtconfig.YsnyServer.proxy_gethostinfo()
	except Exception, e:
		error_info = (u'YSNY连接异常！')
		ybsmtconfig.logger.critical('Connect proxy_gethostinfo() failed, the error information:%s',str(e))
		return error_info, data
	try:
		v2 = ybsmtconfig.MonitorServer.serverrpcser.monitor_version()
	except Exception, e:
		error_info = (u'YMAS连接异常！')
		ybsmtconfig.logger.critical('Connect monitor_version() failed, the error information:%s',str(e))
		return error_info, data
	if v1['Head'] == 0:
		data = v1['Body']
		data['YMAS_version'] = v2
		data['YBSMT_version'] = '1.1.0'
	else:
		error_info = YDI.error_code(v1['Head'])
		ybsmtconfig.logger.error('Failed to get alarm email, error information is %s', data)
	return error_info, data



def record_audit_info(audit_info):
#	audit_info = {'user':'admin','operationType':'ADD','targetType':'LU','attribute':'name:wangzhigang','result':'success','time':str(datetime.now())[:19],'remark':''}
	ybsmtconfig.logger.info('YDI.py record_audit_info() concent mysql')
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()

	operationType = audit_info['operationType']
	targetType = audit_info['targetType']

	audit_record = []
	audit_record.append(audit_info['user'])
	
	if operationType == 'ADD':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'ADD' ")
	elif operationType == 'DEL':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'DEL' ")
	elif operationType == 'ALTER':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'ALTER' ")
	elif operationType == 'LOGIN':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'LOGIN' ")
	elif operationType == 'EXIT':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'EXIT' ")
	flag = cur.fetchall()
	operationType = flag[0][0]
	audit_record.append(operationType)

	if targetType == 'LU':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'LU' ")
	elif targetType == 'LUN':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'LUN' ")
	elif targetType == 'NODE':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'NODE' ")
	elif targetType == 'USER':
		cur.execute("SELECT PropertyID FROM YBSDataBase.T_YBS_Property WHERE value = 'USER' ")
	flag1 = cur.fetchall()
	targetType = flag1[0][0]
	audit_record.append(targetType)

	audit_record.append(audit_info['attribute'])
	audit_record.append(audit_info['result'])
	audit_record.append(audit_info['time'])
	audit_record.append(audit_info['remark'])
	
	ybsmtconfig.logger.info('YDI.py record_audit_info() insert audit_record: %s', audit_record)
	cur.execute('INSERT INTO T_AuditRecords(user,operationType,targetType,attribute,result,time,remark) VALUES(%s, %s, %s, %s, %s, %s, %s)', audit_record)
	cxn.commit()
	cxn.close()
	cur.close()


def query_record():
	ybsmtconfig.logger.info('YDI.py query_record()')
	ret = ''
	audit_record = []
	audit_user = []
	try:
		cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
		cxn.select_db('YBSDataBase')
		cur = cxn.cursor()
		
		ybsmtconfig.logger.info('YDI.py query_record() select datebases')
		cur.execute("SELECT * FROM YBSDataBase. T_AuditRecords")
		flag = cur.fetchall()
		for r in flag:
			audit_info_key = {}
			audit_info_key['user'] = r[1].encode('utf-8')
			if audit_user.count(audit_info_key['user']) is 0 and audit_info_key['user'] != '':
				audit_user.append(audit_info_key['user'])
			audit_info_key['operationType'] = str(r[2]).encode('utf-8')
			cur.execute("SELECT value FROM YBSDataBase.T_YBS_Property WHERE PropertyId = %s", audit_info_key['operationType'])
			t = cur.fetchall()
			audit_info_key['operationType'] = t[0][0]
			audit_info_key['targetType'] = str(r[3]).encode('utf-8')
			cur.execute("SELECT value FROM YBSDataBase.T_YBS_Property WHERE PropertyId = %s", audit_info_key['targetType'])
			t = cur.fetchall()
			audit_info_key['targetType'] = t[0][0]
			audit_info_key['attribute'] = r[4].encode('utf-8')
			audit_info_key['result'] = r[5].encode('utf-8')
			audit_info_key['time'] = r[6]
			audit_record.append(audit_info_key)
			cxn.commit()
	except MySQLdb.Error, e:
		ybsmtconfig.logger.critical('Mysql Error %d: %s', e.args[0], e.args[1])
		ret = (u'数据库连接异常！')
	cxn.close()
	cur.close()
	return ret, audit_record, audit_user


def search_record(check_time, check_user, check_result):
	ybsmtconfig.logger.info('YDI.py search_record()')
	ret = ''
	audit_record = []
	audit_user = []
	try:
		cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
		cxn.select_db('YBSDataBase')
		cur = cxn.cursor()
		if check_user is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AuditRecords WHERE user=%s", check_user)
		if check_result is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AuditRecords WHERE result=%s", check_result)
		if check_time is not '%':
			cur.execute("SELECT * FROM YBSDataBase.T_AuditRecords WHERE time LIKE%s", check_time)
		flag = cur.fetchall()
		for r in flag:
			audit_info_key = {}
			audit_info_key['user'] = r[1].encode('utf-8')
			if audit_user.count(audit_info_key['user']) is 0 and audit_info_key['user'] != '':
				audit_user.append(audit_info_key['user'])
			audit_info_key['operationType'] = str(r[2]).encode('utf-8')
			cur.execute("SELECT value FROM YBSDataBase.T_YBS_Property WHERE PropertyId = %s", audit_info_key['operationType'])
			t = cur.fetchall()
			audit_info_key['operationType'] = t[0][0]
			audit_info_key['targetType'] = str(r[3]).encode('utf-8')
			cur.execute("SELECT value FROM YBSDataBase.T_YBS_Property WHERE PropertyId = %s", audit_info_key['targetType'])
			t = cur.fetchall()
			audit_info_key['targetType'] = t[0][0]
			audit_info_key['attribute'] = r[4].encode('utf-8')
			audit_info_key['result'] = r[5].encode('utf-8')
			audit_info_key['time'] = r[6]
			audit_record.append(audit_info_key)
			cxn.commit()
		ybsmtconfig.logger.info('Search auditor records from YBSDataBase.T_AuditRecords:%s', audit_record)
	except MySQLdb.Error, e:
		ybsmtconfig.logger.critical('Mysql Error %d: %s', e.args[0], e.args[1])
		ret = (u'数据库连接异常！')
	cxn.close()
	cur.close()
	return ret, audit_record, audit_user




def alarm():
	ybsmtconfig.logger.info('YDI.py alarm()')
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()
	#mes = cur.fetchall()
	flag1 = ''
	cur.execute("SELECT emailContent  FROM YBSDataBase.T_AlarmRecords  where pickTm is null and TIMESTAMPDIFF(minute,now(),completeTm)<60 and winAlarm = 'Y' limit 0,1")
	mes = cur.fetchall()
	if(len(mes)==0):
		flag1 = (u'报警记录为空')
	else:
		flag1=mes[0][0]
		cur.execute("UPDATE T_AlarmRecords SET pickTm=now() where pickTm is null and TIMESTAMPDIFF(minute,now(),completeTm)<60 and winAlarm = 'Y'")
	return flag1


def error_code(num):
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()
	flag1 = ''
	cur.execute("SELECT Content from T_YBS_Err where ErrCode=%s",num)
	mes=cur.fetchall()
	cxn.close()
	cur.close()
	print 'error_code'
	print mes
	if(len(mes)==0):
		flag1 = (u'错误码查询失败')
	else:
		flag1 = mes[0][0]
	return flag1

'''
def login_session(request,user_name,role):
	print '###################'
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()
	user_session = request.META['REMOTE_ADDR']
	ybsmtconfig.logger.info('YDI.py login_session() session:%s,role:%s',user_session,role)
	cur.execute("SELECT * FROM YBSDataBase.T_YBSMT_Session where session=%s",user_session)
	mes=cur.fetchall()
	print mes
	if len(mes)==0:
		login_record = []
		login_record.append(user_session);
		login_record.append(role);
		login_record.append(user_name);
		sql  = 'INSERT INTO T_YBSMT_Session(session,role,user_name) VALUES(\'%s\', %s,\'%s\' )'% (user_session,role,user_name)
		ybsmtconfig.logger.info('YDI.py login_session() sql:%s',sql)
		cur.execute(sql)
		#cur.execute('INSERT INTO T_YBSMT_Session(session,role,user_name) VALUES(%s, %s,%s)',login_record)
	else:
		sql = "update YBSDataBase.T_YBSMT_Session set role=" + role + " where session=\'" +  user_session + '\''
		#sql = "update YBSDataBase.T_YBSMT_Session set role=%s where session=\'%s\'",num,user_session
		ybsmtconfig.logger.info(sql)
		cur.execute(sql)
		
	cxn.commit()
	cxn.close()
	cur.close()

def logout_session(request):
	user_session = request.META['REMOTE_ADDR']
	ybsmtconfig.logger.info('YDI.py logout_session() session:%s',user_session)
	
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()
	
	cur.execute('DELETE FROM YBSDataBase.T_YBSMT_Session WHERE session=%s',user_session)
	cxn.commit()
	cxn.close()
	cur.close()


def get_role_type(request):
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()
	user_session = request.META['REMOTE_ADDR']
	sql  = 'SELECT role FROM YBSDataBase.T_YBSMT_Session where session=\'%s\''% (user_session)
	#cur.execute("SELECT role FROM YBSDataBase.T_YBSMT_Session where session=%s",user_session)
	ybsmtconfig.logger.info(sql)
	cur.execute(sql)
	mes=cur.fetchall()
	print mes
	role_type = mes[0][0]
	ybsmtconfig.logger.info('YDI.py get_role_type() session:%s,role:%s',user_session,role_type)
	return role_type

def get_user_name(request):
	cxn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '1', charset = 'utf8')
	cxn.select_db('YBSDataBase')
	cur = cxn.cursor()
	
	user_session = request.META['REMOTE_ADDR']
	sql  = 'SELECT user_name FROM YBSDataBase.T_YBSMT_Session where session=\'%s\''% (user_session)
	ybsmtconfig.logger.info(sql)
	cur.execute(sql)
	#cur.execute("SELECT user_name FROM YBSDataBase.T_YBSMT_Session where session=%s",user_session)
	
	mes=cur.fetchall()
	
	user_name = mes[0][0]
	ybsmtconfig.logger.info('YDI.py get_role_type() session:%s,role:%s',user_session,user_name)
	return user_name
'''



if __name__ == '__main__' :
	alarm()


