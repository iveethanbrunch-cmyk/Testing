import bpy, math, sys, os, time
from mathutils import Vector
S=os.environ['S']
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f'{S}/r3d/rig_merged.glb')
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    # bounds
    mn=Vector((1e9,)*3); mx=Vector((-1e9,)*3)
    for o in objs:
        for c in o.bound_box:
            w=o.matrix_world@Vector(c); mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
    ctr=(mn+mx)/2
    # recentre so floor at z=0, centre at origin
    for o in objs:
        o.location-=Vector((ctr.x,ctr.y,mn.z))
    # materials
    for o in objs:
        for slot in o.material_slots:
            m=slot.material
            if not m or not m.use_nodes: continue
            b=m.node_tree.nodes.get('Principled BSDF')
            col=b.inputs['Base Color'].default_value
            r,g,bb=[c for c in col[:3]]
            name=o.name
            grey = abs(r-g)<0.05 and abs(g-bb)<0.08
            if grey and 0.25<r<0.45:   # aluminium profile (linear)
                b.inputs['Metallic'].default_value=1.0; b.inputs['Roughness'].default_value=0.28; b.inputs['Base Color'].default_value=(0.55,0.57,0.6,1)
            elif grey and r<0.01:
                b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=0.5
            else:
                b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=0.42
                if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value=0.15
    sc=bpy.context.scene
    # backdrop: big curved cyc
    bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,0))
    floor=bpy.context.object
    bpy.ops.object.modifier_add(type='SUBSURF')
    mat=bpy.data.materials.new('cyc'); mat.use_nodes=True
    p=mat.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.62,0.63,0.66,1); p.inputs['Roughness'].default_value=0.6
    floor.data.materials.append(mat)
    w=sc.world or bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
    nt=w.node_tree; bg=nt.nodes['Background']; bg.inputs[0].default_value=(0.55,0.56,0.6,1); bg.inputs[1].default_value=0.25
    bg2=nt.nodes.new('ShaderNodeBackground'); bg2.inputs[0].default_value=(0.80,0.81,0.83,1); bg2.inputs[1].default_value=1.0
    lp=nt.nodes.new('ShaderNodeLightPath'); mix=nt.nodes.new('ShaderNodeMixShader'); out=nt.nodes['World Output']
    nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]); nt.links.new(bg.outputs[0],mix.inputs[1]); nt.links.new(bg2.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs[0])
    def area(name,loc,size,energy,rot_target=(0,0,0.45)):
        l=bpy.data.lights.new(name,'AREA'); l.size=size; l.energy=energy
        ob=bpy.data.objects.new(name,l); sc.collection.objects.link(ob); ob.location=loc
        d=Vector(rot_target)-Vector(loc); ob.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    area('key',(1.6,-1.8,2.2),2.0,160)
    area('fill',(-2.2,-1.2,1.2),2.5,45)
    area('rim',(-0.6,2.2,2.0),1.5,140)
    area('top',(0,0,3.0),2.5,40)
    cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
    cam.data.lens=50; cam.data.sensor_width=36
    sc.render.engine=os.environ.get('ENGINE','CYCLES'); sc.cycles.device='CPU'
    sc.cycles.samples=int(os.environ.get('SAMPLES','24')); sc.cycles.use_denoising=True
    try: sc.cycles.denoiser='OPENIMAGEDENOISE'
    except: pass
    sc.cycles.max_bounces=4
    sc.render.resolution_x=int(os.environ.get('RX','1920')); sc.render.resolution_y=int(os.environ.get('RY','1080'))
    sc.view_settings.view_transform='AgX'
    try: sc.view_settings.look='AgX - Medium High Contrast'
    except: pass
    sc.render.film_transparent=False
    sc.render.use_persistent_data=True
    sc.cycles.use_adaptive_sampling=True
    sc.cycles.adaptive_threshold=0.03
    return cam,(mx-mn)
def aim(cam,pos,target,lens=50):
    cam.location=Vector(pos); cam.data.lens=lens
    d=Vector(target)-Vector(pos); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
if __name__=='__main__':
    cam,size=build(); print('size',size)
    for o in bpy.context.scene.objects:
        if o.type=='MESH' and o.name!='Plane':
            print(o.name, [round(v,3) for v in o.dimensions])
    aim(cam,(1.7,-2.1,1.15),(0,0,0.42),50)
    bpy.context.scene.render.filepath=f'{S}/renders/test.png'
    t=time.time(); bpy.ops.render.render(write_still=True); print('render s',time.time()-t)
