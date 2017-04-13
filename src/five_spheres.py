import os
from bspheres import Simulation

# Note: all units are in centimeters/grams/seconds system
sim = Simulation(
        sphere_count=5, 
        radius_range=(0.8,1.2),
        arena_size=10.0,
        initial_velocities=(-5.0,-1.0,0.0,1.0,5.0),
        random_seed=4)
# Define folder where to save image frame files
src_folder = os.path.dirname(os.path.realpath(__file__))
image_folder = os.path.join(src_folder, 'frames28')
# Simulate and save frames
sim.run(image_folder=image_folder, resolution=[28,28])
