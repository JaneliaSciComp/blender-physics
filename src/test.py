"""
Blender Python script to generate animation sequence of physically interacting objects.

Note: this script assumes cgs units, i.e. 
cgs object density is around 1.0 (gm/cm**3), and gravity is around 980.665 (cm/sec**2),
(In SI units, density would be around 1000 kg/m**3, and gravity 9.80665 m/sec**2)

Authors: Christopher M. Bruns

Copyright (c) 2017, Howard Hughes Medical Institute, All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the 
       documentation and/or other materials provided with the distribution.
    3. Neither the name of the Howard Hughes Medical Institute nor the names 
       of its contributors may be used to endorse or promote products derived 
       from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, ANY 
IMPLIED WARRANTIES OF MERCHANTABILITY, NON-INFRINGEMENT, OR FITNESS FOR A 
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
REASONABLE ROYALTIES; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Standard libraries
import os
import math

# Third party libraries
# import numpy

# Local libraries
import bpy #@UnresolvedImport

def create_shadeless_material(intensity=0.5):
    # Create material for uniform flat coloring
    mat = bpy.data.materials.new('SurfaceMat')
    mat.use_shadeless = True # cartoonish solid color
    # Use grayscale color based on intensity argument
    mat.diffuse_color = (intensity, intensity, intensity)
    return mat

def delete_all_meshes():
    """
    Clears the scene of all existing mesh objects.
    Such as that initial default cube.
    """
    # Delete the default starting geometry (that cube...)
    # select objects by type
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.select = True
        else:
            o.select = False
    # delete the selected items
    bpy.ops.object.delete()

def set_camera_to_top_down_view(cm_per_screen=10):
    cam = bpy.context.scene.camera
    cam.rotation_euler = [0, 0, 0]
    cam.location = [0, 0, 10]
    # Use orthographic projection for maximum simplicity
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = cm_per_screen

class PhysicsSphere(object):
    """
    Represents one spherical body in a Blender physics simulation
    """
    def __init__(self, material, radius=1.0, density=1.0, location=[0,0,0]):
        # Create sphere object
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, size=radius, location=location)
        self.object = bpy.context.active_object
        # Use smooth shading (interpolate surface normals)
        bpy.ops.object.shade_smooth()
        # Apply our material
        if self.object.data.materials:
            self.object.data.materials[0] = material
        else:
            self.object.data.materials.append(material)
        # Activate physics on this object
        bpy.ops.rigidbody.object_add()
        # Use perfect spherical collision boundary
        self.object.rigid_body.collision_shape = 'SPHERE'
        # Assign mass based on density
        volume = 4.0 / 3.0 * math.pi * radius**3
        self.object.rigid_body.mass = density * volume

    def __getattr__(self, attr):
        "Delegate properties (select, rigid_body, location, etc.) to contained instance"
        return getattr(self.object, attr)

    def set_initial_velocity(self, velocity, time_step):
        # Manipulate keyframes to set initial velocity
        ob = self
        # Location before first frame
        loc0 = ob._compute_initial_location(velocity, time_step)
        loc1 = [x for x in ob.location]
        # First two frames are used to kinematically set up initial velocity
        ob.rigid_body.kinematic = True
        ob.object.location = loc0
        ob.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
        ob.keyframe_insert(data_path='location', frame=1)
        ob.object.location = loc1
        ob.keyframe_insert(data_path='location', frame=2)
        # Physics begins on frame 3
        ob.rigid_body.kinematic = False
        ob.keyframe_insert(data_path='rigid_body.kinematic', frame=3)

    def _compute_initial_location(self, initial_velocity, time):
        if time == 0.0:
            return self.location
        loc_t = [self.location[x] - time * initial_velocity[x] for x in range(3)]
        return loc_t

def render_frames(count=51):
    # Render frames of simulation
    rend = bpy.context.scene.render
    rend.engine = 'BLENDER_RENDER'
    rend.resolution_x = 128
    rend.resolution_y = 128
    # Umm... Yes, render at the size I just told you.
    rend.resolution_percentage = 100
    # Avoid anti-aliasing, to minimize the number of different pixel colors
    rend.use_antialiasing = False
    src_folder = os.path.dirname(os.path.realpath(__file__))
    img_folder = os.path.join(src_folder, 'frames')
    scene = bpy.data.scenes['Scene']
    scene.frame_start = 1
    scene.frame_end = count + 1
    # Use a black background
    scene.world.horizon_color = (0,0,0)
    for f in range(1,scene.frame_end+1):
        scene.frame_set(f)
        # Skip first frame, which is kinematic only, not physics
        if f <= 1:
            continue
        scene.render.filepath = img_folder + '/test%d.png' % (f - 1)
        bpy.ops.render.render( write_still=True )

def main():
    delete_all_meshes()
    set_camera_to_top_down_view()
    mat1 = create_shadeless_material(0.5)
    mat2 = create_shadeless_material(0.75)
    # Turn off gravity
    scene = bpy.data.scenes['Scene']
    scene.gravity = [0,0,0] # cm/sec**2
    # Insert spheres at various locations
    objects = [
            PhysicsSphere(material=mat1, location=[0,0,0]),
            PhysicsSphere(material=mat2, location=[1,3,0]),
    ]
    # Set initial velocity so something could happen
    fps = 24.0
    objects[1].set_initial_velocity([0, -5, 0], 1.0/fps)
    render_frames(51)

if __name__ == '__main__':
    main()
