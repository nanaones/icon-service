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

from threading import Lock
from ..base.address import Address
from ..base.message import Message
from ..base.transaction import Transaction
from ..base.exception import IconScoreBaseException
from ..icx.icx_engine import IcxEngine
from .icon_score_info_mapper import IconScoreInfoMapper


class IconScoreContext(object):
    """Provides the current context to IconScore including state, utilities and so on.
    """

    def __init__(self,
                 readonly: bool = False,
                 score_address: Address = None,
                 icx_engine: IcxEngine = None,
                 tx: Transaction = None,
                 msg: Message = None) -> None:
        """Constructor

        :param readonly: whether state change is possible or not
        :param icx_engine:
        :param tx: initial transaction info
        :param msg: message call info
        """
        self.readonly = readonly
        self.__score_address = score_address
        self.__icx_engine = icx_engine
        self.tx = tx
        self.msg = msg
        self.__score_mapper = IconScoreInfoMapper()

    @property
    def address(self) -> Address:
        """The address of the current icon score

        :return: the address of context owner
        """
        return self.__score_address

    def gasleft(self) -> int:
        """Returns the amount of gas left

        If gasleft is zero before tx handling is complete,
        rollback all changed state for the tx
        Consumed gas doesn't need to be paid back to tx owner.

        :return: the amount of gas left
        """
        return 0

    def get_balance(self, address: Address) -> int:
        """Returns the icx balance of context owner (icon score)

        :return: the icx amount of balance
        """
        return self.__icx_engine.get_balance(address)

    def transfer(self, to: Address, amount: int) -> bool:
        """Transfer the amount of icx to the account indicated by 'to'.

        If failed, an exception will be raised.

        :param to: recipient address
        :param amount: icx amount in loop (1 icx == 1e18 loop)
        """
        return self.__icx_engine._transfer(self.address, to, amount)

    def send(self, to: Address, amount: int) -> bool:
        """Send the amount of icx to the account indicated by 'to'.

        :param to: recipient address
        :param amount: icx amount in loop (1 icx == 1e18 loop)
        :return: True(success), False(failure)
        """
        try:
            return self.__icx_engine._transfer(self.address, to, amount)
        except:
            pass

        return False

    def call(self, addr_to: Address, func_name: str, *args, **kwargs)-> None:
        """Call the functions provided by other icon scores.

        :param addr_to:
        :param func_name:
        :param args:
        :param kwargs:
        :return:
        """

        if addr_to == self.__score_address:
            raise IconScoreBaseException("call my score's function")

        icon_score_info = self.__score_mapper.get(addr_to)
        icon_score = icon_score_info.get_icon_score(self.readonly)
        icon_score.call_method(func_name, *args, **kwargs)

    def selfdestruct(self, recipient: Address) -> None:
        """Destroy the current icon score, sending its funds to the given address

        :param recipient: fund recipient
        """

    def revert(self, message: str=None) -> None:
        """Abort execution and revert state changes

        :param message: error log message
        """

    def clear(self) -> None:
        pass


class IconScoreContextFactory(object):
    def __init__(self, max_size: int) -> None:
        self._lock = Lock()
        self._queue = []
        self._max_size = max_size

    def create(self) -> IconScoreContext:
        with self._lock:
            if len(self._queue) > 0:
                return self._queue.pop()

        return IconScoreContext()

    def destroy(self, context: IconScoreContext) -> None:
        with self._lock:
            if len(self._queue) < self._max_size:
                context.clear()
                self._queue.append(context)
