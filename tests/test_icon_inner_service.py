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

"""IconScoreEngine testcase
"""

import shutil
import unittest
import time
import asyncio

from iconservice.icon_inner_service import IconScoreInnerTask
from iconservice.base.address import AddressPrefix
from tests import create_block_hash, create_address, create_tx_hash


class TestIconServiceEngine(unittest.TestCase):
    def setUp(self):
        self._state_db_root_path = '.db'
        self._icon_score_root_path = '.score'

        try:
            shutil.rmtree(self._icon_score_root_path)
            shutil.rmtree(self._state_db_root_path)
        except:
            pass

        self._inner_task = IconScoreInnerTask(self._state_db_root_path, self._icon_score_root_path)
        self._genesis_addr = create_address(AddressPrefix.EOA, b'genesis')
        self._addr1 = create_address(AddressPrefix.EOA, b'addr1')

    def tearDown(self):
        async def _run():
            await self._inner_task.close()
            shutil.rmtree(self._icon_score_root_path)
            shutil.rmtree(self._state_db_root_path)

        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_run())
        except:
            pass

    async def _genesis_invoke(self, block_index: int = 0):
        tx_hash = create_tx_hash(b'genesis')
        tx_timestamp_us = int(time.time() * 10 ** 6)
        request_params = {'txHash': tx_hash, 'timestamp': hex(tx_timestamp_us)}
        tx = {
            'method': '',
            'params': request_params,
            "accounts": [
                {
                    "name": "genesis",
                    "address": f"{self._genesis_addr}",
                    "balance": "0x2961fff8ca4a62327800000"
                },
                {
                    "name": "fee_treasury",
                    "address": "hx1000000000000000000000000000000000000000",
                    "balance": "0x0"
                }
            ],
        }

        make_request = {'transactions': [tx]}
        block_height: int = block_index
        block_timestamp_us = tx_timestamp_us
        block_hash = create_block_hash(block_timestamp_us.to_bytes(8, 'big'))

        make_request['block'] = {
            'blockHeight': hex(block_height),
            'blockHash': block_hash,
            'timestamp': hex(block_timestamp_us)
        }

        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}

        response = await self._inner_task.genesis_invoke(make_request)
        if not isinstance(response, dict):
            return await self._inner_task.remove_precommit_state(precommit_request)
        elif response[tx_hash]['status'] == hex(1):
            return await self._inner_task.write_precommit_state(precommit_request)
        else:
            return await self._inner_task.remove_precommit_state(precommit_request)

    async def _send_icx_invoke(self, addr_from, addr_to, value, block_index: int):

        request_params = {
            "from": addr_from,
            "to": addr_to,
            "value": value,
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
        }

        method = 'icx_sendTransaction'
        # Insert txHash into request params
        tx_hash = create_tx_hash(b'txHash1')
        request_params['txHash'] = tx_hash
        tx = {
            'method': method,
            'params': request_params
        }

        response = await self._inner_task.pre_validate_check(tx)

        make_request = {'transactions': [tx]}
        block_height: int = block_index
        block_timestamp_us = int(time.time() * 10 ** 6)
        block_hash = create_block_hash(block_timestamp_us.to_bytes(8, 'big'))

        make_request['block'] = {
            'blockHeight': hex(block_height),
            'blockHash': block_hash,
            'timestamp': hex(block_timestamp_us)
        }

        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}

        response = await self._inner_task.invoke(make_request)
        if not isinstance(response, dict):
            return await self._inner_task.remove_precommit_state(precommit_request)
        elif response[tx_hash]['status'] == hex(1):
            return await self._inner_task.write_precommit_state(precommit_request)
        else:
            return await self._inner_task.remove_precommit_state(precommit_request)

    def test_genesis_invoke(self):
        async def _run():
            response = await self._genesis_invoke(0)
            self.assertEqual(response, hex(0))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_run())
        except:
            pass

    def test_invoke_success(self):
        async def _run():
            response = await self._genesis_invoke(0)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 1)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 2)
            self.assertEqual(response, hex(0))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_run())
        except:
            pass

    def test_invoke_fail1(self):
        async def _run():
            response = await self._genesis_invoke(0)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 0)
            self.assertEqual(response, hex(0))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_run())
        except:
            pass

    def test_invoke_fail2(self):
        async def _run():
            response = await self._genesis_invoke(0)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 1)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 3)
            self.assertEqual(response, hex(0))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_run())
        except:
            pass

    def test_invoke_fail3(self):
        async def _run():
            response = await self._genesis_invoke(0)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 1)
            self.assertEqual(response, hex(0))
            response = await self._send_icx_invoke(self._genesis_addr, self._addr1, hex(1), 0)
            self.assertEqual(response, hex(0))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_run())
        except:
            pass



if __name__ == '__main__':
    unittest.main()