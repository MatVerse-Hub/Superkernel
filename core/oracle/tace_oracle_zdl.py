"""Thread-free TACE oracle using the zero-dependency kernel."""

from __future__ import annotations

import time
from typing import Dict

from core.kernel.superkernel_zdl import SuperkernelZDL


class TACEOracleZDL:
    """Minimal oracle that advances the kernel and reports Ω improvements."""

    def __init__(self, kernel: SuperkernelZDL, interval: int = 5) -> None:
        self.kernel = kernel
        self.interval = interval
        self.last_omega = kernel.omega()

    def step(self) -> None:
        self.kernel.evolve()
        new_omega = self.kernel.omega()
        if new_omega > self.last_omega:
            print(f"[TACE ZDL] Ω ↑ {self.last_omega:.5f} → {new_omega:.5f}")
        self.last_omega = new_omega

    def run(self, steps: int = 20) -> None:
        for _ in range(steps):
            self.step()
            time.sleep(self.interval)

    def status(self) -> Dict[str, float]:
        return {
            "omega": self.last_omega,
            "interval": self.interval,
        }

