"""Minimal Polygon RPC client using only the standard library."""

from __future__ import annotations

import json
import urllib.request


class PolygonRPC:
    def __init__(self, rpc: str = "https://polygon-rpc.com/") -> None:
        self.rpc = rpc
        self._id = 1

    def call(self, method: str, params: list) -> dict:
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": self._id,
                "method": method,
                "params": params,
            }
        ).encode()

        request = urllib.request.Request(
            self.rpc, data=payload, headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())

    def block_number(self) -> int:
        result = self.call("eth_blockNumber", [])
        return int(result["result"], 16)

