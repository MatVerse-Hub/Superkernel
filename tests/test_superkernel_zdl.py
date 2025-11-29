from core.kernel.superkernel_zdl import SuperkernelZDL


def test_omega_improves_after_evolution_zdl():
    kernel = SuperkernelZDL()
    for idx in range(5):
        vector = [0.01 * (idx + 1) for _ in range(8)]
        kernel.ingest(vector, loss=0.01)

    before = kernel.omega()
    kernel.evolve()
    after = kernel.omega()
    assert after >= before

