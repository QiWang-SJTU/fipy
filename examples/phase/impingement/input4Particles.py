#!/usr/bin/env python

## 
 # ###################################################################
 #  PyFiVol - Python-based finite volume PDE solver
 # 
 #  FILE: "input.py"
 #                                    created: 11/17/03 {10:29:10 AM} 
 #                                last update: 4/2/04 {4:06:17 PM}
 #  Author: Jonathan Guyer
 #  E-mail: guyer@nist.gov
 #  Author: Daniel Wheeler
 #  E-mail: daniel.wheeler@nist.gov
 #    mail: NIST
 #     www: http://ctcms.nist.gov
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  PFM is an experimental
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
 #  Description: 
 # 
 #  History
 # 
 #  modified   by  rev reason
 #  ---------- --- --- -----------
 #  2003-11-17 JEG 1.0 original
 # ###################################################################
 ##

from __future__ import nested_scopes
from fipy.examples.phase.examples.impingement.input import ImpingementSystem
import Numeric

class System4Particles(ImpingementSystem):

    def initialConditions(self, Lx = None, Ly = None):
        pi = Numeric.pi
        def circle(cell, a = 0., b = 0., r = 1.):
            x = cell.getCenter()[0]
            y = cell.getCenter()[1]
            if ((x - a)**2 + (y - b)**2) < r**2:
                return 1.

        cells = self.mesh.getCells()
        self.phase.setValue(0., cells)
        self.theta.setValue(-pi + 0.0001, cells)

        circleCenters = ((0., 0.), (Lx, 0.), (0., Ly), (Lx, Ly))
        thetaValue = (2. * pi / 3., -2. * pi / 3., -2. * pi / 3. + 0.3, 2. * pi / 3.)
        for i in range(4):
            aa = circleCenters[i][0]
            bb = circleCenters[i][1]
            cells = self.mesh.getCells(circle, a = aa, b = bb, r = Lx / 2)
            self.phase.setValue(1., cells)
            self.theta.setValue(thetaValue[i],cells)

        
if __name__ == '__main__':
    n = 100
    system = System4Particles(nx = n, ny = n, steps = 100, drivingForce = 10.)
    system.run()

    
