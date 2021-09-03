import copy
import sys
import requests
import marshal
import math
import json
from datetime import datetime

from urllib import parse
import urllib
from coveopush import CoveoPush
from coveopush import CoveoDocument
from coveopush import CoveoPermissions
from coveopush import CoveoConstants


def createURL(api_key,region):
  base_url=''
  if (not region==''):
    base_url='https://platform-'+region+'.cloud.coveo.com'
  else:
    base_url='https://platform.cloud.coveo.com'
  return base_url


def updateDocument(result):
    mydoc = CoveoDocument.Document(result['uri'])
    if ('X_HTML_X' in result):
      content = result['X_HTML_X']
      mydoc.SetContentAndZLibCompress(content)
    #Special fields
    if 'date' in result:
      print (result['date'])
      #Seems windows issue
      try:
        dt_object = datetime.fromtimestamp(result['date'])
      except:
        dt_object = datetime.fromtimestamp(result['date']/1000)
      mydoc.SetDate(dt_object)
      mydoc.SetModifiedDate(dt_object)
    if 'author' in result:
      mydoc.Author = result['author']
    if 'title' in result:
      mydoc.Title = result['title']
    if 'ClickUri' in result:
      mydoc.ClickableUri = result['ClickUri']
    for key in result:
      keyLow = key.lower()
      if (keyLow not in [key.lower() for key in CoveoConstants.Constants.s_DocumentReservedKeys]):
        badkeys=['source','syssource','indexeddate','sysindexeddate','collection','syscollection','title','concepts','sysconcepts','filetype','sysfiletype','urihash','sysurihash','rowid','sysrowid','clickableuri','orderingid','size','sysclickableuri','sysdate','date','syssize','systransactionid','transactionid']
        if not (keyLow in badkeys):
            mydoc.AddMetadata(keyLow,result[key])
    # Set the fileextension
    if ('filetype' in result):
      mydoc.FileExtension = '.'+result['filetype']

    return mydoc

def callSearchAPI(api_key, par, region, url_parameters):
  print('callSearchAPI')
  base_url=createURL(api_key,region)
  base_url+='/rest/search/v2'+par+'?'+'access_token='+api_key+'&'+url_parameters
  print('Calling:')
  print(base_url)
  r = requests.get(f'{base_url}')
  print (r)
  p = r.json()
  return p


def getAllMeta(api_key, region, result):
  allMeta={}
  #Add special
  allMeta['ClickUri'] = result['ClickUri']
  #Get raw properties
  for key in result['raw']:
      allMeta[key]=result['raw'][key]
  #Is it HTML?
  if (result['hasHtmlVersion']==True):
    #Fetch HTML
    id = result['UniqueId']
    base_url=createURL(api_key,region)
    pars={}
    pars['uniqueId']= id
    base_url+='/rest/search/v2/html?'+'access_token='+api_key+'&'+urllib.parse.urlencode(pars)+'&enableNavigation=false'
    print('Calling for HTML:')
    print(base_url)
    r = requests.get(f'{base_url}')
    print (r.text)
    if (r.text.startswith('<meta http')):
      allMeta['X_HTML_X']="\n".join(r.text.split("\n")[2:])
    else:
      allMeta['X_HTML_X']=r.text
  return allMeta

def processQuery(api_key_search, api_key_push, source_id, type_source, org_id, region, newdata, additional_query, key_field):
  print(f'processQuery')
  #check keyfield
  if key_field=='':
    key_field='uri'
  output_parameters={}
  #default parameters
  output_parameters['numberOfResults']=25
  #output_parameters['searchHub']='PROXY_QS_HUB'
  output_parameters['referrer']='https://coveopartialupdates/'
  report = {}
  totalKeys=0
  output_parameters['q']='@'+key_field+'==('
  for key in newdata:
    output_parameters['q']+='"'+key['key']+'",'
    report[key['key']]='Not Found'
    totalKeys+=1
  output_parameters['q']+=')'
  output_parameters['aq']=additional_query
  if (totalKeys>25):
    return "To many keys provided, maximum=25"

  #call api
  print('Executing query to fetch results: '+output_parameters['q'])
  response = callSearchAPI(api_key_search, '', region, urllib.parse.urlencode(output_parameters))
  #prep it for the response
  totalFiltered = response['totalCountFiltered']
  print ('Total Found: '+str(totalFiltered))
  results = response['results']
  updateSourceStatus = True
  deleteOlder = False
  added=False
  if (totalFiltered>0):
    #Start a new Batch call against STREAM API or PUSH API
    print ('Type of source: '+type_source)
    if (type_source=='' or type_source=='catalog'):
      push = CoveoPush.Push(source_id, org_id, api_key_push, p_Mode=CoveoConstants.Constants.Mode.UpdateStream)
    else:
      push = CoveoPush.Push(source_id, org_id, api_key_push, p_Mode=CoveoConstants.Constants.Mode.Push)

    push.Start(updateSourceStatus, deleteOlder)

    for result in results:
      resultValue=getAllMeta(api_key_search,region, result)
      print('Processing result: '+resultValue[key_field])
      #override the new data
      # find the key in the newdata
      for key in newdata:
        if (resultValue[key_field]==key['key']):
          print('Found result, start to update: '+resultValue[key_field])
          #found
          for meta in key['metadata']:
            print (meta)
            resultValue[meta] = key['metadata'][meta]
          report[resultValue[key_field]]='Found and updated'
          push.Add(updateDocument(resultValue))
          added=True
    #Finish Batch Call
    if (added):
      push.End(updateSourceStatus, deleteOlder)
  print('Pushing batch')
  return report


def process(api_key_search, api_key_push, source_id, type_source, org_id,region, newdata, additional_query, key_field ):
  returnValue=''
  print('process')
  returnValue=json.dumps(processQuery(api_key_search,api_key_push, source_id, type_source, org_id,region, newdata, additional_query, key_field))
  return returnValue

def getKey(body, key):
  if key in body:
    return body[key]
  else:
    return ''

def lambda_handler(event, context):
    print(f"q: {json.dumps(event)}")
    if 'body' in event:
      body = json.loads(event['body'])
      api_key_search=getKey(body,'api_key_search')
      api_key_push=getKey(body,'api_key_push')
      source_id=getKey(body,'source_id')
      org_id=getKey(body,'org_id')
      key_field=getKey(body,'key_field')
      region=getKey(body,'region')
      type_source=getKey(body,'type_source') #catalog or push
      additional_query=getKey(body,'additional_query')
      newdata=getKey(body,'newdata')
      #print (additional_query)
      return {#process(name,key_product, key_variant, products_url, key_limit,key_page, limit, page)#{ #{
            'statusCode': 200,
            'body': process(api_key_search, api_key_push, source_id, type_source,org_id,region, newdata, additional_query, key_field ),
            "headers": {
              "Content-Type": 'application/json',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Headers': "x-www-form-urlencoded, Origin, X-Requested-With, Content-Type, Accept, Authorization"
            }    
      }

# body={}
# with open('settings.json', 'r') as f:
#       config = json.load(f)
# body['api_key_search']=config['api_key_search']
# body['api_key_push']=config['api_key_push']
# body['source_id']=config['source_id']
# body['org_id']=config['org_id']
# body['region']=''
# body['type_source']='' #catalog or push
# body['additional_query']='@source==PartialUpdates'
# body['key_field']='uri'
# newdata=[]
# newdata.append({'key':'https://fashionstore/?id=89a99d0f55e05b94ad545bcb304699f7&col=Bandolier Brown&sz=Big',    'metadata':{'author':'annie','ec_stock':{'':20,'1':20,'2':20}}})
# newdata.append({'key':'https://fashionstore/?id=9fea1d85dc5a534e43b99ef2c41c03f4&col=Yellow Floral&sz=Petite','metadata':{'author':'wim','ec_stock':{'':20,'1':20,'2':20}}})
# newdata.append({'key':'https://fashionstore/?id=b602934bd5e96aca05bc45717a50e12f&col=Bare Necessity&sz=Regular','metadata':{'ec_stock':{'':20,'1':20,'2':20}}})
# body['newdata']=newdata
# event={}
# event['body']=json.dumps(body)
# returnv = lambda_handler(event,event)
# #returnv=process(api_key_search, api_key_push, source_id, org_id,typeSource,region, newdata, additional_query )
# print (returnv)
