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
    # Layered facade, glazing mullions and a deep portal make the installation read as architecture.
    cube("Shadow reveal over entrance",(-.55,-.79,1.68),(1.04,.10,1.72),m["ink"],.025)
    cube("Recessed bronze portal surround",(-.55,-.855,1.55),(1.02,.045,1.88),m["gold"],.025)
    cube("Portal dark glazing",(-.55,-.89,1.55),(.78,.035,1.62),m["glass"],.015)
    for i in range(9):
        cube("Facade vertical brass fin "+str(i),(-1.38+i*.205,-.735,1.73),(.035,.045,1.48),m["gold"],.012)
    for i in range(4):
        cube("Pavilion glazing mullion "+str(i),(0.88+i*.32,-.54,1.0),(.025,.035,1.52),m["silver"],.008)
    cube("Cantilevered signage blade",(-1.95,-.15,2.55),(.72,.08,.12),m["orange"],.025)
    for i in range(3):
        cube("Landscape stone terrace "+str(i),(-2.05+i*.30,-1.48,.30+i*.055),(.25,.38,.10),m["cream"],.025)
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
    cyl("Precision driver housing",(.48,-.83,1.43),.48,.07,m["ink"])
    torus("Concentric machined driver ring",(.48,-.89,1.43),.41,.035,m["gold"],(math.pi/2,0,0))
    torus("Inner diaphragm suspension",(.48,-.91,1.43),.30,.016,m["silver"],(math.pi/2,0,0))
    uv("Textured driver diaphragm",(.48,-.91,1.43),(.26,.045,.26),m["glass"])
    uv("Brushed aluminium dust cap",(.48,-.96,1.43),(.09,.035,.09),m["silver"])
    cyl("Secondary monitor driver housing",(1.04,-.83,1.43),.23,.055,m["ink"],72)
    torus("Secondary driver titanium rim",(1.04,-.88,1.43),.18,.018,m["silver"],(math.pi/2,0,0))
    uv("Secondary driver diaphragm",(1.04,-.90,1.43),(.14,.035,.14),m["glass"])
    for i in range(3):
        cyl("Knurled encoder dial",(-.62+i*.39,-.86,.86),.105,.095,m["gold"],64)
        torus("Encoder etched ring "+str(i),(-.62+i*.39,-.92,.86),.083,.009,m["silver"],(math.pi/2,0,0))
    # A row of recessed faders and illuminated touch keys gives the front panel a real workflow.
    for i in range(4):
        cube("Fader track "+str(i),(-.78+i*.42,-.81,1.05),(.035,.025,.24),m["silver"],.012)
        cube("Fader cap "+str(i),(-.78+i*.42,-.85,1.00+(i%2)*.10),(.11,.07,.065),m["cream"],.018)
    for i in range(5):
        uv("Illuminated function key "+str(i),(-.82+i*.22,-.835,.62),(.035,.018,.035),m["blue"] if i%2 else m["orange"])
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
    cube("Rear exhibition wall",(0,1.55,1.58),(6.0,.16,2.85),m["cream"],.045)
    cube("Left shadow reveal",(-2.86,1.43,1.58),(.08,.08,2.68),m["gold"],.015)
    cube("Right wall return",(2.96,.72,1.58),(.12,1.72,2.85),m["cream"],.035)
    cube("Gallery ceiling shadow line",(0,1.40,2.98),(5.75,.06,.055),m["gold"],.012)
    # Three intentionally different works: folded metal, stone monolith and kinetic glass.
    cyl("Sculpture one low plinth",(-1.65,-.05,.25),.62,.18,m["silver"])
    folded=cube("Folded metal artwork",(-1.65,-.02,1.12),(.78,.42,1.48),m["orange"],.18)
    folded.rotation_euler[1]=.28
    cube("Folded artwork contrasting plane",(-1.92,-.10,1.20),(.12,.34,1.22),m["gold"],.035).rotation_euler[1]=-.22
    torus("Folded artwork aperture",(-1.65,-.27,1.12),.28,.045,m["gold"],(math.pi/2,.2,0))
    cyl("Sculpture two low plinth",(0,-.05,.25),.62,.18,m["silver"])
    cube("Carved stone monolith",(0,.02,1.25),(.72,.54,1.75),m["cream"],.16)
    cube("Monolith inset shadow",(0,-.265,1.30),(.24,.025,1.08),m["ink"],.08)
    cyl("Sculpture three low plinth",(1.65,-.05,.25),.62,.18,m["silver"])
    torus("Kinetic glass sculpture",(1.65,.0,1.32),.58,.16,m["blue"],(.48,.22,.18))
    torus("Kinetic inner brass ring",(1.65,-.18,1.32),.30,.045,m["gold"],(.72,.3,.2))
    # Track lighting and discreet wall washes ground the scene as a real exhibition interior.
    cube("Ceiling lighting rail",(0,.9,2.78),(4.8,.12,.10),m["ink"],.035)
    for i,x in enumerate((-1.65,0,1.65)):
        cyl("Museum spotlight "+str(i),(x,.86,2.58),.11,.16,m["gold"],48)
        curve("Focused gallery light "+str(i),[(x,.8,2.50),(x,-.1,2.12),(x,-.25,1.78)],.012,m["cream"])


def write_saas_svg(path):
    # Original SaaS product interface: navigable workspace, KPI cards, analytics and activity.
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
<defs>
 <linearGradient id="canvas" x2="1" y2="1"><stop stop-color="#0b1220"/><stop offset="1" stop-color="#17263a"/></linearGradient>
 <linearGradient id="accent"><stop stop-color="#5eead4"/><stop offset="1" stop-color="#60a5fa"/></linearGradient>
 <filter id="soft"><feGaussianBlur stdDeviation="42"/></filter>
</defs>
<rect width="1600" height="900" fill="url(#canvas)"/>
<circle cx="1330" cy="120" r="260" fill="#2563eb" opacity=".10" filter="url(#soft)"/>
<!-- app chrome -->
<rect x="54" y="42" width="1492" height="816" rx="24" fill="#0e1929" stroke="#34465e" stroke-width="2"/>
<rect x="54" y="42" width="1492" height="70" rx="24" fill="#142238"/>
<circle cx="92" cy="77" r="7" fill="#fb7185"/><circle cx="116" cy="77" r="7" fill="#fbbf24"/><circle cx="140" cy="77" r="7" fill="#5eead4"/>
<rect x="178" y="61" width="34" height="32" rx="9" fill="url(#accent)"/>
<path d="M187 83 L195 69 L203 83" fill="none" stroke="#0e1929" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<text x="226" y="84" fill="#f1f5f9" font-family="Arial,sans-serif" font-size="22" font-weight="700">Northstar</text>
<rect x="1110" y="58" width="220" height="38" rx="19" fill="#1c2e45" stroke="#3b506c"/>
<circle cx="1132" cy="77" r="6" fill="#5eead4"/><text x="1150" y="83" fill="#b8c7d9" font-family="Arial,sans-serif" font-size="14">All systems operational</text>
<circle cx="1390" cy="77" r="18" fill="#263b55"/><text x="1384" y="83" fill="#dbeafe" font-family="Arial,sans-serif" font-size="15">A</text>
<text x="1422" y="83" fill="#dbeafe" font-family="Arial,sans-serif" font-size="15">Alex Morgan</text>
<!-- sidebar -->
<rect x="54" y="112" width="238" height="746" fill="#101d30"/>
<text x="84" y="158" fill="#7188a6" font-family="Arial,sans-serif" font-size="12" letter-spacing="2">WORKSPACE</text>
<rect x="72" y="178" width="202" height="48" rx="10" fill="#203b53"/>
<rect x="88" y="194" width="15" height="15" rx="4" fill="#5eead4"/>
<text x="118" y="208" fill="#e7f4f7" font-family="Arial,sans-serif" font-size="16" font-weight="700">Overview</text>
<g fill="#9aabc0" font-family="Arial,sans-serif" font-size="15">
 <text x="118" y="267">Analytics</text><text x="118" y="319">Campaigns</text><text x="118" y="371">Audience</text><text x="118" y="423">Automations</text>
</g>
<g fill="none" stroke="#6f89a8" stroke-width="2"><path d="M89 250 h18 v16 h-18z M89 302 h18 v16 h-18z M89 354 h18 v16 h-18z M89 406 h18 v16 h-18z"/></g>
<path d="M78 470 H268" stroke="#293d56"/>
<text x="84" y="508" fill="#7188a6" font-family="Arial,sans-serif" font-size="12" letter-spacing="2">MANAGE</text>
<g fill="#9aabc0" font-family="Arial,sans-serif" font-size="15"><text x="118" y="557">Integrations</text><text x="118" y="609">Settings</text></g>
<circle cx="98" cy="550" r="8" fill="none" stroke="#6f89a8" stroke-width="2"/><path d="M90 609 h16 M98 601 v16" stroke="#6f89a8" stroke-width="2"/>
<rect x="76" y="772" width="194" height="58" rx="12" fill="#172a40"/>
<circle cx="101" cy="801" r="14" fill="#36516d"/><text x="96" y="806" fill="#e2e8f0" font-family="Arial,sans-serif" font-size="13">?</text>
<text x="126" y="797" fill="#dbe7f3" font-family="Arial,sans-serif" font-size="13">Help center</text><text x="126" y="815" fill="#7f94ad" font-family="Arial,sans-serif" font-size="11">Guides and support</text>
<!-- main content -->
<text x="334" y="164" fill="#f8fafc" font-family="Arial,sans-serif" font-size="34" font-weight="700">Good morning, Alex</text>
<text x="334" y="196" fill="#91a5bf" font-family="Arial,sans-serif" font-size="16">Here is what is happening across your workspace today.</text>
<rect x="1300" y="142" width="190" height="42" rx="10" fill="#1b3048" stroke="#3b536e"/>
<text x="1320" y="168" fill="#c5d4e5" font-family="Arial,sans-serif" font-size="14">Last 30 days</text>
<!-- KPI cards -->
<g>
 <rect x="334" y="230" width="350" height="142" rx="15" fill="#17283d" stroke="#31465f"/>
 <rect x="704" y="230" width="350" height="142" rx="15" fill="#17283d" stroke="#31465f"/>
 <rect x="1074" y="230" width="416" height="142" rx="15" fill="#17283d" stroke="#31465f"/>
 <g fill="#91a5bf" font-family="Arial,sans-serif" font-size="14"><text x="360" y="267">Total revenue</text><text x="730" y="267">Active subscribers</text><text x="1100" y="267">Conversion rate</text></g>
 <g fill="#f1f5f9" font-family="Arial,sans-serif" font-size="34" font-weight="700"><text x="360" y="317">$84,254</text><text x="730" y="317">12,840</text><text x="1100" y="317">8.42%</text></g>
 <g fill="#5eead4" font-family="Arial,sans-serif" font-size="13"><text x="550" y="316">+12.8%</text><text x="920" y="316">+6.4%</text><text x="1365" y="316">+2.1%</text></g>
 <g fill="#7188a6" font-family="Arial,sans-serif" font-size="12"><text x="360" y="346">vs. previous period</text><text x="730" y="346">vs. previous period</text><text x="1100" y="346">vs. previous period</text></g>
</g>
<!-- analytics chart -->
<rect x="334" y="396" width="730" height="282" rx="15" fill="#17283d" stroke="#31465f"/>
<text x="360" y="435" fill="#e8eef6" font-family="Arial,sans-serif" font-size="18" font-weight="700">Revenue performance</text>
<text x="360" y="460" fill="#8298b3" font-family="Arial,sans-serif" font-size="12">Revenue over time · USD</text>
<g stroke="#2b4059" stroke-width="1"><path d="M390 500 H1025 M390 545 H1025 M390 590 H1025 M390 635 H1025"/></g>
<path d="M390 610 C440 590 460 602 500 566 S565 555 600 570 S665 520 710 535 S770 505 810 520 S875 470 915 490 S970 455 1025 465 L1025 635 L390 635 Z" fill="#2dd4bf" opacity=".10"/>
<path d="M390 610 C440 590 460 602 500 566 S565 555 600 570 S665 520 710 535 S770 505 810 520 S875 470 915 490 S970 455 1025 465" fill="none" stroke="url(#accent)" stroke-width="4" stroke-linecap="round"/>
<circle cx="915" cy="490" r="6" fill="#5eead4" stroke="#d5fffa" stroke-width="3"/>
<g fill="#7188a6" font-family="Arial,sans-serif" font-size="11"><text x="390" y="657">01 NOV</text><text x="540" y="657">08 NOV</text><text x="690" y="657">15 NOV</text><text x="840" y="657">22 NOV</text><text x="980" y="657">30 NOV</text></g>
<!-- right insight panel -->
<rect x="1084" y="396" width="406" height="282" rx="15" fill="#17283d" stroke="#31465f"/>
<text x="1110" y="435" fill="#e8eef6" font-family="Arial,sans-serif" font-size="18" font-weight="700">Channel insights</text>
<text x="1110" y="460" fill="#8298b3" font-family="Arial,sans-serif" font-size="12">Share of new subscriptions</text>
<g font-family="Arial,sans-serif" font-size="13">
 <text x="1110" y="510" fill="#c6d4e4">Organic search</text><text x="1448" y="510" fill="#e5edf6" text-anchor="end">42%</text>
 <rect x="1110" y="522" width="330" height="8" rx="4" fill="#2b4059"/><rect x="1110" y="522" width="139" height="8" rx="4" fill="#5eead4"/>
 <text x="1110" y="565" fill="#c6d4e4">Referral</text><text x="1448" y="565" fill="#e5edf6" text-anchor="end">31%</text>
 <rect x="1110" y="577" width="330" height="8" rx="4" fill="#2b4059"/><rect x="1110" y="577" width="102" height="8" rx="4" fill="#60a5fa"/>
 <text x="1110" y="620" fill="#c6d4e4">Paid campaigns</text><text x="1448" y="620" fill="#e5edf6" text-anchor="end">27%</text>
 <rect x="1110" y="632" width="330" height="8" rx="4" fill="#2b4059"/><rect x="1110" y="632" width="89" height="8" rx="4" fill="#a78bfa"/>
</g>
<!-- recent activity -->
<rect x="334" y="700" width="1156" height="126" rx="15" fill="#17283d" stroke="#31465f"/>
<text x="360" y="738" fill="#e8eef6" font-family="Arial,sans-serif" font-size="17" font-weight="700">Recent activity</text>
<g font-family="Arial,sans-serif" font-size="13">
 <text x="360" y="778" fill="#d5e0ed">New subscription</text><text x="600" y="778" fill="#91a5bf">Olivia Chen · Pro plan</text><text x="1438" y="778" fill="#5eead4" text-anchor="end">Just now</text>
 <path d="M360 792 H1460" stroke="#2b4059"/>
 <text x="360" y="815" fill="#d5e0ed">Campaign completed</text><text x="600" y="815" fill="#91a5bf">Autumn launch · 4,820 reached</text><text x="1438" y="815" fill="#91a5bf" text-anchor="end">18 min ago</text>
</g>
</svg>'''
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
