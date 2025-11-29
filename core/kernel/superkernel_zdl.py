"""Zero-dependency Superkernel implementation.

This module mirrors the antifragile metric calculations of the main
``Superkernel`` but uses only the Python standard library. It is intended
for restricted environments where installing third-party dependencies
is not possible.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence


Vector = List[float]


class SuperkernelZDL:
    """Superkernel φ∞ – Zero Dependency Edition."""

    def __init__(self) -> None:
        self.vectors: List[Vector] = []
        self.losses: List[float] = []
        self.nu: float = 0.80
        self.lam: float = 1.20
        self.intervention_count: int = 0

    # ------------------------------
    # Utilities (no NumPy required)
    # ------------------------------
    def _dot(self, a: Sequence[float], b: Sequence[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def _norm(self, v: Sequence[float]) -> float:
        return math.sqrt(sum(x * x for x in v))

    def cosine_similarity(self, a: Sequence[float], b: Sequence[float]) -> float:
        na = self._norm(a)
        nb = self._norm(b)
        if na == 0.0 or nb == 0.0:
            return 0.0
        return self._dot(a, b) / (na * nb + 1e-9)

    # ------------------------------
    # Metrics
    # ------------------------------
    def _centroid(self) -> Vector:
        if not self.vectors:
            return []
        return [sum(col) / len(self.vectors) for col in zip(*self.vectors)]

    def _psi(self) -> float:
        if len(self.vectors) < 2:
            return 1.0
        centroid = self._centroid()
        sims = [self.cosine_similarity(v, centroid) for v in self.vectors]
        return sum(sims) / len(sims) if sims else 0.0

    def _theta(self) -> float:
        if len(self.vectors) == 0:
            return 1.0
        centroid = self._centroid()
        dists = [
            math.sqrt(sum((vi - ci) ** 2 for vi, ci in zip(v, centroid)))
            for v in self.vectors
        ]
        mean_dist = sum(dists) / len(dists)
        return min(1.0, 1.0 / (mean_dist + 1e-9))

    def dynamic_cvar(self, alpha: float = 0.95) -> float:
        if not self.losses:
            return 0.0
        sorted_losses = sorted(self.losses)
        cut = int(len(sorted_losses) * alpha)
        tail = sorted_losses[cut:]
        return sum(tail) / len(tail) if tail else 0.0

    def omega(self) -> float:
        psi = self._psi()
        theta = self._theta()
        cvar = self.dynamic_cvar()
        return 0.4 * psi + 0.3 * theta + 0.2 * (1 - cvar) + 0.1 * 1.0

    def hamiltonian(self) -> float:
        omega_val = self.omega()
        cvar = self.dynamic_cvar()
        return 1.0 / (omega_val * omega_val + 1e-9) - self.nu * cvar

    # ------------------------------
    # Data
    # ------------------------------
    def ingest(self, vector: Sequence[float], loss: float) -> None:
        self.vectors.append(list(vector))
        self.losses.append(loss)
        if len(self.vectors) > 10_000:
            self.vectors = self.vectors[-10_000:]
            self.losses = self.losses[-10_000:]

    # ------------------------------
    # Evolution φ∞
    # ------------------------------
    def evolve(self) -> None:
        if self.hamiltonian() > 0.1:
            self.nu = min(0.95, self.nu + 0.02)
            self.lam = min(1.5, self.lam + 0.05)
            self.intervention_count += 1
            print(f"[φ∞ ZDL] Evolução → ν={self.nu:.2f} λ={self.lam:.2f}")

    def status(self) -> Dict[str, float]:
        return {
            "omega": self.omega(),
            "hamiltonian": self.hamiltonian(),
            "psi": self._psi(),
            "theta": self._theta(),
            "cvar": self.dynamic_cvar(),
            "interventions": self.intervention_count,
        }

