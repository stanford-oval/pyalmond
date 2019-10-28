# Copyright 2019 The Board of Trustees of the Leland Stanford Junior University
#
# Author: Paulus Schoutsen <hello@home-assistant.io>
#         Giovanni Campagna <gcampagn@cs.stanford.edu>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Python package to communicate with Almond."""
from abc import ABC, abstractmethod

from aiohttp import ClientResponse, ClientSession


class AbstractAlmondAuth(ABC):
    """Base class to handle auth."""

    def __init__(self, host: str, websession: ClientSession):
        """Initialize the auth."""
        self.host = host
        self._websession = websession

    @abstractmethod
    async def async_get_auth_headers(self) -> dict:
        """Get the request auth headers."""

    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get('headers')

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        headers.update(await self.async_get_auth_headers())

        return await self._websession.request(
            method,
            f"{self.host}{url}",
            **kwargs,
            headers=headers,
        )


class AlmondLocalAuth(AbstractAlmondAuth):
    """Base class for talking to a local Almond API."""

    async def async_get_auth_headers(self) -> dict:
        """Get the request auth headers."""
        return {"origin": "http://127.0.0.1:3000"}


class AbstractAlmondWebAuth(AbstractAlmondAuth):
    """Base class for talking to the Almond Web API."""

    @abstractmethod
    async def async_get_access_token(self):
        """Return a valid access token."""

    async def async_get_auth_headers(self) -> dict:
        """Get the request auth headers."""
        access_token = await self.async_get_access_token()
        return {"Authorization": f"Bearer {access_token}"}


class WebAlmondAPI:
    """Base class for Web Almond API."""

    def __init__(self, auth: AbstractAlmondAuth):
        """Initialize the API."""
        self.auth = auth

    async def async_list_apps(self):
        """List apps running in this Almond."""
        resp = await self.auth.request("get", "/api/apps/list")
        resp.raise_for_status()
        return await resp.json()

    async def async_create_device(self, config):
        """Configure a new device, by passing the full configuration dictionary"""
        assert isinstance(config, dict) and 'kind' in config
        resp = await self.auth.request("post", "/api/devices/create", json=config)
        resp.raise_for_status()
        return await resp.json()

    async def async_create_simple_device(self, kind):
        """Configure a new simple device that has no authentication, by passing only the Thingpedia ID"""
        return await self.async_create_device(dict(kind=kind))

    async def async_list_devices(self):
        """List devices configured in this Almond."""
        resp = await self.auth.request("get", "/api/devices/list")
        resp.raise_for_status()
        return await resp.json()

    async def async_converse_text(self, text: str, conversation_id: str = None) -> dict:
        """Send a text message to Almond, and return Almond's reply."""
        resp = await self.auth.request(
            "post", "/api/converse", json={"command": {"type": "command", "text": text},
                                           "conversationId": conversation_id}
        )
        resp.raise_for_status()
        return await resp.json()

    async def async_converse_thingtalk(self, code: str, conversation_id: str = None) -> dict:
        """Send a program to Almond to be executed, and return Almond's reply."""
        resp = await self.auth.request(
            "post", "/api/converse", json={"command": {"type": "tt", "code": code}, "conversationId": conversation_id}
        )
        resp.raise_for_status()
        return await resp.json()
