import asyncio
import os
import socket
import psutil
import requests
import aiohttp


async def runner():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://indianexpress.com/article/political-pulse/caste-census-bjp-adapting-puncturing-opposition-politics-ready-for-numbers-9975318/") as response:
            print(await response.text())


def kill_process_using_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            os.kill(conn.pid,9)
# asyncio.run(runner())
kill_process_using_port(8082)

# date ='May 1, 2025  08:29 IST'
# val= date.split(",")
# print(val[0]+" "+val[1].strip().split()[0])

# print(requests.get("https://indianexpress.com/article/business/aviation/pahalgam-attack-aftermath-india-shuts-airspace-for-pakistani-flights-in-tit-for-tat-move-9975582/").text)