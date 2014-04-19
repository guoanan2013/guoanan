#!/user/bin/python
# -*- encoding: UTF-8 -*-

import sys
sys.path.append('/opt/ybs/etc/')
import ybsmtconfig
import operator
import YDI

def user_list():
	ybsmtconfig.logger.info('user.py user_list()')
	ret = ''
	user = []
	try:
		user_list = ybsmtconfig.YsnyServer.proxy_userlist()
		ybsmtconfig.logger.info('user.py user_list() return value:%s',user_list)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_userlist() failed, the error information:%s',str(e))
		return ret, user
	#print user_list
	if user_list['Head'] == 0:
		user =  user_list['Body']
		if len(user) == 0:
			ret = (u'YSNY存储用户列表为空')
		ybsmtconfig.logger.info('user.py user_list() success')
	else:
		ret = YDI.error_code(user_list['Head'])
		ybsmtconfig.logger.info('user.py user_list() error_code:%s', ret)
	return ret, user

def delete_user(user_name):
	ybsmtconfig.logger.info('user.py delete_user() user_name:%s',user_name)
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_deleteuser(user_name)
		ybsmtconfig.logger.info('user.py delete_user() return value :%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_delete_user() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0:
		ret = (u'删除用户成功')
		result = 'success'
		ybsmtconfig.logger.info('user.py delete_user() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('user.py delete_user() error_code:%s',ret)
	return ret, result

def add_user(user_info):
	ybsmtconfig.logger.info('user.py add_user() user_info:%s',user_info)
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_adduser(user_info)
		ybsmtconfig.logger.info('user.py add_user() return value:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('Connect proxy_adduser() failed, the error information:%s',str(e))
		return ret, result
	if ret == 0:
		ret = (u'增加用户成功!')
		result = 'success'
		ybsmtconfig.logger.info('user.py add_user() success')
	else:
		ret = YDI.error_code(ret)
		ybsmtconfig.logger.info('user.py add_user() error_code:%s',ret)
	return ret, result


def enable_user(username):
	ybsmtconfig.logger.info('user.py enable_user() username:%s', username)
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_getuserinfo(username)
		ybsmtconfig.logger.info('user.py enable_user proxy_getuserinfo() return value:%s',ret)
	except Exception, e:
		data = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('user.py get_login() failed, the error information:%s',str(e))
		return data, result
	if ret['Head'] == 0:
		user_info = ret['Body']
		if user_info['status'] == 'True':
			user_info['status'] = 'False'
		else:
			user_info['status'] = 'True'
		try:
			modifyuserinfo = ybsmtconfig.YsnyServer.proxy_modifyuserinfo(user_info)
			ybsmtconfig.logger.info('user.py enable_user proxy_modifyuserinfo() return values:%s',modifyuserinfo)
		except Exception, e:
			data = (u'YSNY连接异常')
			ybsmtconfig.logger.critical('user.py enable_user proxy_modifyuserinfo() error_info:%s',str(e))
			return data, result
		if modifyuserinfo == 0:
			ybsmtconfig.logger.info('user.py change user status success')
			data = (u'修改用户状态成功')
			result = 'success'
		else:
			data = YDI.error_code(modifyuserinfo)
			ybsmtconfig.logger.info('user.py enable_user proxy_modifyuserinfo() error_info:%s',str(e))
	else:
		data = YDI.error_code(ret['Head'])
		ybsmtconfig.logger.info('user.py enable_user proxy_getuserinfo() error_info:%s',data)
	return data, result


def get_login(user_name, passwd):
	ybsmtconfig.logger.info('user.py get_login() user_name:%s,passwd:%s',user_name)
	ret=''
	try:
		ret = ybsmtconfig.YsnyServer.proxy_getuserinfo(user_name)
		ybsmtconfig.logger.info('user.py get_login() return value:%s',ret)
	except Exception, e:
		ret = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('user.py get_login() failed, the error information:%s',str(e))
		return ret
	if ret['Head'] == 0:
		if ret['Body']['passwd'] == passwd:
			ret = ret['Body']['type']
		else:
			ret = 'Waring:Input passwd error!'
		ybsmtconfig.logger.info('user.py get_login() information:%s',ret)
	else:
		ret = YDI.error_code(ret['Head'])
		ybsmtconfig.logger.info('user.py get_login() error_code:%s',ret)
	return ret


def user_change_password(username, newpasswd):
	ybsmtconfig.logger.info('user.py change_passwd() username:%s newpasswd:%s',username,newpasswd)
	print username
	print newpasswd
	result = 'failed'
	try:
		ret = ybsmtconfig.YsnyServer.proxy_getuserinfo(username)
		ybsmtconfig.logger.info('user.py change_passwd proxy_getuserinfo() return value:%s',ret)
	except Exception, e:
		data = (u'YSNY连接异常')
		ybsmtconfig.logger.critical('user.py get_login() failed, the error information:%s',str(e))
		return data, result
	if ret['Head'] == 0:
		user_info = ret['Body']
		user_info['passwd'] = newpasswd
		try:
			modifyuserinfo = ybsmtconfig.YsnyServer.proxy_modifyuserinfo(user_info)
			ybsmtconfig.logger.info('user.py change_passwd proxy_modifyuserinfo() return values:%s',modifyuserinfo)
		except Exception, e:
			data = (u'YSNY连接异常')
			ybsmtconfig.logger.critical('user.py change_passwd proxy_modifyuserinfo() error_info:%s',str(e))
			return data, result
		if modifyuserinfo == 0:
			ybsmtconfig.logger.info('user.py change passwd success')
			data = (u'修改密码成功')
			result = 'success'
			return data, result
		else:
			data = YDI.error_code(modifyuserinfo)
			ybsmtconfig.logger.info('user.py change_passwd proxy_modifyuserinfo() error_info:%s',str(e))
			return data, result
	else:
		data = YDI.error_code(ret['Head'])
		ybsmtconfig.logger.info('user.py change_passwd proxy_getuserinfo() error_info:%s',data)
	return data, result



		
if __name__ == '__main__' :
	user_list('admin')
