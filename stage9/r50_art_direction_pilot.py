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
    # Architectural identity installation: stepped volumes, recessed facade and light blade.
    cube("Basalt architectural podium",(-.15,0,.16),(6.0,3.8,.32),m["ink"],.16)
    cube("Main gallery volume",(-.55,.25,1.55),(2.45,1.8,2.75),m["ink"],.12)
    cube("Warm stone facade inset",(-.55,-.675,1.58),(1.92,.055,2.22),m["cream"],.035)
    cube("Deep recessed entrance",(-.55,-.72,.94),(.78,.07,1.18),m["ink"],.025)
    cube("Upper floating canopy",(-.55,-.02,2.94),(2.8,2.15,.16),m["silver"],.045)
    cube("Secondary glass pavilion",(1.38,.28,.98),(1.42,1.58,1.72),m["glass"],.12)
    cube("Pavilion roof",(1.38,.28,1.88),(1.58,1.72,.14),m["gold"],.035)
    # Layered fins create a designed facade rather than a primitive abstract arrangement.
    for i in range(9):
        cube("Facade vertical brass fin "+str(i),(-1.38+i*.205,-.735,1.73),(.035,.045,1.48),m["gold"],.012)
    for i in range(4):
        cube("Landscape step "+str(i),(-2.05+i*.32,-1.25,.36+i*.08),(.27,.46,.12),m["blue"] if i%2 else m["orange"],.025)
    curve("Sculptural wayfinding light",[(-2.7,-.2,2.0),(-2.35,-.2,2.8),(-1.9,-.2,3.0)],.035,m["orange"])
    uv("Spherical light marker",(1.65,-.65,2.12),(.16,.16,.16),m["cream"])

def build_product(m):
    # High-end desktop audio control unit with layered machining, screen, ports and tactile controls.
    cube("Floating graphite presentation base",(0,0,.16),(5.3,3.45,.32),m["ink"],.2)
    cube("Main aluminium enclosure",(0,.05,1.38),(2.72,1.55,2.12),m["silver"],.28)
    cube("Dark glass front control panel",(0,-.765,1.42),(2.42,.055,1.82),m["ink"],.19)
    cube("OLED status display",(-.58,-.805,2.02),(.82,.035,.36),m["glass"],.035)
    # Tiny status indicators and engraved interface marks.
    for i,col in enumerate((m["orange"],m["blue"],m["gold"])):
        uv("Status LED "+str(i),(-.86+i*.16,-.833,1.76),(.025,.018,.025),col)
    cyl("Precision driver housing",(.43,-.83,1.43),.62,.07,m["ink"])
    torus("Concentric machined driver ring",(.43,-.89,1.43),.54,.045,m["gold"],(math.pi/2,0,0))
    torus("Inner diaphragm suspension",(.43,-.91,1.43),.39,.018,m["silver"],(math.pi/2,0,0))
    uv("Textured driver diaphragm",(.43,-.91,1.43),(.34,.055,.34),m["glass"])
    uv("Brushed aluminium dust cap",(.43,-.97,1.43),(.12,.045,.12),m["silver"])
    for i in range(3):
        cyl("Knurled encoder dial",(-.62+i*.39,-.86,.86),.105,.095,m["gold"],64)
        torus("Encoder etched ring "+str(i),(-.62+i*.39,-.92,.86),.083,.009,m["silver"],(math.pi/2,0,0))
    for i in range(11):
        for j in range(2):
            uv("Precision speaker grille perforation",(1.05,-.81,.72+j*.11),(.018,.012,.018),m["ink"])
    # Rear connector bank and a removable dock establish product plausibility.
    for i in range(4):
        cyl("Rear I O connector "+str(i),(-.9+i*.58,.84,1.05),.075,.06,m["ink"],48)
    cube("Ceramic charging cradle",(0,.34,.39),(3.75,1.22,.14),m["cream"],.06)
    cube("Cradle contact strip",(0,-.24,.47),(1.2,.035,.025),m["gold"],.01)

def build_gallery(m):
    # Contemporary museum room with architectural wall, spotlights and distinct curated works.
    cube("Gallery floor plinth",(0,0,.10),(6.3,3.9,.20),m["ink"],.10)
    cube("Rear exhibition wall",(0,1.55,2.0),(6.0,.16,3.8),m["cream"],.045)
    cube("Left shadow reveal",(-2.86,1.43,2.0),(.08,.08,3.6),m["gold"],.015)
    # Three intentionally different works: folded metal, stone monolith and kinetic glass.
    cyl("Sculpture one low plinth",(-1.65,-.05,.25),.62,.18,m["silver"])
    cube("Folded metal artwork",(-1.65,-.02,1.12),(.78,.42,1.48),m["orange"],.18).rotation_euler[1]=.28
    torus("Folded artwork aperture",(-1.65,-.27,1.12),.28,.045,m["gold"],(math.pi/2,.2,0))
    cyl("Sculpture two low plinth",(0,-.05,.25),.62,.18,m["silver"])
    cube("Carved stone monolith",(0,.02,1.25),(.72,.54,1.75),m["cream"],.16)
    cube("Monolith inset shadow",(0,-.265,1.30),(.24,.025,1.08),m["ink"],.08)
    cyl("Sculpture three low plinth",(1.65,-.05,.25),.62,.18,m["silver"])
    torus("Kinetic glass sculpture",(1.65,.0,1.32),.58,.16,m["blue"],(.48,.22,.18))
    torus("Kinetic inner brass ring",(1.65,-.18,1.32),.30,.045,m["gold"],(.72,.3,.2))
    # Track lighting and discreet wall washes ground the scene as a real exhibition interior.
    cube("Ceiling lighting rail",(0,.9,3.58),(4.8,.12,.10),m["ink"],.035)
    for i,x in enumerate((-1.65,0,1.65)):
        cyl("Museum spotlight "+str(i),(x,.86,3.32),.11,.16,m["gold"],48)
        curve("Focused gallery light "+str(i),[(x,.8,3.25),(x,-.1,2.4),(x,-.25,1.8)],.012,m["cream"])


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
