import asyncio
import json
from abc import abstractmethod
from typing import Set, Optional
from urllib.request import getproxies

import aiohttp
from loguru import logger

from nonutils.command import Command


def get_sys_proxy():
    try:
        return getproxies()['http']
    except KeyError:
        return None


class ApiManager:
    def __init__(self):
        self.apis: Set[API] = set()


apimgr = ApiManager()


class ApiMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        return type.__new__(mcs, name, bases, attrs)


class API(metaclass=ApiMetaClass):
    def __init__(self, url: str,
                 cooldown: float = 0., timeout: int = 10,
                 disable: bool = False, proxy: str = get_sys_proxy()):

        self.url = url
        self.cooldown = cooldown
        self.timeout = timeout
        self.disable = disable
        self.proxy = proxy

        apimgr.apis.add(self)

    async def post(self, cmd: Command, data: dict) -> Optional[dict]:
        try:
            async with aiohttp.ClientSession() as client:
                async with client.post(self.url, data=data, timeout=self.timeout, proxy=self.proxy) as response:

                    if response.status != 200:
                        logger.warning(f"Call API failed: {self.url}, resp.status={response.status}")
                        await cmd.send_failed("无法连接到服务器")
                        return None

                    resp = json.loads(await response.text())
                    logger.debug(f"Called API: {self.url}, data={data}, resp={resp} ...")
                    return resp

        except asyncio.TimeoutError:
            logger.warning(f"Call API timeout: {self.url}")
            await cmd.send_failed("请求超时")


    async def get(self, cmd: Command) -> Optional[dict]:
        try:

            async with aiohttp.ClientSession() as client:
                async with client.get(self.url, timeout=self.timeout, proxy=self.proxy) as response:
                    if response.status != 200:
                        logger.error(f"Call API failed: {self.url}, resp.status={response.status}")
                        await cmd.send_failed("无法连接到服务器")
                        return None

                    resp = json.loads(await response.text())
                    logger.debug(f"Called API: {self.url}, resp={resp} ...")
                    return resp

        except asyncio.TimeoutError:
            logger.warning(f"Call API timeout: {self.url}")
            await cmd.send_failed("请求超时")

    @abstractmethod
    async def test(self) -> bool:
        raise NotImplementedError
