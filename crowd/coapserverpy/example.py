import logging
import asyncio
import json

from aiocoap import *
logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def main():
    protocol = yield from Context.create_client_context()

    jsonarr = []
    data = {}
    data['user'] = 1414
    jsonarr.append(data)
    json_arr = json.dumps(jsonarr)
    json_obj = json.dumps(data)

    bytereprArr = str.encode(json_arr)
    bytereprObj = str.encode(json_obj)

    # coap://130.136.37.15:5683/get_subscriptions
    request = Message(code=POST, payload=bytereprArr)
    request.opt.uri_host = '130.136.37.15'
    request.opt.uri_path = ("get_subscriptions",)

    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
