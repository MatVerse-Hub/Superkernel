"""Core antifragile kernel with Omega/psi/theta and CVaR tracking."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence


Vector = List[float]


def _mean(values: Iterable[float]) -> float:
    total = 0.0
    count = 0
    for value in values:
        total += value
        count += 1
    return total / count if count else 0.0


def _euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _centroid(vectors: Iterable[Sequence[float]]) -> Vector:
    vectors = list(vectors)
    if not vectors:
        return []
    length = len(vectors[0])
    totals = [0.0 for _ in range(length)]
    for vector in vectors:
        for idx, value in enumerate(vector):
            totals[idx] += value
    return [value / len(vectors) for value in totals]


@dataclass
class Superkernel:
    """Simplified Superkernel implementation with antifragile metrics."""

    vectors: List[Vector] = field(default_factory=list)
    losses: List[float] = field(default_factory=list)
    nu: float = 0.8
    lam: float = 1.2
    entropy_threshold: float = 0.65
    intervention_count: int = 0
    phi_pow: int = 17

    def dynamic_cvar(self, losses: Sequence[float], alpha: float = 0.95) -> float:
        if not losses:
            return 0.0
        weights = [math.exp(self.lam * loss) for loss in losses]
        total_weight = sum(weights)
        normalized_weights = [weight / total_weight for weight in weights]
        weighted_losses = sorted(loss * weight for loss, weight in zip(losses, normalized_weights))
        cut = int((1 - alpha) * len(weighted_losses))
        return _mean(weighted_losses[cut:])

    def _psi(self) -> float:
        if len(self.vectors) < 2:
            return 1.0
        center = _centroid(self.vectors)
        return _mean(_cosine_similarity(vector, center) for vector in self.vectors)

    def _theta(self) -> float:
        if len(self.vectors) == 0:
            return 1.0
        center = _centroid(self.vectors)
        dist = _mean(_euclidean_distance(vector, center) for vector in self.vectors)
        return min(1.0, 1.0 / (dist + 1e-9))

    def omega_score(self) -> float:
        psi = self._psi()
        theta = self._theta()
        cvar = self.dynamic_cvar(self.losses[-1000:]) if self.losses else 0.0
        pole = 1.0
        return 0.4 * psi + 0.3 * theta + 0.2 * (1 - cvar) + 0.1 * pole

    def hamiltonian(self) -> float:
        omega = self.omega_score()
        cvar = self.dynamic_cvar(self.losses[-1000:]) if self.losses else 0.0
        return 1.0 / (omega**2 + 1e-9) - self.nu * cvar

    def assess_system_health(self) -> Dict[str, float]:
        return {
            "omega": self.omega_score(),
            "hamiltonian": self.hamiltonian(),
            "psi": self._psi(),
            "theta": self._theta(),
            "cvar": self.dynamic_cvar(self.losses[-1000:]) if self.losses else 0.0,
            "intervention_count": self.intervention_count,
        }

    def ingest(self, vector: Sequence[float], loss: float) -> None:
        self.vectors.append(list(vector))
        self.losses.append(loss)
        if len(self.vectors) > 10_000:
            self.vectors = self.vectors[-10_000:]
            self.losses = self.losses[-10_000:]

    def evolve(self) -> None:
        if self.hamiltonian() > 0.1:
            self.intervention_count += 1
            self.nu = min(0.95, self.nu + 0.02)
            self.lam = min(1.5, self.lam + 0.05)
            print(f"[φ∞] Evolução automática → ν={self.nu:.2f} λ={self.lam:.2f}")
