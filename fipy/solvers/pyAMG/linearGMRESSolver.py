from __future__ import unicode_literals
from fipy.solvers.scipy.linearGMRESSolver import LinearGMRESSolver as ScipyLinearGMRESSolver
from fipy.solvers.pyAMG.preconditioners.smoothedAggregationPreconditioner import SmoothedAggregationPreconditioner

__all__ = ["LinearGMRESSolver"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class LinearGMRESSolver(ScipyLinearGMRESSolver):
    """
    The `LinearGMRESSolver` is an interface to the GMRES solver in
    Scipy, using the PyAMG `SmoothedAggregationPreconditioner` by
    default.
    """

    def __init__(self, tolerance=1e-15, iterations=2000, precon=SmoothedAggregationPreconditioner()):
        """
        Parameters
        ----------
        tolerance : float
            Required error tolerance.
        iterations : int
            Maximum number of iterative steps to perform.
        precon : ~fipy.solvers.pyAMG.preconditioners.smoothedAggregationPreconditioner.SmoothedAggregationPreconditioner, optional
        """

        super(LinearGMRESSolver, self).__init__(tolerance=tolerance, iterations=iterations, precon=precon)
