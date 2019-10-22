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

from aiohttp import ClientResponse


class AbstractAlmondAuth(ABC):
    """Base class to handle auth."""

    def __init__(self, host: str):
        """Initialize the auth."""
        self.host = host

    @abstractmethod
    async def post(self, url, **kwargs) -> ClientResponse:
        """Make a post request."""


class WebAlmondAPI:
    """Base class for Web Almond API."""

    def __init__(self, auth: AbstractAlmondAuth):
        """Initialize the API."""
        self.auth = auth

    async def async_converse_text(self, text: str, conversation_id : str = None) -> dict:
        """Send a text message to Almond, and return Almond's reply."""
        resp = await self.auth.post(
            "/api/converse", json={"command": {"type": "command", "text": text}, "conversationId": conversation_id}
        )

        return await resp.json()

    async def async_converse_thingtalk(self, code: str, conversation_id : str = None) -> dict:
        """Send a program to Almond to be executed, and return Almond's reply."""
        resp = await self.auth.post(
            "/api/converse", json={"command": {"type": "tt", "code": code}, "conversationId": conversation_id}
        )

        return await resp.json()
