# -*- coding: utf-8 -*-

# Copyright 2017-2018 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .address import Address


class Message(object):
    """Data which is sent to receipt through icx_sendTransaction json-rpc api
    """

    def __init__(self, sender: Optional['Address']=None, value: int=0) -> None:
        """Constructor

        :param sender: sender of the message (current call)
        :param value: number of loop sent with the message
        """
        # sender of the message (current call)
        self.sender = sender
        # number of loop sent with the message
        self.value = value
