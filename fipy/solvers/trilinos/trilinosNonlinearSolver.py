#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "trilinosNonlinearSolver.py"
 #
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #  Author: David Saylor <David.Saylor@fda.hhs.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 # ###################################################################
 ##

from PyTrilinos import Epetra
from PyTrilinos import NOX

from fipy.solvers.trilinos.trilinosSolver import TrilinosSolver
from fipy.tools import parallel

class _NOXInterface(NOX.Epetra.Interface.Required):
    def __init__(self, var, equation, overlappingMap, nonOverlappingMap, jacobian=None):
        self.var = var
        self.equation = equation
        self.overlappingMap = overlappingMap
        self.nonOverlappingMap = nonOverlappingMap
        self.jacobian = jacobian
        NOX.Epetra.Interface.Required.__init__(self)
        
    def computeF(self, u, F, flag):
        try:
            overlappingVector = Epetra.Vector(self.overlappingMap, self.var)
            
            overlappingVector.Import(u, 
                                     Epetra.Import(self.overlappingMap, 
                                                   self.nonOverlappingMap), 
                                     Epetra.Insert)

            self.var.value = u
            F[:] = self.equation.justResidualVector(dt=self.dt)
            return True
            
        except Exception, e:
            print "TrilinosNonlinearSolver.computeF() has thrown an exception:"
            print str(type(e))[18:-2] + ":", e
            return False
            
    
class TrilinosNonlinearSolver(TrilinosSolver):
    def __init__(self, equation, jacobian=None, tolerance=1e-10, iterations=1000, steps=None, precon=None):
        TrilinosSolver.__init__(self, tolerance=tolerance, iterations=iterations, precon=precon)
        
        self.nlParams = NOX.Epetra.defaultNonlinearParameters(parallel.epetra_comm, 2)
        self.nlParams["Printing"] = {
            'Output Precision': 3, 
            'MyPID': 0, 
            'Output Information': 0, 
            'Output Processor': 0
        }
        self.nlParams["Solver Options"] =  {
            'Status Test Check Type': 'Complete', 
            'Rescue Bad Newton Solve': 'True'
        }
        self.nlParams["Linear Solver"] = {
            'Aztec Solver': 'GMRES', 
            'Tolerance': 0.0001, 
            'Max Age Of Prec': 5, 
            'Max Iterations': 20, 
            'Preconditioner': 'Ifpack'
        }
        self.nlParams["Line Search"] = {'Method': "Polynomial"}
        self.nlParams["Direction"] = {'Method': 'Newton'}
        self.nlParams["Newton"] = {'Forcing Term Method': 'Type 2'}
        
        equation._prepareLinearSystem(var=None, solver=self, boundaryConditions=(), dt=1.)
        
        globalMatrix, nonOverlappingVector, nonOverlappingRHSvector, overlappingVector = self._globalMatrixAndVectors
        
        #define the NOX interface 
        self.overlappingMap = globalMatrix.overlappingMap
        self.nonOverlappingMap = globalMatrix.nonOverlappingMap
        
        self.nox = _NOXInterface(var=self.var, equation=equation, jacobian=jacobian, 
                                 overlappingMap=self.overlappingMap,
                                 nonOverlappingMap=self.nonOverlappingMap)
        
        # Define the Jacobian interface/operator
        self.mf = NOX.Epetra.MatrixFree(self.nlParams["Printing"], self.nox, nonOverlappingVector)

        # Define the Preconditioner interface/operator
        self.fdc = NOX.Epetra.FiniteDifferenceColoring(self.nlParams["Printing"], self.nox,
                                                       nonOverlappingVector, globalMatrix.matrix.Graph(), True)

    def solve(self, dt=1.):
        self.nox.dt = dt
        
        mesh = self.var.mesh
        localNonOverlappingCellIDs = mesh._localNonOverlappingCellIDs
        nonOverlappingVector = Epetra.Vector(self.nonOverlappingMap, 
                                             self.var[localNonOverlappingCellIDs])

        solver = NOX.Epetra.defaultSolver(nonOverlappingVector, 
                                          self.nox, self.mf, self.mf, self.fdc, self.fdc, self.nlParams,
                                          absTol=self.tolerance, relTol=0.5, maxIters=self.iterations, 
                                          updateTol=None, wAbsTol=None, wRelTol=None)
        output = solver.solve()
        
#         if os.environ.has_key('FIPY_VERBOSE_SOLVER'):
#             status = Solver.GetAztecStatus()
# 
#             from fipy.tools.debug import PRINT        
#             PRINT('iterations: %d / %d' % (status[AztecOO.AZ_its], self.iterations))
#             failure = {AztecOO.AZ_normal : 'AztecOO.AZ_normal',
#                        AztecOO.AZ_param : 'AztecOO.AZ_param',
#                        AztecOO.AZ_breakdown : 'AztecOO.AZ_breakdown',
#                        AztecOO.AZ_loss : 'AztecOO.AZ_loss',
#                        AztecOO.AZ_ill_cond : 'AztecOO.AZ_ill_cond',
#                        AztecOO.AZ_maxits : 'AztecOO.AZ_maxits'}
# 
#             PRINT('failure',failure[status[AztecOO.AZ_why]])
#                                
#             PRINT('AztecOO.AZ_r:',status[AztecOO.AZ_r])
#             PRINT('AztecOO.AZ_scaled_r:',status[AztecOO.AZ_scaled_r])
#             PRINT('AztecOO.AZ_rec_r:',status[AztecOO.AZ_rec_r])
#             PRINT('AztecOO.AZ_solve_time:',status[AztecOO.AZ_solve_time])
#             PRINT('AztecOO.AZ_Aztec_version:',status[AztecOO.AZ_Aztec_version])
        
        return output