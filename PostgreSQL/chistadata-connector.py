#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
from kafka import KafkaConsumer
import ast
from kafka import KafkaProducer
import json
from clickhouse_driver import Client

consumer = KafkaConsumer('shipment.public.shipments',
                         bootstrap_servers=['YOUR_LOCAL_IP:9093'],
                         auto_offset_reset='earliest',
                         group_id='my-group',
                         enable_auto_commit=False)

client = Client(host='YOUR_LOCAL_IP', port=8002)


# In[2]:


def parse_message(msg, fields=None):
#     msg = [ast.literal_eval(x) for x in str(msg.decode('utf-8')).split(',')]
    
    try:
        dat = str(msg.decode())
        dat = dat.replace('null', """''""")
        dat = ast.literal_eval(dat)
        
        before = dat['before']
        after = dat['after']
        
 #       print(before, after)
        
        data = []
            
        
        if before:
#            before['sign'] = -1
#             for k,v in before.items():
#                 before[k] = str(v)
            data.append(before)
            
        if after:
#            after['sign'] = 1
#             for k,v in after.items():
#                 after[k] = str(v)
                
            data.append(after)
        
  #      print(data)
  #      print(dat['op'])
    
 #       print(dat)
 #       print(data[0]['shipment_id'])
    
        if dat['op'] == 'c' or dat['op'] == 'u':

            client.execute('INSERT INTO default.kafka_table (shipment_id, order_id, date_created, status) VALUES',
                           data)       
            print(data)
        elif dat['op'] == 'd':

            client.execute(f"alter table default.kafka_table delete where shipment_id = {data[0]['shipment_id']}")
            print(data)


    except Exception as e:
        print(str(e))
    


# In[ ]:


for message in consumer:
#    print (message.value)
    parse_message(message.value)


# In[ ]:





# In[ ]:





# In[ ]:




