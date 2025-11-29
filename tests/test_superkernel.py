from core.kernel.superkernel import Superkernel


def test_omega_improves_after_evolution():
    kernel = Superkernel()
    for idx in range(5):
        vector = [0.01 * (idx + 1) for _ in range(8)]
        kernel.ingest(vector, loss=0.01)

    before = kernel.omega_score()
    kernel.evolve()
    after = kernel.omega_score()
    assert after >= before
