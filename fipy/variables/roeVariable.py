#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "roeVariable.py"
 #
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
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
 #  See the file "license.terms" for information on usage and  redistribution
 #  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
 #  
 # ###################################################################
 ##

from fipy.variables.cellToFaceVariable import _CellToFaceVariable
from fipy.tools import numerix
from fipy.variables.faceVariable import FaceVariable

class _RoeVariable(FaceVariable):
    def __init__(self, var, coeff):
        super(FaceVariable, self).__init__(mesh=var.mesh, elementshape=(2,) + var.shape[:-1], cached=True)
##        self.var = self._requires(var)
        self.var = self._requires(var)
        self.coeff = self._requires(coeff)
        
    def _calcValue(self):
        id1, id2 = self.mesh._adjacentCellIDs
        mesh = self.var.mesh
        
##        ## varDown.shape = (Nequ, Nfac)
##        varDown = numerix.take(self.var, id1, axis=-1)
##        varUp = numerix.take(self.var, id2, axis=-1)

        ## coeffDown.shape = (Nequ, Nequ, Nfac)
        coeffDown = (numerix.take(self.coeff, id1, axis=-1) * mesh._orientedAreaProjections[:, numerix.newaxis, numerix.newaxis]).sum(0)
        coeffUp = (numerix.take(self.coeff, id2, axis=-1) * mesh._orientedAreaProjections[:, numerix.newaxis, numerix.newaxis]).sum(0)
        
##         ## Anumerator.shape = (Nequ, Nface)
##         Anumerator = (coeffUp * varUp[:, numerix.newaxis] \
##                       - coeffDown * varDown[:, numerix.newaxis]).sum(1)

##         ## Adenominator.shape = (Nequ, Nfac)
##         Adenominator = varUp - varDown
##         Adenominator = numerix.where(Adenominator == 0,
##                                      1e-10,
##                                      Adenominator)

##         ## A.shape = (Nequ, Nequ, Nfac)
##         A = Anumerator[:, numerix.newaxis] / Adenominator[numerix.newaxis]

        ## A.shape = (Nequ, Nequ, Nfac)
        A = (coeffUp + coeffDown) / 2.

        ## Needs to be vectorized.
        Abar = numerix.zeros(A.shape, 'd')
        for ifac in xrange(A.shape[-1]):
            eigenvalues, R = numerix.linalg.eig(A[...,ifac])
            argsort = numerix.argsort(eigenvalues)
            eigenvalues, R = eigenvalues[argsort], R[:, argsort]
            DOT = numerix.NUMERIX.dot
            Rinv = numerix.linalg.inv(R)
            Abar[...,ifac] = DOT(DOT(R, abs(eigenvalues) * numerix.identity(eigenvalues.shape[0])), Rinv)
            
        ## value.shape = (2, Nequ, Nequ, Nfac)+
        value = numerix.zeros((2,) + A.shape, 'd')
        value[0] = (coeffDown + Abar) / 2
        value[1] = (coeffUp - Abar) / 2

        return value    

            