"""
Blender Python script to generate animation sequence of physically interacting objects.

Note: this script assumes cgs units, i.e. 
cgs object density is around 1.0 (gm/cm**3), and gravity is around 980.665 (cm/sec**2),
(In SI units, density would be around 1000 kg/m**3, and gravity 9.80665 m/sec**2)

Authors: Christopher M. Bruns

Copyright 2017 HHMI. All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, 
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright 
      notice, this list of conditions and the following disclaimer in the 
      documentation and/or other materials provided with the distribution.
    * Neither the name of HHMI nor the names of its contributors may be used 
      to endorse or promote products derived from this software without 
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
"""

import os
import math

import bpy

def create_shadeless_material():
    # Create material for uniform flat coloring
    mat = bpy.data.materials.new('SurfaceMat')
    mat.use_shadeless = True # cartoonish solid color
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
    def __init__(self, material, radius=1.0, density=1.0, location=[0,0,0], initial_velocity=None):
        self.initial_velocity = initial_velocity
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


def main():
    delete_all_meshes()
    set_camera_to_top_down_view()
    mat = create_shadeless_material()

    # Insert scene items
    # Insert spheres at various locations
    objects = [
            PhysicsSphere(material=mat),
            PhysicsSphere(material=mat, location=[1,3,0], initial_velocity=[])
    ]

    # Turn off gravity
    scene = bpy.data.scenes['Scene']
    scene.gravity = [0,0,0] # cm/sec**2

    rend = bpy.context.scene.render
    rend.engine = 'BLENDER_RENDER'
    rend.resolution_x = 1024
    rend.resolution_y = 1024

    # Manipulate keyframes to set initial velocity
    scene.frame_start = 1
    scene.frame_end = 101
    fps = 30.0
    v_i = [0.0, -1.0, 0.0]
    dLoc = [x / fps for x in v_i]
    # Set initial velocity by setting location in frame start-1
    ob = objects[1]
    # Select only the one object
    for obj in bpy.data.objects:
        obj.select = False
    ob.select = True
    # Location before first frame
    loc0 = [ob.location[x] - dLoc[x] for x in range(3)]
    loc1 = [x for x in ob.location]
    scene.frame_set(frame=scene.frame_start-1) # zeroth frame
    ob.rigid_body.kinematic = True
    ob.location = loc0

    src_folder = os.path.dirname(os.path.realpath(__file__))
    img_folder = os.path.join(src_folder, 'frames')
    # Save screenshot to disk
    scene.render.filepath = img_folder + '/test1.png'
    bpy.ops.render.render( write_still=True ) 

    scene.frame_set(frame=scene.frame_start) # first frame
    ob.location = loc1
    # Save screenshot to disk
    scene.render.filepath = img_folder + '/test2.png'
    bpy.ops.render.render( write_still=True ) 

if __name__ == '__main__':
    main()