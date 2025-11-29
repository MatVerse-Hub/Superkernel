"""Zero-dependency CLI entrypoint."""

from __future__ import annotations

import random

from core.kernel.superkernel_zdl import SuperkernelZDL
from core.oracle.tace_oracle_zdl import TACEOracleZDL


def main() -> None:
    kernel = SuperkernelZDL()

    # Seed with a few random vectors
    for _ in range(5):
        vector = [random.random() for _ in range(32)]
        kernel.ingest(vector, loss=random.random() * 0.03)

    oracle = TACEOracleZDL(kernel)
    oracle.run()


if __name__ == "__main__":
    main()

