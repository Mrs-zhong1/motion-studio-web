#!/usr/bin/env python3
"""R26 Blender procedural 3D pilot; run with blender -b --python this_file -- --out DIR.

All geometry/materials are created in-script. No image API, model weights,
stock images, downloaded textures, external HDRIs or paid assets.
"""
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
BOARD=ROOT/"r26-storyboard.json"
PILOT=[("editorial",2),("product-3d",3),("architecture",2),("agency",1)]
W,H=1600,900

def material(name,color,metallic=0.0,roughness=0.45):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*color,1)
 bs.inputs["Metallic"].default_value=metallic
 bs.inputs["Roughness"].default_value=roughness
 return m

def cube(name,loc,scale,mat,bevel=0.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=name;o.dimensions=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new("Soft manufactured edges","BEVEL");mod.width=bevel;mod.segments=4
  o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
 o.data.materials.append(mat);return o

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
 bpy.ops.object.shade_smooth();return o

def cylinder(name,loc,radius,depth,mat,vertices=96):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 mod=o.modifiers.new("Edge glints","BEVEL");mod.width=0.025;mod.segments=3
 o.modifiers.new("Weighted normals","WEIGHTED_NORMAL");return o

def torus(name,loc,major,minor,mat,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=96,minor_segments=16,location=loc,rotation=rotation)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat);bpy.ops.object.shade_smooth();return o

def point_camera(obj,target):
 obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def setup_scene(template,safe):
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 scene=bpy.context.scene
 scene.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else "BLENDER_EEVEE"
 if hasattr(scene,"eevee"): scene.eevee.taa_render_samples=48
 scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGB"
 scene.render.film_transparent=False
 scene.view_settings.view_transform="AgX" if "AgX" in bpy.context.scene.view_settings.bl_rna.properties["view_transform"].enum_items.keys() else "Standard"
 world=bpy.data.worlds.new("Studio world") if not bpy.data.worlds else bpy.data.worlds[0]
 scene.world=world;world.use_nodes=True
 world.node_tree.nodes["Background"].inputs[0].default_value=(0.025,0.035,0.05,1)
 world.node_tree.nodes["Background"].inputs[1].default_value=0.35
 bg=material("Midnight architectural backdrop",(0.035,0.05,0.065),roughness=0.8)
 floor= cube("Infinite studio floor",(0,0,-0.18),(200,200,0.25),bg,0)
 # camera view spans a quiet third on the side reserved for HTML typography
 camera_data=bpy.data.cameras.new("R26 camera");camera=bpy.data.objects.new("R26 camera",camera_data)
 scene.collection.objects.link(camera);scene.camera=camera
 camera.location=(0,-15,7.2);point_camera(camera,(0,0,1.05));camera_data.type="ORTHO";camera_data.ortho_scale=11.7
 # softbox lighting
 for name,loc,power,size,color in [
  ("Key softbox",(-4,-7,9),1650,7.0,(1.0,0.82,0.66)),
  ("Cool fill",(5,-3,6),1050,6.0,(0.55,0.72,1.0)),
  ("Rim light",(0,5,8),2100,5.0,(1.0,0.72,0.48))]:
  ld=bpy.data.lights.new(name,"AREA");lo=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo)
  lo.location=loc;ld.energy=power;ld.shape="DISK";ld.size=size;ld.color=color;point_camera(lo,(0,0,1))
 return scene

def build(row):
 t=row["template"];safe=row["textSafeZone"];x=-1.55 if safe=="right third" else 1.55
 dark=material("Graphite ceramic",(0.055,0.075,0.09),0.48,0.26)
 metal=material("Brushed titanium",(0.48,0.56,0.61),0.82,0.23)
 ivory=material("Warm limestone",(0.72,0.66,0.53),0.05,0.78)
 wood=material("Smoked oak",(0.28,0.16,0.085),0.0,0.55)
 accent=material("Saturated persimmon",(0.98,0.19,0.085),0.12,0.28)
 yellow=material("Sulfur yellow",(0.98,0.68,0.08),0.08,0.32)
 cyan=material("Powder blue",(0.08,0.58,0.72),0.16,0.3)
 glass=material("Smoked glass",(0.025,0.11,0.15),0.62,0.12)
 if t=="product-3d":
  cube("Floating graphite product plinth",(x,0,0.15),(4.2,2.5,0.34),dark,0.16)
  cube("Sculptural audio enclosure",(x,-0.1,1.55),(2.5,1.05,2.45),dark,0.34)
  cube("Precision titanium faceplate",(x,-0.66,1.55),(2.12,0.10,2.08),metal,0.28)
  cylinder("Speaker driver outer ring",(x,-0.75,1.55),0.72,0.12,dark)
  torus("Machined concentric rim",(x,-0.84,1.55),0.60,0.055,ivory,(1.5708,0,0))
  cylinder("Acoustic diaphragm",(x,-0.84,1.55),0.48,0.08,glass)
  sphere("Central acoustic dome",(x,-0.92,1.55),(0.22,0.11,0.22),metal)
  for i in range(9):
   for j in range(3):
    sphere("Micro perforation",(x-0.92+i*0.23,-0.79,0.72+j*0.16),(0.025,0.018,0.025),dark)
  torus("Suspended product halo",(x,0,2.9),1.8,0.025,metal,(0.2,0,0))
 elif t=="architecture":
  cube("Hillside terrain",(x,0,0.05),(7.5,5.2,0.45),wood,0.12)
  cube("Main limestone volume",(x,0,1.65),(4.2,3.0,3.1),ivory,0.04)
  cube("Recessed shadow volume",(x+1.3,-1.56,1.55),(1.55,0.10,2.65),dark,0.02)
  for dx in (-1.1,0.0):
   cube("Deep timber window reveal",(x+dx,-1.57,1.7),(0.92,0.12,1.95),wood,0.015)
   cube("Reflective glazing",(x+dx,-1.65,1.7),(0.72,0.035,1.68),glass,0.01)
  cube("Cantilevered timber canopy",(x,-0.1,3.28),(4.65,3.3,0.18),wood,0.04)
  for i in range(5):
   cube("Entry stepping stone",(x-2.4+i*0.55,-2.4-i*0.18,0.35),(0.42,0.62,0.12),ivory,0.04)
  for tx in (x-3.2,x+3.0):
   cylinder("Tree trunk",(tx,1.0,1.0),0.13,2.0,wood,24)
   sphere("Tree canopy",(tx,1.0,2.25),(0.8,0.8,1.05),dark)
 elif t=="editorial":
  cube("Oak process table",(x,0,0.55),(5.4,3.2,0.22),wood,0.08)
  for z,mat in ((0.70,ivory),(0.73,ivory)):
   cube("Matte paper folio",(x-0.6,-0.2,z),(2.5,1.75,0.08),mat,0.025)
  cube("Plaster material sample",(x+1.0,0.25,0.82),(0.95,0.9,0.24),ivory,0.04)
  cube("Dark stone sample",(x+1.0,-0.85,0.82),(0.95,0.9,0.24),dark,0.04)
  cylinder("Sculptural ceramic vessel",(x-1.9,0.2,1.15),0.43,0.9,ivory)
  sphere("Vessel shoulder",(x-1.9,0.2,1.65),(0.43,0.43,0.25),ivory)
  torus("Vessel lip",(x-1.9,0.2,1.8),0.16,0.045,metal)
  for i in range(4):
   cube("Material swatch",(x+1.7,-1.0+i*0.48,0.82),(0.46,0.34,0.10),(accent,yellow,cyan,metal)[i],0.02)
 elif t=="agency":
  cube("Color-block campaign stage",(x,0,0.12),(4.8,3.5,0.25),dark,0.12)
  torus("Oversized persimmon loop",(x-0.55,0,1.75),1.05,0.28,accent,(0.45,0.2,0.1))
  sphere("Inflated yellow volume",(x+0.9,0.1,1.25),(0.9,0.9,0.9),yellow)
  cube("Powder-blue geometric prop",(x-0.95,-0.8,0.8),(1.1,1.0,1.1),cyan,0.24)
  torus("Floating cyan ring",(x+1.0,0.4,2.55),0.58,0.11,cyan,(0.7,0.2,0.3))
  cylinder("Persimmon pedestal",(x,0,0.42),1.35,0.25,accent)
 else:
  raise ValueError("Pilot template has no Blender scene: "+t)

def main():
 argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=ROOT/"r26-blender-pilot")
 ap.add_argument("--limit",type=int,default=4);args=ap.parse_args(argv)
 board=json.loads(BOARD.read_text());rows=board["replacements"]
 chosen=[next(r for r in rows if (r["template"],r["chapter"])==k) for k in PILOT][:args.limit]
 args.out.mkdir(parents=True,exist_ok=True);manifest=[]
 for row in chosen:
  scene=setup_scene(row["template"],row["textSafeZone"]);build(row)
  path=args.out/(row["file"].replace(".jpg",".png"));scene.render.filepath=str(path)
  bpy.ops.render.render(write_still=True)
  raw=path.read_bytes()
  manifest.append({"template":row["template"],"chapter":row["chapter"],"file":path.name,
   "source":"PROCEDURAL_ORIGINAL","sourceType":"procedural-3d-render",
   "trueHighResolutionGenerated":True,"nativeSourceDimensions":[W,H],
   "generationSystem":"Blender Eevee procedural scene / stage9/r26_blender_pilot.py",
   "generationDate":datetime.now(timezone.utc).isoformat(),
   "sourceReference":"stage9/r26_blender_pilot.py#"+row["template"],
   "termsUrl":"https://github.com/Mrs-zhong1/motion-studio-web",
   "commercialUseTermsChecked":False,"sha256":hashlib.sha256(raw).hexdigest(),
   "reviewStatus":"HUMAN_VISUAL_REVIEW_REQUIRED","productionEligible":False})
 (args.out/"replacement.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({"mode":"ZERO_COST_BLENDER_3D_REVIEW_ONLY","generated":len(manifest),
  "dimensions":[W,H],"files":[r["file"] for r in manifest],"paidApiCalls":0,
  "thirdPartyAssets":0,"productionEligible":False},indent=2))
if __name__=="__main__":main()
