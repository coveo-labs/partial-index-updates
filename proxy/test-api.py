import copy
import sys
import requests
import marshal
import math
import json
from datetime import datetime

from urllib import parse
import urllib


def callAPI(body):
  print('callSearchAPI')
  base_url = 'https://rufnska662.execute-api.us-east-1.amazonaws.com/prod'
  print (body)
  r = requests.post(f'{base_url}', body)
  print (r)
  p = r.json()
  return p


body={}
with open('settings.json', 'r') as f:
      config = json.load(f)
body['api_key_search']=config['api_key_search']
body['api_key_push']=config['api_key_push']
body['source_id']=config['source_id']
body['org_id']=config['org_id']
body['region']=''
body['type_source']='' #catalog or push
body['additional_query']='@source==PartialUpdates'
body['key_field']='uri'
newdata=[]
newdata.append({'key':'https://fashionstore/?id=89a99d0f55e05b94ad545bcb304699f7&col=Bandolier Brown&sz=Big',    'metadata':{'author':'annie','ec_stock':{'':20,'1':20,'2':20}}})
newdata.append({'key':'https://fashionstore/?id=9fea1d85dc5a534e43b99ef2c41c03f4&col=Yellow Floral&sz=Petite','metadata':{'author':'wim','ec_stock':{'':20,'1':20,'2':20}}})
newdata.append({'key':'https://fashionstore/?id=b602934bd5e96aca05bc45717a50e12f&col=Bare Necessity&sz=Regular','metadata':{'ec_stock':{'':20,'1':20,'2':20}}})
body['newdata']=newdata
jsonbody = json.dumps(body)
returnv = callAPI(jsonbody)
print (returnv)
