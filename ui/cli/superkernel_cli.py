"""CLI to run the Superkernel with Polygon and the TACE Oracle."""
from __future__ import annotations

import os
import random
import time

from core.blockchain.polygon_integration import PolygonIntegrator
from core.kernel.superkernel import Superkernel
from core.oracle.tace_oracle import TACEOracle


def main() -> None:
    kernel = Superkernel()
    for _ in range(3):
        vector = [random.random() for _ in range(16)]
        kernel.ingest(vector, loss=random.random() * 0.05)

    private_key = os.getenv("POLYGON_PRIVATE_KEY")
    pose_contract_address = os.getenv("POSE_CONTRACT_ADDRESS")
    if not pose_contract_address:
        raise RuntimeError("POSE_CONTRACT_ADDRESS must be configured before running the CLI")

    integrator = PolygonIntegrator(private_key=private_key)
    print(f"Connected to Polygon as {integrator.address}")
    print(f"Current balance: {integrator.get_balance():.6f} MATIC")

    oracle = TACEOracle(
        kernel=kernel,
        integrator=integrator,
        pose_contract_address=pose_contract_address,
        interval_seconds=int(os.getenv("TACE_INTERVAL", "45")),
        min_omega_gain=float(os.getenv("TACE_MIN_GAIN", "0.0005")),
    )
    oracle.start()

    try:
        while True:
            status = oracle.status()
            health = kernel.assess_system_health()
            print(
                f"Ω={health['omega']:.6f} | H={health['hamiltonian']:.6f} | dΩ/dt={status['d_omega_dt']:.6f} | samples={status['samples']}"
            )
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down oracle...")
        oracle.stop()


if __name__ == "__main__":
    main()
