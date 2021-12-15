import numpy as np
import sys, h5py, os

# Get path to mcdc (not necessary if mcdc is installed)
sys.path.append('../')

import mcdc

# =============================================================================
# Set materials
# =============================================================================

SigmaC = np.array([1.0])
SigmaS = np.array([[0.0]])
SigmaF = np.array([[0.0]])
nu     = np.array([0.0])
M1 = mcdc.Material(SigmaC, SigmaS, SigmaF, nu)

SigmaC = np.array([1.5])
M2 = mcdc.Material(SigmaC, SigmaS, SigmaF, nu)

SigmaC = np.array([2.0])
M3 = mcdc.Material(SigmaC, SigmaS, SigmaF, nu)

# =============================================================================
# Set cells
# =============================================================================

# Set surfaces
S0 = mcdc.SurfacePlaneX(0.0, "vacuum")
S1 = mcdc.SurfacePlaneX(2.0, "transmission")
S2 = mcdc.SurfacePlaneX(4.0, "transmission")
S3 = mcdc.SurfacePlaneX(6.0, "vacuum")

# Set cells
C1 = mcdc.Cell([+S0, -S1], M2)
C2 = mcdc.Cell([+S1, -S2], M3)
C3 = mcdc.Cell([+S2, -S3], M1)
cells = [C1, C2, C3]

# =============================================================================
# Set source
# =============================================================================

# Position distribution
pos = mcdc.DistPoint(mcdc.DistUniform(0.0,6.0), mcdc.DistDelta(0.0), 
                             mcdc.DistDelta(0.0))
# Direction distribution
dir = mcdc.DistPointIsotropic()

# Energy group distribution
g = mcdc.DistDelta(0)

# Time distribution
time= mcdc.DistDelta(0.0)

# Create the source
Src = mcdc.SourceSimple(pos,dir,g,time)
sources = [Src]

# =============================================================================
# Set filters and tallies
# =============================================================================

spatial_filter = mcdc.FilterPlaneX(np.linspace(0.0, 6.0, 61))

T = mcdc.Tally('tally', scores=['flux', 'flux-face', 'current', 'current-face'], 
               spatial_filter=spatial_filter)

tallies = [T]

# =============================================================================
# Set and run simulator
# =============================================================================

# Set speed
speeds = np.array([1.0])

# Set simulator
simulator = mcdc.Simulator(speeds, cells, sources, tallies=tallies, 
                           N_hist=10000)

def test_regression_slab_uniform():
    # Run
    simulator.run()

    # Ans
    with h5py.File('output.h5', 'r') as f:
        phi         = f['tally/flux/mean'][:]
        phi_sd      = f['tally/flux/sdev'][:]
        phi_face    = f['tally/flux-face/mean'][:]
        phi_face_sd = f['tally/flux-face/sdev'][:]
        J         = f['tally/current/mean'][:,0]
        J_sd      = f['tally/current/sdev'][:,0]
        J_face    = f['tally/current-face/mean'][:,0]
        J_face_sd = f['tally/current-face/sdev'][:,0]
    os.remove('output.h5')

    # Sol
    with h5py.File('test_regression_slab_uniform_solution_h5', 'r') as f:
        phi_ref         = f['tally/flux/mean'][:]
        phi_sd_ref      = f['tally/flux/sdev'][:]
        phi_face_ref    = f['tally/flux-face/mean'][:]
        phi_face_sd_ref = f['tally/flux-face/sdev'][:]
        J_ref         = f['tally/current/mean'][:,0]
        J_sd_ref      = f['tally/current/sdev'][:,0]
        J_face_ref    = f['tally/current-face/mean'][:,0]
        J_face_sd_ref = f['tally/current-face/sdev'][:,0]

    assert phi.all() == phi_ref.all()
    assert phi_sd.all() == phi_sd_ref.all()
    assert phi_face.all() == phi_face_ref.all()
    assert phi_face_sd.all() == phi_face_sd_ref.all()
    assert J.all() == J_ref.all()
    assert J_sd.all() == J_sd_ref.all()
    assert J_face.all() == J_face_ref.all()
    assert J_face_sd.all() == J_face_sd_ref.all()
