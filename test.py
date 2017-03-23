import bpy

# Delete the default starting geometry (that cube...)
# select objects by type
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.select = True
    else:
        o.select = False
# delete the selected items
bpy.ops.object.delete()

# Insert scene items
# Create material for uniform flat coloring
mat = bpy.data.materials.new('SurfaceMat')
mat.use_shadeless = True # cartoonish solid color
# Insert spheres at various locations
objects = []
for loc in [ [0,0,0], [1,3,0], ]:
    # Create sphere object
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, size=1, location=loc)
    # Use smooth shading (interpolate surface normals)
    bpy.ops.object.shade_smooth()
    # Apply our material
    ob = bpy.context.active_object
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)
    # Activate physics on this object
    bpy.ops.rigidbody.object_add()
    # Use spherical collision boundary
    ob.rigid_body.collision_shape = 'SPHERE'
    # Save this object in a list, for later access
    objects.append(ob)

# Set camera to top-down view
cam = bpy.context.scene.camera
cam.rotation_euler = [0, 0, 0]
cam.location = [0, 0, 10]
# Use orthographic projection for maximum simplicity
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 10 # meters per screen

rend = bpy.context.scene.render
rend.engine = 'BLENDER_RENDER'
rend.resolution_x = 1024
rend.resolution_y = 1024
img_folder = 'C:/Users/brunsc/projects/blender_physics'
scene = bpy.data.scenes['Scene']

# Manipulate keyframes to set initial velocity
scene = bpy.data.scenes['Scene']
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

# Save screenshot to disk
scene.render.filepath = img_folder + '/test1.png'
bpy.ops.render.render( write_still=True ) 

scene.frame_set(frame=scene.frame_start) # first frame
ob.location = loc1

# Save screenshot to disk
scene.render.filepath = img_folder + '/test2.png'
bpy.ops.render.render( write_still=True ) 
