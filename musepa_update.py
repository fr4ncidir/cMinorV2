#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cCoap.py
#
#  Copyright 2020 Francesco Antoniazzi <francesco.antoniazzi@emse.fr>

import asyncio
import argparse

from aiocoap import Context, Message, POST


async def update_call(address, payload, ttl=False):
    context = await Context.create_client_context()

    update_address = "coap://{}/sparql/update".format(address)
    if ttl:
        update_address += "?format=ttl"
        
    request = Message(code=POST, payload=payload.encode(), uri=update_address)
    response = await context.request(request).response
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tool to make updates to MUSEPA!")
    parser.add_argument("-a", "--address", required=True, help="Example: 127.0.0.1:5476 or 127.0.0.1 or 192.168.1.13...")
    parser.add_argument("-p", "--payload", required=True)
    parser.add_argument("--ttl", default=False, help="Add this if the payload is formatted in ttl")
    args = parser.parse_args()

    result = asyncio.get_event_loop().run_until_complete(update_call(args.address, args.payload, ttl=args.ttl))

    print("Response code: %s\nServer answer : %s\nServer info : %r " % (result.code, result.payload.decode(), result.remote))
    