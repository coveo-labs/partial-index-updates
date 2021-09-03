# Coveo Partial Updates

## Use Case
You have a Push or Catalog source.
You only have partial information available (like inventory) for updates.

Normally Push and Catalog sources do not provide a way to update the content partially.

This example will show how you can query the index to fetch all metadata (including the HTML-quickview data). How you can update the content, and push it back into your source using the Python Push SDK.


## Requirements
1. Generic parameters
 * `api_key_search`, the api key which has access to the content through the search api
 * `api_key_push`, the push api key which has the rights to push to the (source_id) source
 * `source_id`, the source id of the source which should receive the content
 * `org_id`, the org id of the Coveo organization
 * `region`, the region. Possible values: 
   * USA/Canada = empty
   * Europe = eu
   * Apac = ap
 * `type_source`, the type of source. Possible values: 
   * Catalog = empty
   * Push = push
 * `additional_query`, the additional query so that you only select the requested source. `@source==PartialUpdates`
 * `key_field`, by default we use the `uri` field to get the content from the index. Your `key` in your `newdata` structure must use the contents of the requested field in the index.
2. Data parameters
 * `newdata`, An array containing
 * `key`: the `key` field of the index to retrieve (see `key_field`)
 * `metadata`: dictionary with the keys to update

For example:
```
{
  'api_key_search':'x608e3-45c4-4bc1-9ebb-881f5100',
  'api_key_push':'xxssdfe31d-3a3b-45c9-bf0d-c9sdfsd8e60a89',
  'source_id':'coveo63nga69u-wo3e5ffo27eokwecopy',
  'org_id':'coveo63nga69u',
  'region':'',
  'type_source':'',
  'additional_query':'@source==PartialUpdates',
  'key_field':'uri',
  'newdata':
[{'key':'https://fashionstore/?id=89a99d0f55e05b94ad545bcb304699f7&col=Bandolier Brown&sz=Big',    'metadata':{'ec_brand':'wim','ec_stock':{'':20,'1':20,'2':20}}},
{'key':'https://fashionstore/?id=9fea1d85dc5a534e43b99ef2c41c03f4&col=Yellow Floral&sz=Petite','metadata':{'ec_brand':'wim','ec_stock':{'':20,'1':20,'2':20}}},
{'key':'https://fashionstore/?id=b602934bd5e96aca05bc45717a50e12f&col=Bare Necessity&sz=Regular','metadata':{'ec_stock':{'':20,'1':20,'2':20}}}]
}
```

In the example, update your settings.json with:
```
{
  "api_key_search":"",
  "api_key_push":"",
  "source_id":"",
  "org_id":""
}
```

3. Response
   For each supplied key you will get a result back if it was found or not.
For example:
```
{"https://fashionstore/?id=89a99d0f55e05b94ad545bcb304699f7&col=Bandolier Brown&sz=Big": "Found and updated", "https://fashionstore/?id=9fea1d85dc5a534e43b99ef2c41c03f4&col=Yellow Floral&sz=Petite": "Found and updated", "https://fashionstore/?id=b602934bd5e96aca05bc45717a50e12f&col=Bare Necessity&sz=Regular": "Not found"}
```

## Temporary proxy
We created an Amazon AWS REST service which takes care of this. 

Available here: [Amazon proxy url](https://rufnska662.execute-api.us-east-1.amazonaws.com/prod)

Example call: `test-api.py`

## Version
1.0 Sept 2021, Wim Nijmeijer

