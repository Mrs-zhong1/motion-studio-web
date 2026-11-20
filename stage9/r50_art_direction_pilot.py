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

def text3d(name, body, loc, size, material, align="LEFT"):
    data=bpy.data.curves.new(name,"FONT"); data.body=body; data.size=size
    data.align_x=align; data.extrude=.004; data.bevel_depth=.001
    obj=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(obj)
    obj.location=loc; obj.rotation_euler=(math.pi/2,0,0); obj.data.materials.append(material)
    return obj

def build_agency(m):
    # Creative-agency portfolio environment: three distinct, full-scale campaign worlds.
    # Keep the portfolio wall readable and the foreground clear; avoid generic abstract rings.
    bpy.context.scene.camera.data.ortho_scale=14.0
    cube("Agency stage",(0,0,-.16),(12.0,7.4,.24),m["ink"],.035)
    cube("Portfolio backdrop",(0,3.0,2.20),(11.7,.18,4.35),m["ink"],.025)
    panels=[
      (-3.35,2.0,2.10,2.72,3.05,m["orange"],"01 / BRAND IDENTITY","FORM / FIELD"),
      (0.0,2.0,2.10,2.72,3.05,m["blue"],"02 / DIGITAL CULTURE","MOVE / BEYOND"),
      (3.35,2.0,2.10,2.72,3.05,m["cream"],"03 / CAMPAIGN","MAKE / IMPACT")
    ]
    for idx,(x,y,z,w,h,accent,kicker,title) in enumerate(panels):
        cube("Campaign frame %02d"%idx,(x,y,z),(w,.12,h),accent,.035)
        cube("Campaign canvas %02d"%idx,(x,y-.085,z),(w-.15,.035,h-.15),m["ink"] if idx!=2 else m["gold"],.012)
        text3d("Campaign kicker %02d"%idx,kicker,(x-w*.43,y-.13,z+h*.31),.115,m["cream"] if idx!=2 else m["ink"])
        text3d("Campaign title %02d"%idx,title,(x-w*.43,y-.14,z-h*.40),.165,m["cream"] if idx!=2 else m["ink"])
        if idx==0:
            # Identity packaging study: glass fragrance vessel, metal cap and label.
            cube("Identity bottle body",(x,y-.30,z+.05),(.78,.30,.94),m["cream"],.14)
            cyl("Bottle neck",(x,y-.31,z+.56),.20,.18,m["gold"],64)
            cube("Bottle cap",(x,y-.31,z+.72),(.43,.34,.22),m["ink"],.045)
            cube("Bottle label",(x,y-.47,z+.04),(.56,.025,.34),m["orange"],.025)
            for j in range(3):
                cube("Identity color bar %d"%j,(x-.83+j*.20,y-.26,z-.62),(.10,.035,.38+j*.08),m["gold"],.018)
        elif idx==1:
            # Digital-culture campaign: dimensional device screen with a vivid content tile.
            cube("Digital campaign device",(x,y-.28,z+.02),(1.25,.13,1.42),m["silver"],.12)
            cube("Digital screen glass",(x,y-.37,z+.05),(1.08,.035,1.22),m["ink"],.07)
            cube("Digital artwork field",(x,y-.40,z+.12),(.88,.025,.72),m["blue"],.035)
            torus("Digital signal loop",(x,y-.46,z+.12),.30,.045,m["orange"],(math.pi/2,.15,.1))
            uv("Digital signal core",(x,y-.47,z+.12),(.13,.035,.13),m["cream"])
            for j in range(4):
                cube("Digital UI line %d"%j,(x-.30+j*.20,y-.45,z-.42),(.12,.025,.035),m["cream"],.01)
        else:
            # Campaign art direction: layered print pieces and a sculpted display object.
            cube("Campaign poster board",(x,y-.27,z+.05),(1.35,.10,1.35),m["cream"],.035)
            cube("Campaign poster color block",(x-.25,y-.34,z+.18),(.48,.025,.76),m["orange"],.018)
            cube("Campaign poster typography bar",(x+.30,y-.35,z-.18),(.38,.025,.10),m["ink"],.012)
            cube("Campaign packaging box",(x+.60,y-.52,z-.24),(.48,.32,.32),m["blue"],.045)
            cube("Packaging label",(x+.60,y-.70,z-.24),(.34,.025,.14),m["cream"],.018)
    # Keep the foreground stage clear; campaign frames carry the visual hierarchy.
    
def build_product(m):
    # Premium mirrorless cinema camera with recognizable optical and tactile details.
    bpy.context.scene.camera.data.ortho_scale=11.8
    cube("Camera presentation slab",(0,0,.12),(5.9,3.8,.24),m["ink"],.18)
    cube("Magnesium camera body",(-.25,.08,1.42),(2.95,1.25,1.72),m["ink"],.22)
    cube("Top titanium shoulder",(-.25,.08,2.32),(2.55,1.12,.16),m["silver"],.07)
    # Multi-stage optical lens barrel with visible aperture and engraved focus rings.
    cyl("Lens outer hood",(-.15,-.92,1.47),.82,.78,m["ink"],128).rotation_euler[0]=math.pi/2
    cyl("Lens aluminium barrel",(-.15,-1.23,1.47),.72,.68,m["silver"],128).rotation_euler[0]=math.pi/2
    cyl("Lens inner barrel",(-.15,-1.49,1.47),.63,.24,m["ink"],128).rotation_euler[0]=math.pi/2
    torus("Lens front gold rim",(-.15,-1.63,1.47),.58,.045,m["gold"],(math.pi/2,0,0))
    cyl("Optical front glass",(-.15,-1.65,1.47),.52,.025,m["glass"],128).rotation_euler[0]=math.pi/2
    torus("Focus ring front",(-.15,-1.38,1.47),.69,.028,m["gold"],(math.pi/2,0,0))
    torus("Zoom ring rear",(-.15,-1.08,1.47),.77,.025,m["ink"],(math.pi/2,0,0))
    for i in range(16):
        a=2*math.pi*i/16
        cube("Lens grip notch %02d"%i,(-.15+.70*math.cos(a),-1.39,1.47+.70*math.sin(a)),(.035,.035,.055),m["ink"],.008)
    # Optical aperture: dark central iris and a subtle blue glass reflection read clearly as a camera lens.
    cyl("Recessed aperture iris",(-.15,-1.681,1.47),.29,.018,m["ink"],128).rotation_euler[0]=math.pi/2
    cyl("Lens optical center",(-.15,-1.696,1.47),.19,.012,m["glass"],128).rotation_euler[0]=math.pi/2
    uv("Optical blue reflection",(-.23,-1.711,1.57),(.085,.012,.035),m["blue"])
    torus("Inner aperture ring",(-.15,-1.705,1.47),.24,.012,m["silver"],(math.pi/2,0,0))
    cube("Ergonomic camera grip",(1.12,-.48,1.42),(.58,.42,1.42),m["cream"],.16)
    for i in range(9):
        cube("Grip tactile rib %02d"%i,(1.12,-.71,.88+i*.13),(.42,.035,.022),m["ink"],.008)
    cyl("Shutter release button",(.65,-.28,2.42),.12,.08,m["orange"],64)
    cyl("Exposure compensation dial",(-.85,-.25,2.45),.19,.10,m["gold"],64)
    torus("Exposure dial engraved ring",(-.85,-.25,2.51),.14,.012,m["silver"])
    cube("Electronic viewfinder housing",(-.28,.60,2.38),(.82,.48,.42),m["silver"],.09)
    cube("Viewfinder optical glass",(-.28,.86,2.39),(.48,.035,.23),m["glass"],.045)
    cube("Rear articulating display",(-.28,.70,1.40),(1.42,.12,.92),m["blue"],.08)
    cube("Hot shoe rail",(-.28,-.02,2.48),(.72,.28,.07),m["gold"],.025)
    for i in range(4):
        cyl("Top control dial %02d"%i,(-1.12+i*.32,-.10,2.48),.105,.10,m["silver"],64)
    for i in range(5):
        cube("Rear control key %02d"%i,(.55+i*.20,.70,.92),(.12,.035,.08),m["orange"] if i==0 else m["silver"],.018)
    for i in range(4):
        cube("I O port cover %02d"%i,(-1.15+i*.32,.69,.95),(.22,.035,.18),m["gold"],.025)
    cube("Camera mount base",(-.25,.25,.42),(1.65,.82,.18),m["silver"],.07)
    for x in (-.82,.32):
        cyl("Tripod mount foot "+str(x),(x,.25,.27),.13,.25,m["ink"],64)

def build_gallery(m):
    # Open-front museum gallery: remove the foreground right wall that hid the third artwork.
    bpy.context.scene.camera.data.ortho_scale=15.6
    cube("Gallery floor",(0,.25,.05),(9.6,6.8,.16),m["ink"],.025)
    cube("Rear plaster exhibition wall",(0,3.15,2.10),(9.1,.18,3.75),m["cream"],.025)
    cube("Left gallery return",(-4.55,2.0,2.10),(.18,2.25,3.75),m["cream"],.025)
    cube("Ceiling reveal",(0,2.95,3.98),(8.8,.10,.08),m["gold"],.015)
    cyl("Work one stone pedestal",(-2.55,-.25,.32),.72,.42,m["silver"])
    uv("Folded ceramic volume A",(-2.55,-.25,1.28),(.46,.40,.96),m["orange"])
    uv("Folded ceramic volume B",(-2.20,-.20,1.48),(.30,.34,.76),m["cream"])
    curve("Folded ribbon contour",[(-2.9,-.52,.85),(-3.05,-.52,1.55),(-2.5,-.52,2.05),(-2.05,-.52,1.52),(-2.22,-.52,.92)],.075,m["gold"])
    cyl("Work two stone pedestal",(0,-.20,.32),.72,.42,m["silver"])
    uv("Carved stone lower mass",(0,-.18,1.02),(.58,.48,.58),m["cream"])
    uv("Carved stone upper mass",(.18,-.17,1.78),(.36,.34,.62),m["silver"])
    uv("Carved stone crown",(-.08,-.15,2.27),(.22,.24,.28),m["orange"])
    cyl("Work three stone pedestal",(2.55,-.25,.32),.72,.42,m["silver"])
    torus("Suspended blue orbital form",(2.55,-.20,1.58),.62,.17,m["blue"],(.45,.2,.15))
    torus("Suspended brass inner orbit",(2.55,-.42,1.58),.34,.055,m["gold"],(.8,.35,.2))
    curve("Sculpture organic spine",[(2.15,-.20,.95),(2.10,-.18,1.55),(2.60,-.15,2.18),(3.05,-.15,1.72)],.07,m["cream"])
    # Track lighting is mounted behind the works; beams stay above the display silhouettes.
    cube("Museum lighting track",(0,2.55,3.72),(7.2,.10,.10),m["ink"],.025)
    for i,x in enumerate((-2.55,0,2.55)):
        cyl("Museum spotlight "+str(i),(x,2.48,3.48),.14,.20,m["gold"],64)
        curve("Spotlight beam "+str(i),[(x,2.42,3.38),(x,1.0,2.75),(x,.1,2.25)],.012,m["cream"])
    for i in range(7):
        cube("Wall wash vertical reveal "+str(i),(-3.0+i*.95,3.03,2.10),(.018,.025,2.9),m["gold"],.004)

def write_saas_svg(path):
    """Original SaaS workspace dashboard composition with explicitly illustrative demo data."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
<defs>
 <linearGradient id="canvas" x2="1" y2="1"><stop stop-color="#f6f7f5"/><stop offset="1" stop-color="#e9eeeb"/></linearGradient>
 <linearGradient id="brand" x2="1" y2="1"><stop stop-color="#183b35"/><stop offset="1" stop-color="#315e51"/></linearGradient>
 <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#183b35" flood-opacity=".09"/></filter>
</defs>
<rect width="1600" height="900" fill="url(#canvas)"/>
<rect x="0" y="0" width="226" height="900" fill="#172e2a"/>
<text x="34" y="58" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f5f7f3">NORTHSTAR</text>
<text x="34" y="82" font-family="Arial,sans-serif" font-size="10" letter-spacing="2" fill="#8eaaa0">WORKSPACE</text>
<rect x="22" y="126" width="182" height="42" rx="10" fill="#31574d"/>
<text x="48" y="153" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#fff">Overview</text>
<g font-family="Arial,sans-serif" font-size="14" fill="#b8c9c1">
 <text x="48" y="210">Projects</text><text x="48" y="258">Insights</text><text x="48" y="306">Campaigns</text><text x="48" y="354">Reports</text>
 <text x="34" y="430" font-size="10" letter-spacing="2" fill="#78948a">WORKSPACE</text>
 <text x="48" y="474">Team members</text><text x="48" y="522">Integrations</text><text x="48" y="570">Settings</text>
</g>
<circle cx="42" cy="204" r="4" fill="#a6d7c1"/><circle cx="42" cy="252" r="4" fill="#78948a"/><circle cx="42" cy="300" r="4" fill="#78948a"/><circle cx="42" cy="348" r="4" fill="#78948a"/>
<circle cx="42" cy="468" r="4" fill="#78948a"/><circle cx="42" cy="516" r="4" fill="#78948a"/><circle cx="42" cy="564" r="4" fill="#78948a"/>
<circle cx="48" cy="836" r="17" fill="#d4a76c"/><text x="48" y="841" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#172e2a">A</text>
<text x="76" y="833" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#f5f7f3">Alex Morgan</text><text x="76" y="851" font-family="Arial,sans-serif" font-size="10" fill="#8eaaa0">Workspace admin</text>
<rect x="226" y="0" width="1374" height="76" fill="#fff"/>
<text x="270" y="47" font-family="Arial,sans-serif" font-size="14" fill="#73847d">Workspace /</text><text x="365" y="47" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#1c3731">Overview</text>
<rect x="1290" y="20" width="180" height="36" rx="9" fill="#f3f6f3" stroke="#dce5df"/><text x="1310" y="43" font-family="Arial,sans-serif" font-size="12" fill="#71837b">Last 30 days</text>
<circle cx="1515" cy="38" r="17" fill="#e4eee8"/><text x="1515" y="43" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#315e51">?</text>
<text x="270" y="132" font-family="Arial,sans-serif" font-size="30" font-weight="700" fill="#1b3731">Good morning, Alex</text>
<text x="270" y="164" font-family="Arial,sans-serif" font-size="14" fill="#71837b">A clear view of your team's work and performance.</text>
<rect x="1360" y="108" width="184" height="42" rx="10" fill="url(#brand)"/><text x="1452" y="135" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#fff">+ New project</text>
<g filter="url(#shadow)">
 <rect x="270" y="198" width="292" height="132" rx="14" fill="#fff"/><rect x="582" y="198" width="292" height="132" rx="14" fill="#fff"/><rect x="894" y="198" width="292" height="132" rx="14" fill="#fff"/><rect x="1206" y="198" width="338" height="132" rx="14" fill="#fff"/>
</g>
<g font-family="Arial,sans-serif">
 <text x="294" y="232" font-size="12" fill="#75867e">Active projects</text><text x="294" y="282" font-size="34" font-weight="700" fill="#1b3731">24</text><text x="352" y="281" font-size="11" fill="#36856a">+12.5%</text>
 <text x="606" y="232" font-size="12" fill="#75867e">Tasks completed</text><text x="606" y="282" font-size="34" font-weight="700" fill="#1b3731">86%</text><text x="710" y="281" font-size="11" fill="#36856a">+4.8%</text>
 <text x="918" y="232" font-size="12" fill="#75867e">Team capacity</text><text x="918" y="282" font-size="34" font-weight="700" fill="#1b3731">78%</text><text x="1022" y="281" font-size="11" fill="#b27b3f">-2.1%</text>
 <text x="1230" y="232" font-size="12" fill="#75867e">On-time delivery</text><text x="1230" y="282" font-size="34" font-weight="700" fill="#1b3731">92%</text><text x="1334" y="281" font-size="11" fill="#36856a">+6.3%</text>
 <text x="294" y="309" font-size="10" fill="#9aa8a1">ILLUSTRATIVE DEMO METRIC</text><text x="606" y="309" font-size="10" fill="#9aa8a1">ILLUSTRATIVE DEMO METRIC</text><text x="918" y="309" font-size="10" fill="#9aa8a1">ILLUSTRATIVE DEMO METRIC</text><text x="1230" y="309" font-size="10" fill="#9aa8a1">ILLUSTRATIVE DEMO METRIC</text>
</g>
<g filter="url(#shadow)"><rect x="270" y="354" width="824" height="310" rx="14" fill="#fff"/><rect x="1114" y="354" width="430" height="310" rx="14" fill="#fff"/><rect x="270" y="688" width="824" height="166" rx="14" fill="#fff"/><rect x="1114" y="688" width="430" height="166" rx="14" fill="#fff"/></g>
<text x="296" y="392" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#1b3731">Project activity</text><text x="296" y="416" font-family="Arial,sans-serif" font-size="11" fill="#8a9992">Work completed over time · illustrative data</text>
<g stroke="#e9eeeb" stroke-width="1"><path d="M318 462 H1058 M318 510 H1058 M318 558 H1058 M318 606 H1058"/></g>
<g font-family="Arial,sans-serif" font-size="10" fill="#93a199"><text x="292" y="466">100</text><text x="298" y="514">75</text><text x="298" y="562">50</text><text x="298" y="610">25</text></g>
<path d="M330 580 C390 560 420 574 470 530 S560 548 610 500 S700 518 750 470 S840 494 890 444 S980 458 1040 426" fill="none" stroke="#3b806a" stroke-width="4" stroke-linecap="round"/>
<path d="M330 580 C390 560 420 574 470 530 S560 548 610 500 S700 518 750 470 S840 494 890 444 S980 458 1040 426 L1040 620 L330 620Z" fill="#d9ebe2" opacity=".65"/>
<g fill="#3b806a"><circle cx="470" cy="530" r="5"/><circle cx="610" cy="500" r="5"/><circle cx="750" cy="470" r="5"/><circle cx="890" cy="444" r="5"/><circle cx="1040" cy="426" r="5"/></g>
<g font-family="Arial,sans-serif" font-size="10" fill="#93a199"><text x="330" y="640">01 Nov</text><text x="500" y="640">08 Nov</text><text x="670" y="640">15 Nov</text><text x="840" y="640">22 Nov</text><text x="1000" y="640">30 Nov</text></g>
<text x="1140" y="392" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#1b3731">Team workload</text><text x="1140" y="416" font-family="Arial,sans-serif" font-size="11" fill="#8a9992">Capacity by team · illustrative data</text>
<g font-family="Arial,sans-serif" font-size="12" fill="#596d64">
 <text x="1140" y="464">Design</text><text x="1495" y="464" text-anchor="end" font-weight="700" fill="#1b3731">82%</text>
 <text x="1140" y="520">Strategy</text><text x="1495" y="520" text-anchor="end" font-weight="700" fill="#1b3731">68%</text>
 <text x="1140" y="576">Production</text><text x="1495" y="576" text-anchor="end" font-weight="700" fill="#1b3731">91%</text>
</g>
<g><rect x="1140" y="476" width="355" height="8" rx="4" fill="#edf1ee"/><rect x="1140" y="476" width="291" height="8" rx="4" fill="#3b806a"/><rect x="1140" y="532" width="355" height="8" rx="4" fill="#edf1ee"/><rect x="1140" y="532" width="241" height="8" rx="4" fill="#7aa995"/><rect x="1140" y="588" width="355" height="8" rx="4" fill="#edf1ee"/><rect x="1140" y="588" width="323" height="8" rx="4" fill="#c28b50"/></g>
<text x="296" y="728" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#1b3731">Recent projects</text>
<g font-family="Arial,sans-serif" font-size="11" fill="#8a9992"><text x="296" y="765">PROJECT</text><text x="680" y="765">OWNER</text><text x="830" y="765">STATUS</text><text x="1010" y="765">DUE</text></g>
<g font-family="Arial,sans-serif" font-size="12" fill="#40574e">
 <text x="296" y="794">Brand refresh / Northstar</text><text x="680" y="794">M. Chen</text><text x="830" y="794" fill="#36856a">In progress</text><text x="1010" y="794">Nov 24</text>
 <text x="296" y="828">Product launch / Atlas</text><text x="680" y="828">J. Rivera</text><text x="830" y="828" fill="#b27b3f">In review</text><text x="1010" y="828">Nov 27</text>
</g>
<text x="1140" y="728" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#1b3731">Priority insight</text>
<rect x="1140" y="750" width="378" height="78" rx="10" fill="#eef5f0"/>
<text x="1160" y="778" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#315e51">Production capacity is nearing its limit.</text>
<text x="1160" y="801" font-family="Arial,sans-serif" font-size="11" fill="#6d8177">Review workload allocation before the next launch.</text>
<text x="270" y="882" font-family="Arial,sans-serif" font-size="10" letter-spacing="1" fill="#9aa8a1">CONCEPT UI · ALL METRICS AND PROJECTS ARE ILLUSTRATIVE DEMO CONTENT</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")

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
