#!/user/bin/python
# -*- encoding: UTF-8 -*-

from django.shortcuts import render_to_response,render
from django.http import HttpResponse
from mako.template import Template
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from datetime import datetime
import csv
import sys
sys.path.append('/opt/ybs/etc/')
import types

import ybsmtconfig 
import YDI
import target
import resocures
import user
from user import *
import json
import monitor_test
import alarm_test



def login(request):
	name = request.GET['name']
	passwd = request.GET['passwd']
	ybsmtconfig.logger.info('login() name:%s,passwd:%s', name, passwd)
	user = auth.authenticate(username = name, password = passwd)
	# Correct password, and the user is marked "active"
	if user is not None:
		if user.is_active:
			# user login
			auth.login(request, user)
			# Redirect to a success page.
			audit_info = {'user':name,'operationType':'LOGIN','targetType':'USER','attribute':'ADMIN LOGIN','result':'success','time':str(datetime.now())[:19],'remark':''}
			YDI.record_audit_info(audit_info)
			if request.user.has_perm('ManagementTool.super_admin') or request.user.has_perm('ManagementTool.admin'):
				return render_to_response('rm_cluster.html', context_instance = RequestContext(request))
			else:
				return render_to_response('um_setting.html', context_instance = RequestContext(request))
		else:
			audit_info = {'user':name,'operationType':'LOGIN','targetType':'USER','attribute':'ADMIN LOGIN','result':'failed','time':str(datetime.now())[:19],'remark':''}
			YDI.record_audit_info(audit_info)
			return render_to_response('login.html', {'error_info':(u'该用户已被禁用')})
	else:
		# Show an error page
		audit_info = {'user':name,'operationType':'LOGIN','targetType':'USER','attribute':'ADMIN LOGIN','result':'failed','time':str(datetime.now())[:19],'remark':''}
		YDI.record_audit_info(audit_info)
		return render_to_response('login.html',{'error_info': (u'请确认用户名和密码')})

def reset_login(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('login.html', locals())

def get_user_type(request):
	results = ''
	return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')

def default(request):
	users = User.objects.all()
###############
#	for t in users:
#		a = User.objects.get(username = t)
#		a.delete()
#	users = User.objects.all()
###############
	#if null, get user from cluster and write in database
	if len(users) == 0:
		ret = user_list()
		if len(ret[0]) == 0:
			for i in ret[1]:
				print i
				u = User.objects.create_user(username = i['user_name'], password = i['passwd'])
				#set permission
				if i['type'] == 'super_admin':
					u.user_permissions.add(25)
				elif i['type'] == 'admin':
					u.user_permissions.add(26)
				elif i['type'] == 'super_auditor':
					u.user_permissions.add(27)
				elif i['type'] == 'auditor':
					u.user_permissions.add(28)
				#set 'is_active'
				if i['status'] == 'False':
					u.is_active = False
					u.save()
			return render_to_response('login.html',locals())
		else:
			#return error information
			return render_to_response('login.html',{'error_info': ret[0]})
	else:
		return render_to_response('login.html',locals())

#@login_required
def logout_user(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	username = request.user
	auth.logout(request)
	audit_info = {'user':username, 'operationType':'EXIT', 'targetType':'USER', 'attribute':'ADMIN EXIT', 'result':'success', 'time':str(datetime.now())[:19], 'remark':''}
	YDI.record_audit_info(audit_info)
	return render_to_response('logout_user.html',locals())       

#@login_required
def index(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('index.html', context_instance = RequestContext(request))

#@login_required
def change_passwd(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	username = str(request.user)
	newpasswd = request.GET['newpasswd']
	repeatpasswd = request.GET['repeatpasswd']
	ybsmtconfig.logger.info('views.py user_list() newpasswd:%s, repeatpasswd:%s', newpasswd, repeatpasswd)
	if newpasswd != repeatpasswd:
		results = (u'请重新输入密码')
		return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')
	ret = user_change_password(username, newpasswd)
	if ret[1] == 'success':
		u = User.objects.get(username = request.user)
		u.set_password(newpasswd)
		u.save()
	ybsmtconfig.logger.info('views.py user_list() information:%s', ret)
	results = ret[0]
	return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')

############################################################################################################################
####################resources_monitor#######################################################################################
def resources_monitor(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())
	
	return render_to_response('rm_cluster.html', context_instance = RequestContext(request))


def rm_cluster(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('rm_cluster.html', context_instance = RequestContext(request))

def rm_nodes(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('rm_nodes.html', context_instance = RequestContext(request))


####################equipment management######################################################################################
def em_nodes(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ybsmtconfig.logger.info('views.py em_nodes()')
	ret = resocures.node_list()
	ybsmtconfig.logger.error('views.py resources_list() error_info:%s',ret)
	return render_to_response('em_nodes.html',{'error_info':ret[0],'node_list':ret[1]}, context_instance = RequestContext(request))

def em_del_node(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	node_ip = request.GET['node_ip'].encode('UTF-8')
	print 'def deletenode(request):'
	ybsmtconfig.logger.info('views.py deletenode() node_ip:%s', node_ip)
	ret = resocures.delete_node(node_ip)
	ybsmtconfig.logger.info('views.py deletenode() information:%s', ret)
	info = 'DEL_NODE node_ip:'+ node_ip
	audit_info = {'user':request.user,'operationType':'DEL','targetType':'NODE','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	result = resocures.node_list()
	return render_to_response('em_nodes.html',{'error_info':ret[0],'node_list':result[1]}, context_instance = RequestContext(request))


def em_change_node(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	node_ip = request.GET['node_ip']
	status= request.GET['node_status']
	ybsmtconfig.logger.info('views.py changenode() node_ip:%s node_status:%s',node_ip,status)
	ret = resocures.change_node(node_ip, status)
	ybsmtconfig.logger.info('views.py changenode() information:%s',ret)
	info = 'CHA_NODE node_ip:'+ node_ip
	audit_info = {'user':request.user,'operationType':'DEL','targetType':'NODE','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	result = resocures.node_list()
	return render_to_response('em_nodes.html',{'error_info':ret[0],'node_list':result[1]}, context_instance = RequestContext(request))

def em_add_node(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('em_add_node.html', context_instance = RequestContext(request))


def em_add_node_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ip = request.GET['ip']
	ybsmtconfig.logger.info('views.py addnode() node_ip:%s',ip)
	if len(ip) == 3:
		return render_to_response('resources.html',{'node_list':node_list,'error_info':(u'输入不能为空')}, context_instance = RequestContext(request))
	ret = resocures.add_node(ip)
	ybsmtconfig.logger.error('views.py addnode() information:%s',ret)
	info = 'ADD_NODE node_ip:'+ ip
	audit_info = {'user':request.user,'operationType':'ADD','targetType':'NODE','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	#result = resocures.node_list()
	#return render_to_response('em_add_node.html',{'error_info':ret[0],'node_list':result[1]}, context_instance = RequestContext(request))
	return HttpResponse(json.dumps(ret[0], ensure_ascii = False), mimetype = 'application/json')


def em_zone(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ret = resocures.zone_info()
	#print ret
	return render_to_response('em_zone.html',{'error_info':ret[0], 'zone_info':ret[1]}, context_instance = RequestContext(request))

def em_zone_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	node_id = request.GET['node_id']
	node_ip = request.GET['node_ip']
	new_id = request.GET['new_id']
	error_info = resocures.set_zone(node_id, node_ip, new_id)
	ret = resocures.zone_info()
	return render_to_response('em_zone.html',{'error_info':error_info, 'zone_info':ret[1]}, context_instance = RequestContext(request))


#em_cache_management
def em_cluster(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ret = resocures.cache()
	print ret
	return render_to_response('em_cluster.html',{'error_info':ret[0], 'cache_info':ret[1]}, context_instance = RequestContext(request))


def em_change_cache(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	cache_info = {}
	cache_info['cache_status'] = request.GET['cache_status']
	if cache_info['cache_status'] == (u'开启'):
		cache_info['cache_status'] = 1
	else:
		cache_info['cache_status'] = 0
	cache_info['node_ip'] = request.GET['node_ip']
	cache_info['cache_dir'] = request.GET['cache_dir']
	if cache_info['cache_dir'] == ('-'):
		cache_info['cache_dir'] = ''
	cache_info['cache_size'] = request.GET['cache_size']
	if cache_info['cache_size'] == ('-'):
		cache_info['cache_size'] = ''
	cache_info['cache_flag'] = request.GET['cache_flag']
	#print cache_info
	return render_to_response('em_change_cache.html',{'cache_info':cache_info}, context_instance = RequestContext(request))

def em_change_cache_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	cache_info = {}
	cache_info['cache_status'] = request.GET['cache_status']
	if cache_info['cache_status'] == (u'开启'):
		cache_info['cache_status'] = 1
	else:
		cache_info['cache_status'] = 0
	cache_info['node_ip'] = request.GET['node_ip']
	cache_info['cache_dir'] = request.GET['cache_dir']
	cache_info['cache_size'] = request.GET['cache_size']
	cache_info['cache_flag'] = request.GET['cache_flag']
	if cache_info['cache_flag'] == (u'是'):
		cache_info['cache_flag'] = 'directio'
	elif cache_info['cache_flag'] == (u'否'):
		cache_info['cache_flag'] = 'no_directio'
	#print cache_info
	results = resocures.cache_change(cache_info)
	return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')



def em_shutdown(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('em_shutdown.html', context_instance = RequestContext(request))



def em_shutdown_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	name = request.GET['name']
	passwd = request.GET['passwd']
	ybsmtconfig.logger.info('em_shutdown_action() name:%s,passwd:%s', name, passwd)
	if request.user.has_perm('ManagementTool.super_admin'):
		user = auth.authenticate(username = name, password = passwd)
		if user is not None:
			ret = resocures.shutdown_cluster()
			results = ret
			return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')
		else:
			results = (u'请确认用户名和密码！')
			return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')
	else:
		results = (u'当前用户无执行权限！')
		return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')
####################equipment management######################################################################################


####################alarm management######################################################################################
def alarm_management(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	result = alarm_test.get_T_AlarmRecords()
	error_info = result[0]
	alarm_records = result[1]
	alarm_ip = result[2]
	return render_to_response('am_manage.html', {'error_info':error_info, 'alarm_records':alarm_records, 'alarm_ip':alarm_ip}, context_instance = RequestContext(request))

def am_manage(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	result = alarm_test.get_T_AlarmRecords()
	error_info = result[0]
	alarm_records = result[1]
	alarm_ip = result[2]
	return render_to_response('am_manage.html', {'error_info':error_info, 'alarm_records':alarm_records, 'alarm_ip':alarm_ip}, context_instance = RequestContext(request))


def am_search(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	search_ip = request.GET['search_ip'].encode('utf-8')
	search_date_start = request.GET['search_date_start'].encode('utf-8')
	search_context = request.GET['search_context'].encode('utf-8')
	search_date_end = request.GET['search_date_end'].encode('utf-8')
	search_status = request.GET['search_status'].encode('utf-8')
	error_info = ''
	result = alarm_test.search_T_AlarmRecords(search_ip, search_date_start, search_context, search_date_end, search_status)
	error_info = result[0]
	alarm_records = result[1]
	alarm_ip = result[2]
	return render_to_response('am_manage.html', {'error_info':error_info, 'alarm_records':alarm_records, 'alarm_ip':alarm_ip}, context_instance = RequestContext(request))

def am_handle(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	AlarmID = request.GET['AlarmID'].encode('utf-8')
	error_info = ''
	result = alarm_test.handle_T_AlarmRecords(AlarmID)
	error_info = result[0]
	alarm_records = result[1]
	alarm_ip = result[2]
	return render_to_response('am_manage.html', {'error_info':error_info, 'alarm_records':alarm_records, 'alarm_ip':alarm_ip}, context_instance = RequestContext(request))
	
	
def am_setting(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	alarm_setting_info = alarm_test.get_alarm_setting()
	if type(alarm_setting_info) == types.StringType or type(alarm_setting_info) == types.UnicodeType:
		error_info = alarm_setting_info
		alarm_cpu = {}
		alarm_mem = {}
		alarm_disk = {}
	else:
		alarm_cpu = alarm_setting_info['cpu']
		alarm_mem = alarm_setting_info['mem']
		alarm_disk = alarm_setting_info['disk']
	#print alarm_setting_info
	return render_to_response('am_setting.html',{'error_info':error_info,'alarm_cpu':alarm_cpu,'alarm_mem':alarm_mem,'alarm_disk':alarm_disk}, context_instance = RequestContext(request))
	
	
def am_setting_save(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	cpu = {}
	mem = {}
	disk ={}
	#if 'cpuinfo' in request.GET and request.GET['cpuinfo'] and 'meminfo' in request.GET and request.GET['meminfo'] and 'diskinfo' in request.GET and request.GET['diskinfo']:
	cpuinfo = request.GET['cpuinfo'].encode('utf-8')
	meminfo = request.GET['meminfo'].encode('utf-8')
	diskinfo = request.GET['diskinfo'].encode('utf-8')
	cpulist = cpuinfo.split(',')
	memlist = meminfo.split(',')
	disklist = diskinfo.split(',')
	print cpulist
	print memlist
	print disklist
	cpu = {'status':int(cpulist[0]),'watchtime':int(cpulist[1]),'alarmline':int(cpulist[2]),'popwin':int(cpulist[3]),'sendemail':int(cpulist[4]),'voice':int(cpulist[5])}
	mem = {'status':int(memlist[0]),'watchtime':int(memlist[1]),'alarmline':int(memlist[2]),'popwin':int(memlist[3]),'sendemail':int(memlist[4]),'voice':int(memlist[5])}
	disk = {'status':int(disklist[0]),'watchtime':int(disklist[1]),'alarmline':int(disklist[2]),'popwin':int(disklist[3]),'sendemail':int(disklist[4]),'voice':int(disklist[5])}
	ret = alarm_test.save_alarm_setting(cpu, mem, disk)
	error_info = ret
	ybsmtconfig.logger.info('view.py alarmsetting() cpu:%s mem:%s disk:%s',cpu,mem,disk)
	alarm_setting_info = alarm_test.get_alarm_setting()
	print '1111111111111111111111111111111111111'
	print alarm_setting_info
	if type(alarm_setting_info) == types.StringType or type(alarm_setting_info) == types.UnicodeType:
		alarm_cpu = {}
		alarm_mem = {}
		alarm_disk = {}
	else:
		error_info = (u'报警配置保存成功！')
		alarm_cpu = alarm_setting_info['cpu']
		alarm_mem = alarm_setting_info['mem']
		alarm_disk = alarm_setting_info['disk']
	ybsmtconfig.logger.info('view.py alarmsetting() information:%s', ret)
	return render_to_response('am_setting.html',{'error_info':error_info,'alarm_cpu':alarm_cpu,'alarm_mem':alarm_mem,'alarm_disk':alarm_disk}, context_instance = RequestContext(request))



def am_email(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	alarm_email = alarm_test.get_alarm_email()
	if type(alarm_email) == types.StringType or type(alarm_email) == types.UnicodeType:
		error_info = alarm_email
		alarm_email = {}
	return render_to_response('am_email.html', {'error_info':error_info,'email_info':alarm_email}, context_instance = RequestContext(request))
	
	
def am_email_save(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	smtp_server_addr = request.GET['smtp_server_addr']
	smtp_server_username = request.GET['smtp_server_username']
	smtp_server_password = request.GET['smtp_server_password']
	send_email_addr = request.GET['send_email_addr']
	recv_email_addr = request.GET['recv_email_addr']
	topic = request.GET['topic']
	email_info={'smtp_server_addr':smtp_server_addr,'smtp_server_username':smtp_server_username,'smtp_server_password':smtp_server_password,'send_email_addr':send_email_addr,'recv_email_addr':recv_email_addr,'topic':topic}
	ybsmtconfig.logger.info('view.py saveemail() smtp_server_addr:%s, smtp_server_username:%s, smtp_server_password:%s, send_email_addr:%s, recv_email_addr:%s, topic:%s', smtp_server_addr,smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr,topic)
	ret = alarm_test.save_alarm_email_test(smtp_server_addr,smtp_server_username,smtp_server_password,send_email_addr,recv_email_addr,topic)
	error_info = ret
	ybsmtconfig.logger.error('view.py saveemail() information:%s',ret)

	alarm_email = alarm_test.get_alarm_email()
	if type(alarm_email) == types.StringType or type(alarm_email) == types.UnicodeType:
		alarm_email = {}
	return render_to_response('am_email.html',{'error_info':error_info,'email_info':alarm_email}, context_instance = RequestContext(request))


def am_email_test(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	smtp_server_addr = request.GET['smtp_server_addr']
	smtp_server_username = request.GET['smtp_server_username']
	smtp_server_password = request.GET['smtp_server_password']
	send_email_addr = request.GET['send_email_addr']
	recv_email_addr = request.GET['recv_email_addr']
	topic = request.GET['topic']
	email_content = request.GET['email_content']
	email_info={'smtp_server_addr':smtp_server_addr,'smtp_server_username':smtp_server_username,'smtp_server_password':smtp_server_password,'send_email_addr':send_email_addr,'recv_email_addr':recv_email_addr,'topic':topic,'email_content':email_content}
	ybsmtconfig.logger.info('view.py testemail() smtp_server_addr:%s, smtp_server_username:%s, smtp_server_password:%s, send_email_addr:%s, recv_email_addr:%s, topic:%s', smtp_server_addr,smtp_server_username, smtp_server_password, send_email_addr, recv_email_addr, topic)
	ret = alarm_test.test_email(smtp_server_addr,smtp_server_username,smtp_server_password,send_email_addr,recv_email_addr,topic,email_content)
	error_info = ret
	ybsmtconfig.logger.info('view.py testemail() informaiton:%s',ret)
	return render_to_response('am_email.html',{'error_info':error_info,'email_info':email_info}, context_instance = RequestContext(request))

####################help management######################################################################################
def help_management(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('hm_introductions.html', context_instance = RequestContext(request))


def hm_introductions(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('hm_introductions.html', context_instance = RequestContext(request))

def hm_about(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ret = YDI.get_version()
	error_info = ret[0]
	about = ret[1]
	return render_to_response('hm_about.html',{'error_info':error_info,'about':about}, context_instance = RequestContext(request))


####################LU######################################################################################################
####################storage management######################################################################################
def ceate_ip_san(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	request.session['lu'] = {}
	request.session['lu']['lu_name'] = ''
	request.session['lu']['lu_passwd'] = ''
	request.session['lu']['chap_name'] = ''
	request.session['lu']['lu_ip'] = ''
	request.session['lu']['selvalue'] = ''
	request.session['lu']['num'] = 0

	request.session['lun'] = []
	request.session['black'] = []


def sm_ip_san(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ceate_ip_san(request)
	ybsmtconfig.logger.info('views.py sm_ip_san()')
	target_info = target.target_list()
	ybsmtconfig.logger.info('views.py sm_ip_san() get target_list() return message:%s', target_info)
	online_targetip = target.get_online_targetip()
	return render_to_response('sm_ip_san.html',{'error_info':target_info[0],'target_info':target_info[1],'online_targetip':online_targetip[1]}, context_instance = RequestContext(request))

def sm_onlineloader(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_name = request.GET['lu_name']
	lu_ip = request.GET['lu_ip']
	ybsmtconfig.logger.info('views.py onlineloder() lu_name:%s lu_ip:%s',lu_name,lu_ip)
	onlineloder_list = target.onlineloder_list(lu_name,lu_ip)
	print onlineloder_list[1]
	ybsmtconfig.logger.info('views.py onlineloder() info:%s',onlineloder_list)
	return render_to_response('sm_onlineloader.html',{'error_info':onlineloder_list[0],'onlineloder_list':onlineloder_list[1]}, context_instance = RequestContext(request))

def sm_delete_target(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_name = request.GET['lu_name']
	lu_ip = request.GET['lu_ip']
	ybsmtconfig.logger.info('views.py delete_lu() lu_name:%s lu_ip:%s',lu_name,lu_ip)
	ret = target.delete_lu(lu_name,lu_ip)

	info = 'DELETE_LU:'+lu_name +','+lu_ip
	audit_info = {'user':request.user,'operationType':'DEL','targetType':'LU','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)

	target_info = target.target_list()
	online_targetip = target.get_online_targetip()
	return render_to_response('sm_ip_san.html',{'error_info':ret[0],'target_info':target_info[1],'online_targetip':online_targetip[1]},context_instance = RequestContext(request))	
	

#detailed
def sm_change_target(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	ybsmtconfig.logger.info('views.py sm_change_target() lu_name:%s,lu_ip:%s',lu_name,lu_ip)
	target_info = target.target_tails(lu_name,lu_ip)
	target_temp = target_info[1]
	lu_info = target_temp['lu_info']
	if len(lu_info) == 0:
		target_info_list = target.target_list()
		return render_to_response('ip_san.html',{'error_info':target_info[0],'target_info':target_info_list[1]}, context_instance = RequestContext(request))
	lun_info = target_temp['lun_info']
	black_list = target_temp['initiator_blacklist']
	black_info = {'black_name':''}
	for i, value in enumerate(black_list):
		black_info = {'black_name':''}
		black_info['black_name']=value
		black_list[i]=black_info
	dic = {'error_info':target_info[0], 'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list}
	ybsmtconfig.logger.info('views.py sm_change_target() success return value:%s',dic)
	return render_to_response('sm_change_target.html',dic, context_instance = RequestContext(request))

def sm_modify_ip_chap(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	new_chap = request.GET['new_chap'].encode('utf-8')
	chap_name = request.GET['chap_name'].encode('utf-8')
	ret = target.modify_ip_chap(lu_name, lu_ip, new_chap, chap_name)
	
	target_info = target.target_tails(lu_name,lu_ip)
	target_info = target_info[1]
	lu_info = target_info['lu_info']
	lun_info = target_info['lun_info']
	black_list = target_info['initiator_blacklist']
	for i, value in enumerate(black_list):
		black_info = {'black_name':''}
		black_info['black_name'] = value
		black_list[i]=black_info
	dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list,'error_info':ret}
	return render_to_response('sm_change_target.html',dic, context_instance = RequestContext(request))

def sm_addlun(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	addlun_info = {}
	dic ={}
	lun_name = request.GET['lun_name'].encode('utf-8')
	lun_size = request.GET['lun_size'].encode('utf-8')
	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	if len(lun_name) == 0 or len(lun_size) == 1:
		return render_to_response('ip_san.html',{'error_info':(u'输入不能为空')}, context_instance = RequestContext(request))
	lun_info = [{'lun_name':lun_name,'lun_size':lun_size}]
	addlun_info = {'lu_name':lu_name,'lun_info':lun_info,'lu_ip':lu_ip}
	ybsmtconfig.logger.info('views.py addlun() lun_info:%s',lun_info)
	ret = target.add_lun(addlun_info)
	ybsmtconfig.logger.info('views.py addlun() info:%s',ret)
	info = 'ADD_LUN lun_name:'+lun_name
	audit_info = {'user':request.user,'operationType':'ADD','targetType':'LUN','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)

	target_info = target.target_tails(lu_name,lu_ip)
	target_info = target_info[1]
	lu_info = target_info['lu_info']
	lun_info = target_info['lun_info']
	black_list = target_info['initiator_blacklist']
	for i, value in enumerate(black_list):
		black_info = {'black_name':''}
		black_info['black_name']=value
		black_list[i]=black_info
	dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list,'error_info':ret[0]}
	return render_to_response('sm_change_target.html',dic, context_instance = RequestContext(request))


def sm_dellun(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	deletelun_info = {}
	lun_name = request.GET['lun_name'].encode('utf-8')
	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	lu_ip = lu_ip[:-1]
	lunname_info = [lun_name]
	deletelun_info = {'lu_name':lu_name,'lunname_info':lunname_info,'lu_ip':lu_ip}
	ybsmtconfig.logger.info('views.py delete_lun() lun_info:%s',deletelun_info)
	ret = target.delete_lun(deletelun_info)
	ybsmtconfig.logger.error('views.py delete_lun() info:%s',ret)
	
	info = 'DEL_LUN lun_name:'+lun_name
	audit_info = {'user':request.user,'operationType':'DEL','targetType':'LUN','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	target_info = target.target_tails(lu_name,lu_ip)
	target_info = target_info[1]
	lu_info = target_info['lu_info']
	lun_info = target_info['lun_info']
	black_list = target_info['initiator_blacklist']
	for i, value in enumerate(black_list):
		black_info = {'black_name':''}
		black_info['black_name']=value
		black_list[i]=black_info
	dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list,'error_info':ret[0]}
	return render_to_response('sm_change_target.html',dic, context_instance = RequestContext(request))


def sm_addblack(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	black_name = request.GET['black_name'].encode('utf-8')
	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	if len(black_name) == 0:
		return render_to_response('detailed.html',{'error_info':(u'参数不能为空')}, context_instance = RequestContext(request))
	ybsmtconfig.logger.info('views.py addblack() lu_name:%s,black_name:%s,lu_ip:%s',lu_name,black_name,lu_ip)
	ret = target.add_black(lu_name,black_name,lu_ip)
	
	target_info = target.target_tails(lu_name,lu_ip)
	target_info = target_info[1]
	lu_info = target_info['lu_info']
	lun_info = target_info['lun_info']
	black_list = target_info['initiator_blacklist']
	for i, value in enumerate(black_list):
		black_info = {'black_name':''}
		black_info['black_name'] = value
		black_list[i] = black_info
	dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list,'error_info':ret}
	return render_to_response('sm_change_target.html', dic, context_instance = RequestContext(request))


def sm_delblack(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	black_name = request.GET['black_name'].encode('utf-8')
	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	ret = target.delete_black(lu_name,black_name,lu_ip)
	
	target_info = target.target_tails(lu_name,lu_ip)
	target_info = target_info[1]
	lu_info = target_info['lu_info']
	lun_info = target_info['lun_info']
	black_list = target_info['initiator_blacklist']
	for i, value in enumerate(black_list):
		black_info = {'black_name':''}
		black_info['black_name']=value
		black_list[i]=black_info
	dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list,'error_info':ret}
	return render_to_response('sm_change_target.html',dic, context_instance = RequestContext(request))


def sm_add_target(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('sm_add_target.html', context_instance = RequestContext(request))


def sm_add_target_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_info={}
	lu_passwd = request.GET['lu_passwd'].encode('utf-8')
	chap_name = request.GET['chap_name'].encode('utf-8')
	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	selvalue = request.GET['selvalue'].encode('utf-8')
	ip_value = lu_ip
	if len(lu_name) == 0 or len(lu_ip) == 3:
		return render_to_response('ip_san.html',{'error_info':(u'参数不能为空')}, context_instance = RequestContext(request))
	if selvalue == '0':
		ip_value="ALL"
	elif selvalue == '1':
		temp = ip_value.split('.')
		ip_value = temp[0]+'.'+temp[1]+'.'+temp[2]+'.0/24'
	elif selvalue == '2':
		temp = ip_value.split('.')
		ip_value = temp[0]+'.'+temp[1]+'.0.0/16'
	request.session['lu'] = {}
	request.session['lu']['lu_name'] = lu_name
	request.session['lu']['chap_name'] = chap_name
	request.session['lu']['lu_passwd'] = lu_passwd
	request.session['lu']['lu_ip'] = lu_ip
	request.session['lu']['selvalue'] = ip_value
	request.session['lu']['num'] = 0
	ybsmtconfig.logger.info('views.py addlu() lu info:%s', request.session['lu'])

	lun_name = request.GET['lun_name'].encode('utf-8')
	lun_size = request.GET['lun_size'].encode('utf-8')
	lun_num = request.session['lu']['num']
	lun_info = {'lun_name':lun_name, 'lun_size':lun_size, 'lun_num':lun_num}
	ybsmtconfig.logger.info('views.py addlu_lun() lun_name:%s,lun_size:%s,lun_info:%s',lun_name,lun_size,lun_info)
	request.session['lun'] = request.session['lun']
	request.session['lun'].append(lun_info)
	request.session['lu']['num'] = request.session['lu']['num'] + 1
	dic = {'lu_info':request.session['lu'],'lun_info':request.session['lun'], 'black_list': request.session['black']}
	ybsmtconfig.logger.info(dic)

	results = addlu_real(request)
	return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')

def sm_recover_target(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('sm_recover_target.html', context_instance = RequestContext(request))

def sm_recover_target_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	src_ip = request.GET['src_ip'].encode('utf-8')
	des_ip = request.GET['des_ip'].encode('utf-8')
	ybsmtconfig.logger.info('views.py recover_target() src_ip:%s,des_ip:%s',src_ip,des_ip)
	#target_info = target.target_list()
	#online_targetip = target.get_online_targetip()
	recover_ret = target.recover_target_list(src_ip,des_ip)
	return HttpResponse(json.dumps(recover_ret, ensure_ascii = False), mimetype = 'application/json')


def sm_fc_san(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('sm_fc_san.html', context_instance = RequestContext(request))

def sm_lun_assign(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('sm_lun_assign.html', context_instance = RequestContext(request))


def sm_service_conf(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	result = target.iscsi_service()
	#print result
	return render_to_response('sm_service_conf.html',{'error_info':result[0], 'iscsi_list':result[1]}, context_instance = RequestContext(request))

def sm_service_conf_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_ip = request.GET['ip'].encode('utf-8')
	tgt_status = request.GET['tgt_status'].encode('utf-8')
	if tgt_status == (u'启动').encode('utf-8'):
		status = 1
	else:
		status = 0
	error_info = target.iscsi_service_exchange(lu_ip, status)
	result = target.iscsi_service()
	return render_to_response('sm_service_conf.html',{'error_info':error_info, 'iscsi_list':result[1]}, context_instance = RequestContext(request))



def sm_fc_service(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('sm_fc_service.html', context_instance = RequestContext(request))

'''
#@login_required
def ip_san(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	ceate_ip_san(request)
	ybsmtconfig.logger.info('views.py ip_san()')
	target_info = target.target_list()
	ybsmtconfig.logger.info('views.py ip_san() get target_list() return message:%s', target_info)
	online_targetip = target.get_online_targetip()
	return render_to_response('ip_san.html',{'error_info':target_info[0],'target_info':target_info[1],'online_targetip':online_targetip[1]}, context_instance = RequestContext(request))
'''

def fc_san(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())
		
	return render_to_response('fc_san.html',context_instance = RequestContext(request))



def set_ipfilter(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	if 'lu_name' in request.GET and 'ipfilter'in request.GET and'lu_ip' in request.GET and request.GET['lu_name'] and request.GET['lu_ip'] and request.GET['ipfilter']:
		ipfilter = request.GET['ipfilter']
		lu_name = request.GET['lu_name']
		lu_ip = request.GET['lu_ip']
		target_info = target.target_tails(lu_name,lu_ip)
		lu_info = target_info['lu_info']
		lun_info = target_info['lun_info']
		lu_info = lu_info[0]
		black_list = target_info['client_blacklist']
		if black_list[0]=='1':
			black_list = black_list[1:]
			return render_to_response('detailed.html',{'error_info':black_list}, context_instance = RequestContext(request))
		else:
			dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list}
			return render_to_response('detailed.html',dic, context_instance = RequestContext(request))

def addlu_lun(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lun_name = request.GET['lun_name'].encode('utf-8')
	lun_size = request.GET['lun_size'].encode('utf-8')
	lun_num = request.session['lu']['num']
	lun_info = {'lun_name':lun_name, 'lun_size':lun_size, 'lun_num':lun_num}
	ybsmtconfig.logger.info('views.py addlu_lun() lun_name:%s,lun_size:%s,lun_info:%s',lun_name,lun_size,lun_info)
	request.session['lun'] = request.session['lun']
	request.session['lun'].append(lun_info)
	request.session['lu']['num'] = request.session['lu']['num'] + 1
	dic = {'lu_info':request.session['lu'],'lun_info':request.session['lun'], 'black_list': request.session['black']}
	ybsmtconfig.logger.info(dic)
	return render_to_response('addlu_info.html',dic, context_instance = RequestContext(request))



#add_lu_black
def add_black(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	black_name = request.GET['black_name'].encode('utf-8')
	black_info = {'black_name':black_name}
	request.session['black'] = request.session['black']
	request.session['black'].append(black_info)
	ybsmtconfig.logger.info('views.py add_black() black_name:%s',black_name)
	dic = {'lu_info':request.session['lu'],'lun_info':request.session['lun'], 'black_list': request.session['black']}
	return render_to_response('addlu_info.html',dic, context_instance = RequestContext(request))

def addlu(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_info={}
	lu_passwd = request.GET['lu_passwd'].encode('utf-8')
	chap_name = request.GET['chap_name'].encode('utf-8')
	lu_name = request.GET['lu_name'].encode('utf-8')
	lu_ip = request.GET['lu_ip'].encode('utf-8')
	selvalue = request.GET['selvalue'].encode('utf-8')
	ip_value = lu_ip
	if len(lu_name) == 0 or len(lu_ip) == 3:
		return render_to_response('ip_san.html',{'error_info':(u'参数不能为空')}, context_instance = RequestContext(request))
	if selvalue == '0':
		ip_value="ALL"
	elif selvalue == '1':
		temp = ip_value.split('.')
		ip_value = temp[0]+'.'+temp[1]+'.'+temp[2]+'.0/24'
	elif selvalue == '2':
		temp = ip_value.split('.')
		ip_value = temp[0]+'.'+temp[1]+'.0.0/16'
	request.session['lu'] = {}
	request.session['lu']['lu_name'] = lu_name
	request.session['lu']['chap_name'] = chap_name
	request.session['lu']['lu_passwd'] = lu_passwd
	request.session['lu']['lu_ip'] = lu_ip
	request.session['lu']['selvalue'] = ip_value
	request.session['lu']['num'] = 0
	ybsmtconfig.logger.info('views.py addlu() lu info:%s', request.session['lu'])
	return render_to_response('addlu_info.html',{'lu_info':request.session['lu']}, context_instance = RequestContext(request))


def addlu_real(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lu_info = request.session['lu']
	lun_info = request.session['lun']
	black_list = []
	for info in request.session['black']:
		black_list.append(info['black_name'])
	dic = {'lu_info':lu_info,'lun_info':lun_info, 'black_list': black_list}
	ret = target.addlu(lu_info,lun_info,black_list)
	ybsmtconfig.logger.info('views.py addlu_real() lu_info:%s',dic)

	if len(lun_info) == 0:
		return (u'lun不能为空')
		#dic =  {'lu_info':lu_info,'lun_info':lun_info, 'error_info':(u'lun不能为空'),'black_list': request.session['black']}
		#return render_to_response('addlu_info.html',dic, context_instance = RequestContext(request))

	info = 'ADD_LU lu_name:'+lu_info['lu_name']
	audit_info = {'user':request.user,'operationType':'ADD','targetType':'LU','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	
	dic =  {'lu_info':lu_info,'lun_info':lun_info, 'error_info':ret[0],'black_list': request.session['black']}
	return ret[0]
	#return render_to_response('addlu_info.html',dic, context_instance = RequestContext(request))




#def dellu_lun(request):
def del_lun_web(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	lun_name = request.GET['lun_name'].encode('utf-8')
	lun_size = request.GET['lun_size'].encode('utf-8')
	request.session['lun'] = request.session['lun']
	for num, info in enumerate(request.session['lun']):
		if info['lun_name'] == lun_name and info['lun_size'] == lun_size:
			del request.session['lun'][num]
			request.session['lu']['num'] = request.session['lu']['num'] - 1
			break
	dic = {'lu_info':request.session['lu'],'lun_info':request.session['lun'], 'black_list': request.session['black']}
	return render_to_response('addlu_info.html',dic, context_instance = RequestContext(request))


#def dellu_black(request):
def del_black_web(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	black_name = request.GET['black_name'].encode('utf-8')
	request.session['black'] = request.session['black']
	for num, info in enumerate(request.session['black']):
		if info['black_name'] == black_name:
			del request.session['black'][num]
			break
	dic = {'lu_info':request.session['lu'],'lun_info':request.session['lun'], 'black_list': request.session['black']}
	return render_to_response('addlu_info.html',dic, context_instance = RequestContext(request))
#####################LU###############################################################################################################


###################USER############################################################################################################
####################user management######################################################################################
def user_list_django(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	user_list = []
	users = User.objects.all()
	#show admin
	if request.user.has_perm('ManagementTool.super_admin'):
		for user in users:
			temp_user = User.objects.get(username = user)
			a = temp_user.get_all_permissions()
			if 'ManagementTool.admin' in a:
				u = {}
				u['username'] = temp_user
				u['status'] = ''
				if temp_user.is_active:
					u['status'] = (u'启用')
				else:
					u['status'] = (u'禁用')
				user_list.append(u)
	#show auditor
	elif request.user.has_perm('ManagementTool.super_auditor'):
		for user in users:
			temp_user = User.objects.get(username = user)
			a = temp_user.get_all_permissions()
			if 'ManagementTool.auditor' in a:
				u = {}
				u['username'] = temp_user
				u['status'] = ''
				if temp_user.is_active:
					u['status'] = (u'启用')
				else:
					u['status'] = (u'禁用')
				user_list.append(u)
	ybsmtconfig.logger.error('views.py user_list information:%s', user_list)
	return user_list


def uesr_management(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	user_list = user_list_django(request)
	return render_to_response('um_setting.html', {'users':user_list}, context_instance = RequestContext(request))


def um_setting(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	user_list = user_list_django(request)
	return render_to_response('um_setting.html', {'users':user_list}, context_instance = RequestContext(request))


def um_enable_user(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	username = request.GET['username']
	ybsmtconfig.logger.info('views.py enableuser() username:%s',username)
	try:
		u = User.objects.get(username = username)
	except Exception, e:
		user_list = user_list_django(request)
		return render_to_response('um_setting.html', {'error_info':(u'不存在该用户'), 'users':user_list}, context_instance = RequestContext(request))
	#change user status in cluster
	ret = enable_user(username)
	if ret[1] == 'success':
		if u.is_active:
			u.is_active = False
			u.save()
		else:
			u.is_active = True
			u.save()
	user_list = user_list_django(request)
	return render_to_response('um_setting.html',{'users':user_list, 'error_info':ret[0]}, context_instance = RequestContext(request))


def um_delete_user(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	username = request.GET['username']
	ybsmtconfig.logger.info('views.py deleteuser() user_name:%s',username)
	try:
		u = User.objects.get(username = username)
	except Exception, e:
		user_list = user_list_django(request)
		return render_to_response('um_setting.html', {'error_info':(u'不存在该用户'), 'users':user_list}, context_instance = RequestContext(request))
	#delete user in cluster
	ret = delete_user(username)
	ybsmtconfig.logger.error('views.py deleteuser() information:%s',ret)
	#delete user in Django
	if ret[1] == 'success':
		u.delete()
	#add audit information
	info = 'DEL_USER user_name:'+ username
	audit_info = {'user':request.user,'operationType':'DEL','targetType':'USER','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	
	user_list = user_list_django(request)
	return render_to_response('um_setting.html',{'users':user_list, 'error_info':ret[0]}, context_instance = RequestContext(request))


def um_add_user(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('um_add_user.html', context_instance = RequestContext(request))



def um_add_user_action(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	username = request.GET['username']
	userpasswd = request.GET['userpasswd']
	userrepasswd = request.GET['userrepasswd']
	try:
		u = User.objects.get(username = username)
		#user_list = user_list_django(request)
		return render_to_response('administrator.html', {'error_info':(u'该用户已存在')}, context_instance = RequestContext(request))
	except Exception, e:
		pass
	if userpasswd != userrepasswd:
		#user_list = user_list_django(request)
		return render_to_response('administrator.html', {'error_info':(u'密码输入错误')}, context_instance = RequestContext(request))
	#add new user in cluster
	user_info = {}
	if request.user.has_perm('ManagementTool.super_admin'):
		usertype = 'admin'
	elif request.user.has_perm('ManagementTool.super_auditor'):
		usertype = 'auditor'
	user_info = {'user_name':username,'passwd':userpasswd,'type':usertype,'status':'True','other_name':'Null'}
	ybsmtconfig.logger.info('views.py adduser_real() user_info:%s',user_info)
	ret = add_user(user_info)
	#add user in Django
	if ret[1] == 'success':
		u = User.objects.create_user(username = username, password = userpasswd)
		#set permission
		if request.user.has_perm('ManagementTool.super_admin'):
			u.user_permissions.add(26)
		elif request.user.has_perm('ManagementTool.super_auditor'):
			u.user_permissions.add(28)
	#add audit information
	info = 'ADD_USER user_name:' + username
	audit_info = {'user':request.user,'operationType':'ADD','targetType':'USER','attribute':info,'result':ret[1],'time':str(datetime.now())[:19],'remark':''}
	YDI.record_audit_info(audit_info)
	ybsmtconfig.logger.info('views.py adduser_real() information:%s', ret)

	#user_list = user_list_django(request)
	#return render_to_response('um_add_user.html', {'error_info':ret[0]}, context_instance = RequestContext(request))
	print ret
	return HttpResponse(json.dumps(ret[0], ensure_ascii = False), mimetype = 'application/json')


'''
#@login_required
def administrator(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	user_list = user_list_django(request)
	return render_to_response('administrator.html', {'users':user_list}, context_instance = RequestContext(request))
'''
#####################USER##########################################################################################################################




########monitor#################################################################
#@login_required
def monitor(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	flag = 0
	cluster_info = monitor_test.monitor_cluster()
	if type(cluster_info) == types.StringType or type(cluster_info) == types.UnicodeType:
		flag = 1
		cluster_info = ['']
	node_info = monitor_test.monitor_node()
	if type(node_info) == types.StringType or type(node_info) == types.UnicodeType:
		flag = 1
		node_info = []
	alarm_records = alarm_test.get_T_AlarmRecords()
	if type(alarm_records) == types.StringType or type(alarm_records) == types.UnicodeType:
		flag = 1
		alarm_records = {}
	alarm_setting_info = alarm_test.get_alarm_setting()
	if type(alarm_setting_info) == types.StringType or type(alarm_setting_info) == types.UnicodeType:
		flag = 1
		alarm_cpu = {}
		alarm_mem = {}
		alarm_disk = {}
	else:
		alarm_cpu = alarm_setting_info['cpu']
		alarm_mem = alarm_setting_info['mem']
		alarm_disk = alarm_setting_info['disk']
	alarm_email = alarm_test.get_alarm_email()
	if type(alarm_email) == types.StringType or type(alarm_email) == types.UnicodeType:
		flag = 1
		alarm_email = {}
	if flag:
		error_info = (u'YMAS连接异常')
	return render_to_response('monitor.html',{'error_info':error_info,'email_info':alarm_email,'cluster_info':cluster_info[0],'node_info':node_info, 'alarm_records':alarm_records,'alarm_cpu':alarm_cpu,'alarm_mem':alarm_mem,'alarm_disk':alarm_disk}, context_instance = RequestContext(request))



def alarm(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	alarm_msg = alarm_msg.front_alarm_msg
	print alarm_msg()
	return HttpResponse(json.dumps(results, ensure_ascii = False), mimetype = 'application/json')

#@login_required
def auditors(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	error_info = ''
	result = YDI.query_record()
	error_info = result[0]
	audit_info = result[1]
	audit_user = result[2]
	return render_to_response('auditors.html', {'error_info':error_info, 'audit_info':audit_info, 'audit_user':audit_user}, context_instance = RequestContext(request))



def au_search(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	check_time = request.GET['check_time'].encode('utf-8')
	check_user = request.GET['check_user'].encode('utf-8')
	check_result = request.GET['check_result'].encode('utf-8')
	error_info = ''
	result = YDI.search_record(check_time, check_user, check_result)
	error_info = result[0]
	audit_info = result[1]
	audit_user = result[2]
	return render_to_response('auditors.html', {'error_info':error_info, 'audit_info':audit_info, 'audit_user':audit_user}, context_instance = RequestContext(request))


def addauditor(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	return render_to_response('addauditor.html',context_instance = RequestContext(request))

def export(request):
	if not request.user.is_authenticated() or not request.user.is_active:
		return render_to_response('login.html', locals())

	audit_info = YDI.query_record()
	#print audit_info
	audit_info_temp = [[],[],[],[],[],[]]
	for temp in audit_info[1]:
		audit_info_temp[0].append(temp['time'])
		audit_info_temp[1].append(temp['user'])
		audit_info_temp[2].append(temp['operationType'])
		audit_info_temp[3].append(temp['targetType'])
		audit_info_temp[4].append(temp['attribute'])
		audit_info_temp[5].append(temp['result'])
	print audit_info_temp
	response = HttpResponse(mimetype='text/cxv')                                   
    	response['Content-Disposition'] = 'attachment; filename=audit.csv'
	writer = csv.writer(response)
	writer.writerow(['TIME', 'USER','OPERTIONTYPE','OBJECTTYPE','OBJECTATTBUIT','RESULT','REMARK'])
	for(time,user,operationType,targetType,attribute,result) in zip(audit_info_temp[0],audit_info_temp[1],audit_info_temp[2],audit_info_temp[3],audit_info_temp[4],audit_info_temp[5]):
		writer.writerow([time,user,operationType,targetType,attribute,result])
#	for (time,user,operationType,targetType,attribute,result) in zip(audit_info_temp[0], UNRULY_PASSENGERS):
#		writer.writerow([time,user,operationType,targetType,attribute,result])
	return response
