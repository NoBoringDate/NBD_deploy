import logging

import httpx
import json
import os




class API:

    url=os.environ.get('API_URL')
    
        
    @staticmethod
    def get_token():
        r=httpx.get(API.url+'/get_token')
        r=r.json()
        return r.get('token')
       # return '5391711397:AAEZlSKhJJXhid0Aaz9kcPGyTvQQZM2XHJ0'
    @staticmethod
    async def Get(route:str, params:dict={}):
        try:
            async with httpx.AsyncClient() as client:
                r=await client.get(API.url+'/'+route, params=params)
        except Exception as ex:
            logging.info(f"Get request failed:{API.url}/{route} params={params}\n  {ex}", stack_info=True)
        return r
    
    @staticmethod
    async def Post(route:str, data:dict={}):
        try:
            async with httpx.AsyncClient() as client:
                r=await client.post(API.url+'/'+route, data=json.dumps(data))
        except Exception as ex:
            logging.info(f"Post request failed:{API.url}/{route} data={data}\n  {ex}", stack_info=True)
        return r
