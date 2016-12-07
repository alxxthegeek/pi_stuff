from boto.ec2 import cloudwatch
from boto.utils import get_instance_metadata
import datetime
 
conn_cw=cloudwatch.connect_to_region('us-east-1')
conn_cw.put_metric_data(namespace='kegmetrics',name='temp',value='1',dimensions={'temp':'c'})
