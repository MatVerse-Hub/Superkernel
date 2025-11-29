"""Polygon Mainnet integration for recording Superkernel metrics."""
from __future__ import annotations

import importlib
import json
import os
from typing import Optional

from dotenv import load_dotenv

from core.kernel.superkernel import Superkernel

load_dotenv()


class PolygonIntegrator:
    """Connects to Polygon and registers Superkernel metrics on-chain."""

    def __init__(self, private_key: Optional[str] = None, rpc_url: Optional[str] = None):
        web3_module = importlib.import_module("web3")
        middleware_module = importlib.import_module("web3.middleware")
        account_module = importlib.import_module("eth_account")

        Web3 = getattr(web3_module, "Web3")
        geth_poa_middleware = getattr(middleware_module, "geth_poa_middleware")
        Account = getattr(account_module, "Account")

        self.rpc_url = rpc_url or os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com/")
        self.chain_id = int(os.getenv("POLYGON_CHAIN_ID", "137"))
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Polygon RPC at {self.rpc_url}")

        key = private_key or os.getenv("POLYGON_PRIVATE_KEY")
        if key:
            self.account = Account.from_key(key)
        else:
            self.account = Account.create()
        self.address = self.account.address

    def get_balance(self, address: Optional[str] = None) -> float:
        target = address or self.address
        balance_wei = self.w3.eth.get_balance(target)
        return float(self.w3.from_wei(balance_wei, "ether"))

    def deploy_pose_contract(self, contract_abi: str, bytecode: str) -> str:
        abi = json.loads(contract_abi) if isinstance(contract_abi, str) else contract_abi
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        nonce = self.w3.eth.get_transaction_count(self.address)
        gas_price = self.w3.eth.gas_price
        gas_estimate = contract.constructor().estimate_gas({"from": self.address})

        tx = contract.constructor().build_transaction(
            {
                "chainId": self.chain_id,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce,
            }
        )

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1:
            raise ValueError("PoSE contract deployment failed")
        return receipt.contractAddress

    def register_metric_on_chain(
        self, kernel: Superkernel, metric_name: str, value: float, contract_address: str
    ) -> str:
        contract_abi = json.loads(os.getenv("POSE_ABI", "[]"))
        contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

        nonce = self.w3.eth.get_transaction_count(self.address)
        gas_price = self.w3.eth.gas_price

        tx = contract.functions.registerMetric(metric_name, int(value * 1e6)).build_transaction(
            {
                "chainId": self.chain_id,
                "gasPrice": gas_price,
                "nonce": nonce,
            }
        )

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()

    def evolve_via_tace(self, kernel: Superkernel, contract_address: str) -> Optional[str]:
        old_omega = kernel.omega_score()
        kernel.evolve()
        new_omega = kernel.omega_score()
        if new_omega > old_omega:
            return self.register_metric_on_chain(
                kernel=kernel,
                metric_name="Omega_Evolution",
                value=new_omega,
                contract_address=contract_address,
            )
        return None
