import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from materials.models import Material, WeightRule

print("Creating materials...")

# ── SOLID WOODS ──────────────────────────────
pine_2x3 = Material.objects.create(
    name='Pinewood AD 2x3', category='solid_wood',
    wood_type='Pinewood', wood_grade='AD',
    width_mm=50, height_mm=75,
    uom='CFT', rate=841,
)
pine_2x6 = Material.objects.create(
    name='Pinewood AD 2x6', category='solid_wood',
    wood_type='Pinewood', wood_grade='AD',
    width_mm=50, height_mm=150,
    uom='CFT', rate=841,
)
pine_3x4 = Material.objects.create(
    name='Pinewood AD 3x4', category='solid_wood',
    wood_type='Pinewood', wood_grade='AD',
    width_mm=75, height_mm=100,
    uom='CFT', rate=841,
)
pine_4x4 = Material.objects.create(
    name='Pinewood AD 4x4', category='solid_wood',
    wood_type='Pinewood', wood_grade='AD',
    width_mm=100, height_mm=100,
    uom='CFT', rate=841,
)

# ── PLYWOOD ──────────────────────────────────
ply_8mm = Material.objects.create(
    name='8mm BWR Plywood', category='plywood',
    wood_grade='BWR', thickness_mm=8,
    uom='SQM', rate=339,
)
ply_12mm = Material.objects.create(
    name='12mm BWR Plywood', category='plywood',
    wood_grade='BWR', thickness_mm=12,
    uom='SQM', rate=450,
)

# ── HARDWARE ─────────────────────────────────
nails = Material.objects.create(
    name='Nails 32/55/80mm', category='hardware',
    description='Common wire nails',
    uom='NOS', rate=1,
)
nut_bolt = Material.objects.create(
    name='Nut Bolt M10x12', category='hardware',
    description='M10x12 hex bolt with nut',
    uom='NOS', rate=18,
)
lashing = Material.objects.create(
    name='Lashing Belt 32mm', category='hardware',
    description='Polyester lashing belt 32mm 3T',
    uom='MTR', rate=10,
)
buckle = Material.objects.create(
    name='Wire Buckle 32mm', category='hardware',
    description='Steel wire buckle 32mm',
    uom='NOS', rate=8,
)

# ── CONSUMABLES ──────────────────────────────
bw_sw = Material.objects.create(
    name='Bubble Wrap + Stretch Wrap', category='consumable',
    description='20mm bubble wrap + 25 micron stretch wrap',
    uom='SQM', rate=9,
)
vci = Material.objects.create(
    name='VCI Sheet', category='consumable',
    description='VCI anti-corrosion film 50 micron',
    uom='SQM', rate=18,
)
silica = Material.objects.create(
    name='Silica Gel 50g', category='consumable',
    description='50g silica gel packets',
    uom='NOS', rate=7,
)

print("Materials created!")
print("Creating weight rules...")

# ── WEIGHT RULE 1: Light (0-700kg) ───────────
WeightRule.objects.create(
    name='Light 0-700kg',
    weight_from=0, weight_to=700,
    deck_material=ply_8mm,
    wall_material=ply_8mm,
    top_material=ply_8mm,
    beading_material=pine_2x3,
    runner_material=pine_3x4,
    chock_material=pine_3x4,
    deck_w=0, deck_h=8,
    runner_w=100, runner_h=100,
    beading_w=50, beading_h=50,
    wall_t=8,
    use_l_runner=False,
    deck_pitch=140,
    w_runner_pitch=600,
    lb_l_pitch=700, lb_h_pitch=900,
    wb_w_pitch=700, wb_h_pitch=500,
    top_bl_pitch=600, top_bw_pitch=700,
    top_chock_pitch=500, bot_chock_pitch=500,
    lashing_pitch=600,
    overhead_pct=7, margin_pct=25, gst_pct=12, wastage_pct=5,
)

# ── WEIGHT RULE 2: Medium (700-1500kg) ───────
WeightRule.objects.create(
    name='Medium 700-1500kg',
    weight_from=700, weight_to=1500,
    deck_material=pine_2x3,
    wall_material=ply_8mm,
    top_material=ply_8mm,
    beading_material=pine_2x3,
    runner_material=pine_3x4,
    chock_material=pine_3x4,
    deck_w=150, deck_h=25,
    runner_w=100, runner_h=100,
    beading_w=50, beading_h=50,
    wall_t=8,
    use_l_runner=False,
    deck_pitch=140,
    w_runner_pitch=600,
    lb_l_pitch=700, lb_h_pitch=900,
    wb_w_pitch=700, wb_h_pitch=500,
    top_bl_pitch=600, top_bw_pitch=700,
    top_chock_pitch=500, bot_chock_pitch=500,
    lashing_pitch=600,
    overhead_pct=7, margin_pct=25, gst_pct=12, wastage_pct=5,
)

# ── WEIGHT RULE 3: Heavy (1500-4500kg) ───────
WeightRule.objects.create(
    name='Heavy 1500-4500kg',
    weight_from=1500, weight_to=4500,
    deck_material=pine_2x6,
    wall_material=ply_8mm,
    top_material=ply_8mm,
    beading_material=pine_2x3,
    runner_material=pine_3x4,
    l_runner_material=pine_4x4,
    chock_material=pine_4x4,
    deck_w=150, deck_h=50,
    runner_w=75, runner_h=100,
    l_runner_w=100, l_runner_h=100,
    beading_w=75, beading_h=50,
    wall_t=8,
    use_l_runner=True,
    deck_pitch=140,
    l_runner_pitch=500,
    w_runner_pitch=600,
    lb_l_pitch=700, lb_h_pitch=900,
    wb_w_pitch=700, wb_h_pitch=500,
    top_bl_pitch=600, top_bw_pitch=700,
    top_chock_pitch=500, bot_chock_pitch=500,
    lashing_pitch=600,
    overhead_pct=7, margin_pct=25, gst_pct=12, wastage_pct=5,
)

# ── WEIGHT RULE 4: Very Heavy (4500-8000kg) ──
WeightRule.objects.create(
    name='Very Heavy 4500-8000kg',
    weight_from=4500, weight_to=8000,
    deck_material=pine_2x6,
    wall_material=ply_8mm,
    top_material=ply_8mm,
    beading_material=pine_2x3,
    runner_material=pine_4x4,
    l_runner_material=pine_4x4,
    chock_material=pine_4x4,
    deck_w=150, deck_h=50,
    runner_w=100, runner_h=100,
    l_runner_w=100, l_runner_h=100,
    beading_w=75, beading_h=50,
    wall_t=8,
    use_l_runner=True,
    deck_pitch=140,
    l_runner_pitch=500,
    w_runner_pitch=600,
    lb_l_pitch=700, lb_h_pitch=900,
    wb_w_pitch=700, wb_h_pitch=500,
    top_bl_pitch=600, top_bw_pitch=700,
    top_chock_pitch=500, bot_chock_pitch=500,
    lashing_pitch=600,
    overhead_pct=7, margin_pct=25, gst_pct=12, wastage_pct=5,
)

print("Weight rules created!")
print("\nAll done! Run test_engine.py again to verify.")