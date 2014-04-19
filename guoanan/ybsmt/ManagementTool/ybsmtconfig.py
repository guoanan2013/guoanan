import logging
import logging.handlers
import xmlrpclib
Ip_PortMonitor = "http://127.0.0.1:30013"
MonitorServer = xmlrpclib.ServerProxy(Ip_PortMonitor)

Ip_PortYsny = "http://127.0.0.1:30011"
YsnyServer = xmlrpclib.ServerProxy(Ip_PortYsny)

LOG_FILE = "/opt/ybs/log/YBSMT.log"
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 10*1024*1024, backupCount=5)  # initialize handler
fmt = '%(asctime)s - %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
formatter = logging.Formatter(fmt)  # initialize formatter
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
