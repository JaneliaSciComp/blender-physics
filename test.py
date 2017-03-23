import bpy

print ("Hello")

folder = 'C:/Users/brunsc/projects/blender_physics'
bpy.data.scenes['Scene'].render.filepath = folder + '/test1.png'
bpy.ops.render.render( write_still=True ) 

