#!/usr/bin/env python3
"""R50 scene-specific art-direction pilot. Run inside Blender 4.x.

Creates three original procedural 3D review scenes plus a standalone original
SaaS SVG composition. No external images, textures, fonts, HDRIs or paid APIs.
All outputs remain review-only until independent visual and rights review.
"""
import argparse, hashlib, json, math, sys
from datetime import datetime, timezone
from pathlib import Path
import bpy
from mathutils import Vector

W,H=1600,900
ROOT=Path(__file__).resolve().parent

def mat(name, color, metallic=0.0, rough=0.45, transmission=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=rough
    if "Transmission" in p.inputs: p.inputs["Transmission"].default_value=transmission
    return m

def cube(name, loc, dims, material, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b=o.modifiers.new("Machined radius","BEVEL"); b.width=bevel; b.segments=5
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    o.data.materials.append(material); return o

def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth(); return o

def cyl(name, loc, radius, depth, material, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    b=o.modifiers.new("Edge radius","BEVEL"); b.width=.025; b.segments=4
    o.modifiers.new("Weighted normals","WEIGHTED_NORMAL"); return o

def torus(name, loc, major, minor, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=128, minor_segments=24, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); bpy.ops.object.shade_smooth(); return o

def curve(name, points, bevel, material):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.bevel_depth=bevel; c.bevel_resolution=5
    s=c.splines.new("BEZIER"); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=co; p.handle_left_type="AUTO"; p.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o); o.data.materials.append(material); return o

def camera_and_light():
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else "BLENDER_EEVEE"
    scene.render.resolution_x=W; scene.render.resolution_y=H; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.image_settings.color_mode="RGB"
    scene.view_settings.view_transform="AgX" if "AgX" in bpy.context.scene.view_settings.bl_rna.properties["view_transform"].enum_items.keys() else "Standard"
    world=bpy.data.worlds.new("R50 deep studio") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world=world; world.use_nodes=True; world.node_tree.nodes["Background"].inputs[0].default_value=(.012,.019,.03,1); world.node_tree.nodes["Background"].inputs[1].default_value=.28
    d=bpy.data.cameras.new("R50 portrait product camera"); cam=bpy.data.objects.new("R50 portrait product camera",d); scene.collection.objects.link(cam); scene.camera=cam
    cam.location=(7,-13,7); target=Vector((0,0,1.3)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler(); d.type="ORTHO"; d.ortho_scale=11.4
    for name,loc,power,size,color in [
        ("Warm key",(-4,-6,8),1900,6,(1,.78,.58)),
        ("Cool fill",(5,-2,5),1250,5,(.48,.68,1)),
        ("Rim",(0,5,7),2300,4,(1,.48,.24))]:
        ld=bpy.data.lights.new(name,"AREA"); lo=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo)
        lo.location=loc; ld.energy=power; ld.shape="DISK"; ld.size=size; ld.color=color
        lo.rotation_euler=(Vector((0,0,1))-Vector(loc)).to_track_quat("-Z","Y").to_euler()

def reset(template):
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    camera_and_light()
    floor=mat("Matte midnight cyclorama",(.018,.027,.04),0,.82)
    cube("Seamless studio ground",(0,0,-.2),(200,200,.3),floor,0)
    return {
      "ink":mat("Obsidian anodized alloy",(.025,.038,.052),.72,.23),
      "silver":mat("Satin titanium",(.48,.57,.64),.88,.2),
      "cream":mat("Warm porcelain",(.82,.77,.66),.08,.28),
      "orange":mat("Vermilion lacquer",(.96,.19,.075),.18,.24),
      "blue":mat("Ultramarine enamel",(.035,.18,.72),.24,.22),
      "glass":mat("Optical smoked glass",(.035,.12,.17),.45,.12,.35),
      "gold":mat("Champagne brass",(.65,.39,.13),.82,.24)
    }

def build_agency(m):
    # A deliberate architectural composition: nested portals, a folded ribbon and a plinth.
    cube("Basalt monolith plinth",(-.2,0,.18),(5.8,3.7,.36),m["ink"],.18)
    for i, material in enumerate((m["orange"],m["blue"],m["gold"])):
        torus("Layered sculptural portal "+str(i),(-.65+i*.55,.1,2.15+i*.12),1.35-i*.16,.095,material,(math.pi/2,0,.12*i))
    curve("Continuous folded metal gesture",[(-2.1,-.5,1.2),(-1.4,-.2,3.4),(.1,.15,3.8),(1.35,.3,2.5),(2.1,.2,1.4)],.11,m["silver"])
    uv("Gloss enamel sphere",(1.45,-.55,1.15),(.72,.72,.72),m["orange"])
    for i in range(5):
        cube("Floating editorial color tile "+str(i),(-2.1+i*.62,-1.45,.48+i*.12),(.42,.12,.42), (m["blue"],m["gold"],m["cream"],m["orange"],m["silver"])[i],.035)

def build_product(m):
    # A premium desktop audio instrument with visible controls, machined rings and a dock.
    cube("Floating dark titanium product deck",(0,0,.18),(5.1,3.3,.34),m["ink"],.22)
    cube("Sculpted speaker chassis",(0,0,1.48),(2.65,1.45,2.35),m["ink"],.38)
    cube("Brushed front fascia",(0,-.755,1.48),(2.3,.08,2.05),m["silver"],.28)
    cyl("Driver surround",(0,-.83,1.58),.77,.09,m["ink"])
    torus("Precision brass driver rim",(0,-.9,1.58),.68,.045,m["gold"],(math.pi/2,0,0))
    uv("Carbon fiber diaphragm",(0,-.91,1.58),(.57,.07,.57),m["glass"])
    uv("Aluminium dust cap",(0,-.99,1.58),(.19,.08,.19),m["silver"])
    for i in range(3):
        cyl("Machined rotary control",(.95+i*.28,-.86,.78),.085,.11,m["gold"],48)
    for i in range(13):
        for j in range(3):
            uv("Precision ventilation perforation",(-.96+i*.16,-.84,.72+j*.13),(.018,.012,.018),m["ink"])
    torus("Dock halo",(0,.12,2.75),1.8,.018,m["silver"],(.15,.08,0))
    cube("Ceramic charging dock",(0,.35,.42),(3.5,1.2,.16),m["cream"],.08)

def build_gallery(m):
    # Sculptural exhibition: layered plinths, a suspended kinetic ring and stone monolith.
    cube("Gallery black stage",(0,0,.12),(6.2,3.8,.24),m["ink"],.12)
    for i,(x,z,ma) in enumerate([(-1.55,1.0,m["cream"]),(0,1.35,m["orange"]),(1.55,.9,m["blue"])]):
        cyl("Museum pedestal "+str(i),(x,.1,z/2),.68,.12,m["silver"])
        if i==0:
            uv("Porcelain biomorphic sculpture",(x,0,z+.48),(.48,.4,.72),ma)
        elif i==1:
            torus("Suspended kinetic sculpture",(x,0,z+.35),.62,.13,ma,(.55,.2,.2))
            torus("Inner orbit",(x,0,z+.35),.36,.055,m["gold"],(.9,.3,.1))
        else:
            cube("Monolithic cobalt sculpture",(x,0,z+.28),(.72,.52,1.1),ma,.24)
            torus("Cutout frame",(x,-.3,z+.28),.34,.055,m["gold"],(math.pi/2,0,0))
    curve("Ceiling installation cable",[(-2.6,1.2,3.5),(-1.2,1.2,3.1),(0,1.2,3.7),(1.3,1.2,3.15),(2.6,1.2,3.5)],.018,m["gold"])


def write_saas_svg(path):
    # Original vector UI scene: task flow, data cards and live signal; no external fonts/images.
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101a2b"/><stop offset="1" stop-color="#243b58"/></linearGradient><linearGradient id="glow"><stop stop-color="#5eead4"/><stop offset="1" stop-color="#60a5fa"/></linearGradient><filter id="blur"><feGaussianBlur stdDeviation="35"/></filter></defs>
<rect width="1600" height="900" fill="url(#bg)"/><circle cx="1220" cy="260" r="210" fill="#2563eb" opacity=".22" filter="url(#blur)"/>
<g font-family="Arial,sans-serif"><text x="110" y="115" fill="#9fb4d1" font-size="22" letter-spacing="5">MOTION / WORKFLOW SYSTEM</text><text x="110" y="205" fill="#f8fafc" font-size="62" font-weight="700">From signal to outcome.</text>
<text x="110" y="255" fill="#a8bad1" font-size="24">A clear, connected product journey — not a static dashboard.</text>
<g transform="translate(110 360)"><rect width="390" height="310" rx="28" fill="#17283d" stroke="#45617e"/><circle cx="52" cy="58" r="20" fill="#5eead4"/><text x="92" y="67" fill="#e2e8f0" font-size="28">01 / Capture</text><path d="M42 130 H330 M42 170 H270 M42 210 H300" stroke="#6f89a8" stroke-width="12" stroke-linecap="round"/><rect x="42" y="245" width="128" height="34" rx="17" fill="#164e63"/><text x="60" y="268" fill="#99f6e4" font-size="16">LIVE SIGNAL</text></g>
<path d="M520 515 C560 515 560 515 600 515" stroke="url(#glow)" stroke-width="5" fill="none"/><path d="M585 500 L605 515 L585 530" stroke="#5eead4" stroke-width="5" fill="none"/>
<g transform="translate(620 360)"><rect width="390" height="310" rx="28" fill="#17283d" stroke="#45617e"/><circle cx="52" cy="58" r="20" fill="#60a5fa"/><text x="92" y="67" fill="#e2e8f0" font-size="28">02 / Shape</text><rect x="42" y="125" width="306" height="130" rx="18" fill="#203b59"/><path d="M72 220 L132 180 L190 200 L260 145 L320 165" stroke="#5eead4" stroke-width="6" fill="none"/><circle cx="260" cy="145" r="9" fill="#5eead4"/></g>
<path d="M1030 515 C1070 515 1070 515 1110 515" stroke="url(#glow)" stroke-width="5" fill="none"/><path d="M1095 500 L1115 515 L1095 530" stroke="#5eead4" stroke-width="5" fill="none"/>
<g transform="translate(1130 360)"><rect width="360" height="310" rx="28" fill="#17283d" stroke="#45617e"/><circle cx="52" cy="58" r="20" fill="#a78bfa"/><text x="92" y="67" fill="#e2e8f0" font-size="28">03 / Deliver</text><circle cx="180" cy="185" r="72" fill="none" stroke="#334e6b" stroke-width="18"/><path d="M180 113 A72 72 0 1 1 117 220" stroke="#5eead4" stroke-width="18" fill="none" stroke-linecap="round"/><text x="180" y="195" fill="#f8fafc" font-size="34" text-anchor="middle" font-weight="700">92%</text></g>
<text x="110" y="790" fill="#8ea6c3" font-size="18" letter-spacing="3">CAPTURE  →  SHAPE  →  DELIVER</text></g></svg>'''
    path.write_text(svg,encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,default=Path("r50-review"))
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    args=ap.parse_args(argv)
    args.out.mkdir(parents=True,exist_ok=True); manifest=[]
    for template,builder in (("agency",build_agency),("product-3d",build_product),("gallery",build_gallery)):
        # reset() returns a scene-specific material palette and clears the prior scene.
        materials=reset(template)
        builder(materials)
        scene=bpy.context.scene; out=args.out/(template+"-r50.png"); scene.render.filepath=str(out)
        bpy.ops.render.render(write_still=True); raw=out.read_bytes()
        manifest.append({"template":template,"file":out.name,"sourceType":"procedural-3d-render","dimensions":[W,H],"sha256":hashlib.sha256(raw).hexdigest(),"sourceCodeSha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"blenderVersion":bpy.app.version_string,"renderEngine":scene.render.engine,"thirdPartyAssets":False,"commercialUseTermsChecked":False,"reviewStatus":"HUMAN_VISUAL_REVIEW_REQUIRED","productionEligible":False})
    svg=args.out/"saas-r50.svg"; write_saas_svg(svg); raw=svg.read_bytes()
    manifest.append({"template":"saas","file":svg.name,"sourceType":"original-svg-vector","dimensions":[W,H],"sha256":hashlib.sha256(raw).hexdigest(),"sourceCodeSha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"thirdPartyAssets":False,"commercialUseTermsChecked":False,"reviewStatus":"HUMAN_VISUAL_REVIEW_REQUIRED","productionEligible":False})
    (args.out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"generated":len(manifest),"files":[x["file"] for x in manifest],"productionEligible":False,"reviewRequired":True},indent=2))

if __name__=="__main__": main()
