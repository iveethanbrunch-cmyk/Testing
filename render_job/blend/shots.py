import bpy,os,sys,math,time,json
sys.path.insert(0,os.environ['S']+'/blend')
from scene import build, aim
from mathutils import Vector
S=os.environ['S']; OUT=os.environ.get('OUT','frames'); FPS=int(os.environ.get('FPS','24'))
SHOTS={
 # name: (dur, [pos0,tgt0,lens0],[pos1,tgt1,lens1])
 'hero':   (7.0, [(-1.9,-2.0,0.55),(0,0,0.45),55], [(1.9,-2.0,0.75),(0,0,0.45),55]),
 'rise':   (5.0, [(0.0,-2.6,0.25),(0,0,0.40),40], [(0.0,-2.3,1.45),(0,0,0.45),40]),
 'feeder': (5.0, [(-1.0,-0.95,0.95),(-0.22,0.05,0.62),70], [(-0.55,-1.15,0.85),(-0.12,0.05,0.6),70]),
 'form':   (5.0, [(0.55,-0.85,0.85),(0.03,0.1,0.58),85], [(0.25,-0.95,0.70),(0.03,0.1,0.58),85]),
 'hopper': (5.0, [(0.75,-1.0,0.55),(0.05,0.08,0.45),60], [(0.65,-1.1,0.35),(0.05,0.08,0.22),60]),
 'high':   (8.0, [(-1.2,-1.5,1.9),(0,0.02,0.42),42], [(1.0,-1.7,1.9),(0,0.02,0.42),42]),
 'end':    (7.0, [(2.0,-1.6,0.95),(0,0,0.45),50], [(2.6,-2.2,0.85),(0,0,0.42),50]),
}
SHIFT={'hero':-0.17,'end':-0.17,'rise':-0.08,'high':0.17}
def ease(t): return t*t*(3-2*t)
def lerp(a,b,t): return tuple(x+(y-x)*t for x,y in zip(a,b))
cam,_=build()
sc=bpy.context.scene
names=os.environ.get('SHOTS',','.join(SHOTS)).split(',')
only=os.environ.get('ONLY')  # 'first' for previews
for n in names:
    dur,a,b=SHOTS[n]; N=int(round(dur*FPS)); os.makedirs(f'{S}/{OUT}/{n}',exist_ok=True)
    cam.data.shift_x=SHIFT.get(n,0.0)
    frames=[0,N//2,N-1] if only else range(N)
    for i in frames:
        out=f'{S}/{OUT}/{n}/{i:04d}.png'
        if os.path.exists(out) and not only: continue
        t=ease(i/(N-1))
        aim(cam,lerp(a[0],b[0],t),lerp(a[1],b[1],t),a[2]+(b[2]-a[2])*t)
        sc.render.filepath=out; t0=time.time(); bpy.ops.render.render(write_still=True)
        print('FRAME',n,i,N,round(time.time()-t0,1),flush=True)
