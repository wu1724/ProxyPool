import os
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

data_ip_path = os.path.join(data_dir,'data_ip.db')
logger_path = os.path.join(data_dir,'main.log')