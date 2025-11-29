"""Oracle that monitors Omega growth and triggers Polygon registrations."""
from __future__ import annotations

import threading
import time
from typing import Optional

from core.blockchain.polygon_integration import PolygonIntegrator
from core.kernel.superkernel import Superkernel


class TACEOracle:
    """Monitor dΩ/dt and register improvements on-chain."""

    def __init__(
        self,
        kernel: Superkernel,
        integrator: PolygonIntegrator,
        pose_contract_address: str,
        interval_seconds: int = 30,
        min_omega_gain: float = 0.0005,
    ):
        self.kernel = kernel
        self.integrator = integrator
        self.pose_contract_address = pose_contract_address
        self.interval_seconds = interval_seconds
        self.min_omega_gain = min_omega_gain
        self.history = []
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _record_state(self) -> None:
        health = self.kernel.assess_system_health()
        self.history.append({"timestamp": time.time(), **health})
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

    def _compute_d_omega_dt(self) -> float:
        if len(self.history) < 2:
            return 0.0
        dt = self.history[-1]["timestamp"] - self.history[-2]["timestamp"]
        domega = self.history[-1]["omega"] - self.history[-2]["omega"]
        return domega / dt if dt > 0 else 0.0

    def _trigger_if_needed(self) -> None:
        self._record_state()
        d_omega_dt = self._compute_d_omega_dt()
        if d_omega_dt <= 0:
            return
        omega_gain = self.history[-1]["omega"] - self.history[-2]["omega"] if len(self.history) >= 2 else 0.0
        if omega_gain >= self.min_omega_gain:
            tx_hash = self.integrator.register_metric_on_chain(
                kernel=self.kernel,
                metric_name="TACE_Evolution",
                value=self.history[-1]["omega"],
                contract_address=self.pose_contract_address,
            )
            print(f"[TACE] Ω improved by {omega_gain:.6f}; recorded on-chain at {tx_hash}")

    def _loop(self) -> None:
        while self.running:
            try:
                self.kernel.evolve()
                self._trigger_if_needed()
                time.sleep(self.interval_seconds)
            except Exception as exc:  # pragma: no cover - defensive logging
                print(f"TACE Oracle error: {exc}")
                time.sleep(self.interval_seconds)

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join()

    def status(self) -> dict:
        return {
            "running": self.running,
            "samples": len(self.history),
            "d_omega_dt": self._compute_d_omega_dt(),
        }
