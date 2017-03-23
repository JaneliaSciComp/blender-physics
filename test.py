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
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, size=1)
bpy.ops.object.shade_smooth()

# Set camera to top-down view
cam = bpy.context.scene.camera
cam.rotation_euler = [0, 0, 0]
cam.location = [0, 0, 10]
# Use orthographic projection for maximum simplicity
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 20

# Save screenshot to disk
img_folder = 'C:/Users/brunsc/projects/blender_physics'
scene = bpy.data.scenes['Scene']
scene.render.filepath = img_folder + '/test1.png'
bpy.ops.render.render( write_still=True ) 
