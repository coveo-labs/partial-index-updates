from coveopush import CoveoPush
from coveopush import CoveoDocument
from coveopush import CoveoPermissions
from coveopush import CoveoConstants

import json
import os
from datetime import timedelta
from datetime import datetime
import random
import html
stores=["1","2","3","4","5","6","7"]
storesSKU={}


def fixHtml(htmls):
  htmls = htmls.replace("&amp;","&")
  return html.unescape(htmls)

def add_document(post,filename):
    global storesSKU
    global stores
    # Create new push document
    product = True
    if ('_PROD' in filename):
      product = True
      col = post['color']
      col = col.replace('/','').replace("'","").replace("?","")
      size = post['selected_size']
      mydoc = CoveoDocument.Document('https://fashionstore/?id='+post['uniq_id']+'&col='+col+'&sz='+size)
      content = "<meta charset='UTF-16'><meta http-equiv='Content-Type' content='text/html; charset=UTF-16'><html><head><title>"+fixHtml(post['product_name'])+"</title></head><body>"+post['description']+' '+post['product_code']+' '+' '.join(post['attributes'])+"</body></html>"
      mydoc.SetContentAndZLibCompress(content)
      mydoc.AddMetadata('documenttype','Product')
      mydoc.AddMetadata('objecttype','Product')
      mydoc.AddMetadata("ec_brand", post['brand_name'])
      mydoc.AddMetadata("customerreviewcount",post['review_count'])
      mydoc.AddMetadata("ec_fit_size", size)
      mydoc.AddMetadata("ec_seller", post['seller_name'])
      mydoc.AddMetadata("ec_on_sale", post['on_sale'])
      mydoc.AddMetadata("ec_category", post['category'])
      mydoc.AddMetadata("category_slug", post['category'].replace('|','/').replace(' ','-').lower())
      mydoc.AddMetadata("ec_name", fixHtml(post['product_name']))
      #Multiple products (colors) have the same group, we want to fold by them
      mydoc.AddMetadata("ec_product_group", post['product_code'])
      mydoc.AddMetadata("product_gender", post['product_gender'])
      #ec_Product_id is the unique identifier for this product
      #ec_Product_id must also be availabe in the VARIANT
      #This will create a query like:
      #[[@ec_product_id] @objecttype==Variant @ec_variant_id=[[@ec_availability_skus] @objecttype==Availability]]
      #And after selecting a store:
      #@ec_variant_id=[[@ec_availability_skus] @objecttype==Availability @ec_availability_id==2 @source==FashionCatalog]]
      mydoc.AddMetadata("ec_product_id", post['uniq_id'])
      mydoc.AddMetadata("ec_images", post['images'])
      if (len(post['images'])>0):
        mydoc.AddMetadata("ec_image", post['images'][0])
      mydoc.AddMetadata("ec_price", post['mrp'])
      mydoc.AddMetadata("ec_promo_price", post['price'])
      mydoc.AddMetadata("ec_item_group_id", post['product_code'])
      mydoc.AddMetadata("ec_in_stock",  False if post['out_of_stock']=="1" else True)
      mydoc.AddMetadata("ec_slug", post['product_code'])
      mydoc.AddMetadata("ec_tags", post['attributes'])
      mydoc.AddMetadata("ec_season", post['season'])
      mydoc.AddMetadata("ec_color_img", post['colorimg'])
      mydoc.AddMetadata("ec_product_color", post['color'])
      mydoc.AddMetadata("ec_store_prices", post['store_prices'])#'"'+json.dumps(post['store_prices'])+'"')
      mydoc.AddMetadata("ec_brand_cat", post['brandcat'])
      mydoc.AddMetadata("ec_rating", post['rating'])
      mydoc.AddMetadata("permanentid", post['uniq_id'])
      mydoc.Title = fixHtml(post['product_name'])
      stock={}
      stock[""] = str('20')

      for storeid in stores:
        stock[storeid] = 10
      mydoc.AddMetadata("ec_stock", stock)


    
    # Build up the quickview/preview (HTML)

    # Set the fileextension
    mydoc.FileExtension = ".html"
    # Set the date
    mydoc.SetDate(datetime.now())
    mydoc.SetModifiedDate(datetime.now())

    return mydoc


def main():
    global storesSKU
    counter = 0
    with open('settings.json', 'r') as f:
      config = json.load(f)
      
    sourceId = config['sourceId']
    orgId = config['orgId']
    apiKey = config['apiKey']

    updateSourceStatus = True
    deleteOlder = True
    # Setup the push client
    push = CoveoPush.Push(sourceId, orgId, apiKey, p_Mode=CoveoConstants.Constants.Mode.Stream)
    # Set the maximum
    push.SetSizeMaxRequest(150*1024*1024)

    # Start the batch
    push.Start(updateSourceStatus, deleteOlder)
    path=u"..\\json"
    for filename in os.listdir(path):
      print ("Parse: "+filename)
      with open(path+"/"+filename) as data_file:
        try:
          rec = json.load(data_file)
          rec['on_sale']='No'
          push.Add(add_document(rec,filename))
            #add_document2(rec,filename)
          #push.Add(add_document3(rec,filename))
          #push.Add(add_document4(rec,filename))
          counter = counter +1
        except Exception as e: 
          print(e)
          print (rec)
        #  print ("Error opening")

      #if counter>100: break
    

    # End the Push
    push.End(updateSourceStatus, deleteOlder)

if __name__ == '__main__':
    main()
