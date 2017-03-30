import os
from bspheres import Simulation

sim = Simulation(sphere_count=5, random_seed=2)
# Define folder where to same image frames
src_folder = os.path.dirname(os.path.realpath(__file__))
image_folder = os.path.join(src_folder, 'frames')
sim.run(image_folder=image_folder)
