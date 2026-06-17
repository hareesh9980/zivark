import math
from .design_engine import ceiling


def get_material_rate(material):
    """Get rate from material object safely"""
    if material:
        return material.rate
    return 0


def get_material_name(material):
    """Get name from material object safely"""
    if material:
        return material.name
    return 'Unknown'


def build_bom(design):
    """
    Build complete BOM from design dict.
    Returns list of BOM items with all details.
    """
    bom  = []
    rule = design.get('rule')
    sr   = 1

    def add_item(description, material, l, w, h,
                 qty_nos, total_qty, uom, rate):
        nonlocal sr
        total_cost = round(total_qty * rate, 2)
        bom.append({
            'sr_no':        sr,
            'description':  description,
            'material':     get_material_name(material),
            'length_mm':    round(l) if l else 0,
            'width_mm':     round(w) if w else 0,
            'thickness_mm': round(h) if h else 0,
            'qty_nos':      qty_nos,
            'total_qty':    total_qty,
            'uom':          uom,
            'rate_per_uom': rate,
            'total_cost':   total_cost,
        })
        sr += 1

    # ── DECK ─────────────────────────────────
    deck_mat = design.get('deck_material')
    if deck_mat:
        add_item(
            'Deck',
            deck_mat,
            design['deck_length'],
            design['deck_w'],
            design['deck_h'],
            design['deck_qty'],
            design['deck_total_qty'],
            design['deck_uom'],
            get_material_rate(deck_mat),
        )

    # ── LENGTH RUNNER ────────────────────────
    if design.get('use_l_runner') and design.get('l_runner_material'):
        l_mat = design['l_runner_material']
        add_item(
            'Length Runner',
            l_mat,
            design['box_od_l'],
            design['l_runner_w'],
            design['l_runner_h'],
            design['l_runner_qty'],
            design['l_runner_total_qty'],
            'CFT',
            get_material_rate(l_mat),
        )

    # ── WIDTH RUNNER ─────────────────────────
    r_mat = design.get('runner_material')
    if r_mat and design['w_runner_qty'] > 0:
        add_item(
            'Width Runner',
            r_mat,
            design['box_od_w'],
            design['runner_w'],
            design['runner_h'],
            design['w_runner_qty'],
            design['w_runner_total_qty'],
            'CFT',
            get_material_rate(r_mat),
        )

    # ── LENGTH WALL ──────────────────────────
    wall_mat = design.get('wall_material')
    if wall_mat:
        add_item(
            'Length Wall',
            wall_mat,
            design['box_od_l'],
            design['box_id_h'],
            design['wall_t'],
            2,
            design['lwall_sqm'],
            'SQM',
            get_material_rate(wall_mat),
        )

    # ── LENGTH BEADING-L ─────────────────────
    b_mat = design.get('beading_material')
    if b_mat:
        add_item(
            'Length Beading-L',
            b_mat,
            design['box_od_l'],
            design['beading_w'],
            design['beading_h'],
            design['lb_l_qty'],
            design['lb_l_total_qty'],
            'CFT',
            get_material_rate(b_mat),
        )

        # ── LENGTH BEADING-H ─────────────────
        add_item(
            'Length Beading-H',
            b_mat,
            design['box_id_h'],
            design['beading_w'],
            design['beading_h'],
            design['lb_h_qty'],
            design['lb_h_total_qty'],
            'CFT',
            get_material_rate(b_mat),
        )

    # ── WIDTH WALL ───────────────────────────
    if wall_mat:
        add_item(
            'Width Wall',
            wall_mat,
            design['box_od_w'],
            design['box_id_h'],
            design['wall_t'],
            2,
            design['wwall_sqm'],
            'SQM',
            get_material_rate(wall_mat),
        )

    # ── WIDTH BEADING-W ──────────────────────
    if b_mat:
        add_item(
            'Width Beading-W',
            b_mat,
            design['box_od_w'],
            design['beading_w'],
            design['beading_h'],
            design['wb_w_qty'],
            design['wb_w_total_qty'],
            'CFT',
            get_material_rate(b_mat),
        )

        # ── WIDTH BEADING-H ──────────────────
        add_item(
            'Width Beading-H',
            b_mat,
            design['box_id_h'],
            design['beading_w'],
            design['beading_h'],
            design['wb_h_qty'],
            design['wb_h_total_qty'],
            'CFT',
            get_material_rate(b_mat),
        )

    # ── TOP WALL ─────────────────────────────
    top_mat = design.get('top_material') or wall_mat
    if top_mat:
        add_item(
            'Top Wall',
            top_mat,
            design['box_od_l'],
            design['box_od_w'],
            design['wall_t'],
            1,
            design['twall_sqm'],
            'SQM',
            get_material_rate(top_mat),
        )

    # ── TOP BEADING-L ────────────────────────
    if b_mat:
        add_item(
            'Top Beading-L',
            b_mat,
            design['box_od_l'],
            design['beading_w'],
            design['beading_h'],
            design['top_bl_qty'],
            design['top_bl_total_qty'],
            'CFT',
            get_material_rate(b_mat),
        )

        # ── TOP BEADING-W ────────────────────
        add_item(
            'Top Beading-W',
            b_mat,
            design['box_od_w'],
            design['beading_w'],
            design['beading_h'],
            design['top_bw_qty'],
            design['top_bw_total_qty'],
            'CFT',
            get_material_rate(b_mat),
        )

    # ── TOP CHOCKING ─────────────────────────
    chock_mat = design.get('chock_material')
    if chock_mat:
        add_item(
            'Top Chocking',
            chock_mat,
            design['box_od_w'],
            design['runner_w'],
            design['runner_h'],
            design['top_chock_qty'],
            design['top_chock_total_qty'],
            'CFT',
            get_material_rate(chock_mat),
        )

        # ── BOTTOM CHOCKING ──────────────────
        add_item(
            'Bottom Chocking',
            chock_mat,
            design['box_od_l'],
            design['runner_w'],
            75,
            design['bot_chock_qty'],
            design['bot_chock_total_qty'],
            'CFT',
            get_material_rate(chock_mat),
        )

    # ── GET HARDWARE FROM DB ─────────────────
    try:
        from materials.models import Material
        hardwares    = Material.objects.filter(
                        category='hardware', is_active=True)
        consumables  = Material.objects.filter(
                        category='consumable', is_active=True)
    except:
        hardwares   = []
        consumables = []

    # ── NAILS ────────────────────────────────
    nails = hardwares.filter(
        name__icontains='nail').first() if hardwares else None
    if nails:
        add_item(
            'Nails 32/55/80mm',
            nails,
            0, 0, 0,
            design['nails_qty'],
            design['nails_total_qty'],
            'NOS',
            get_material_rate(nails),
        )

    # ── NUT BOLT ─────────────────────────────
    nb = hardwares.filter(
        name__icontains='nut').first() if hardwares else None
    if nb:
        add_item(
            'N/B M10x12"',
            nb,
            0, 0, 0,
            design['nb_qty'],
            design['nb_qty'],
            'NOS',
            get_material_rate(nb),
        )

    # ── BW + SW ──────────────────────────────
    bw = consumables.filter(
        name__icontains='bubble').first() if consumables else None
    if bw:
        add_item(
            'BW & SW',
            bw,
            0, 0, 0,
            1.3,
            design['bw_qty'],
            'SQM',
            get_material_rate(bw),
        )

    # ── VCI SHEET ────────────────────────────
    vci = consumables.filter(
        name__icontains='vci').first() if consumables else None
    if vci:
        add_item(
            'VCI Sheet',
            vci,
            0, 0, 0,
            1.3,
            design['vci_qty'],
            'SQM',
            get_material_rate(vci),
        )

    # ── LASHING BELT ─────────────────────────
    lash = hardwares.filter(
        name__icontains='lash').first() if hardwares else None
    if lash:
        add_item(
            'Lashing Belt 32mm',
            lash,
            0, 0, 0,
            design['lashing_qty'],
            design['lashing_total_qty'],
            'MTR',
            get_material_rate(lash),
        )

    # ── WIRE BUCKLE ──────────────────────────
    buckle = hardwares.filter(
        name__icontains='buckle').first() if hardwares else None
    if buckle:
        add_item(
            'Wire Buckle 32mm',
            buckle,
            0, 0, 0,
            design['lashing_qty'],
            design['lashing_qty'],
            'NOS',
            get_material_rate(buckle),
        )

    # ── SILICA GEL ───────────────────────────
    silica = consumables.filter(
        name__icontains='silica').first() if consumables else None
    if silica:
        add_item(
            'Silica Gel',
            silica,
            0, 0, 0,
            design['silica_qty'],
            design['silica_qty'],
            'NOS',
            get_material_rate(silica),
        )

    return bom


def calculate_totals(bom, overhead_pct=7.0,
                     margin_pct=25.0, gst_pct=12.0):
    """
    Calculate final totals from BOM:
    Total Cost → Overhead → After OH →
    Margin → Before GST → GST → Grand Total
    """
    total_cost = sum(item['total_cost'] for item in bom)

    overhead_amount = round(total_cost * overhead_pct / 100, 2)
    after_overhead  = round(total_cost + overhead_amount, 2)
    margin_amount   = round(after_overhead * margin_pct / 100, 2)
    before_gst      = ceiling(
                        after_overhead + margin_amount, 100)
    gst_amount      = round(before_gst * gst_pct / 100, 2)
    grand_total     = round(before_gst + gst_amount, 2)

    return {
        'total_cost':      round(total_cost, 2),
        'overhead_pct':    overhead_pct,
        'overhead_amount': overhead_amount,
        'after_overhead':  after_overhead,
        'margin_pct':      margin_pct,
        'margin_amount':   margin_amount,
        'before_gst':      before_gst,
        'gst_pct':         gst_pct,
        'gst_amount':      gst_amount,
        'grand_total':     grand_total,
    }


def run_costing(design, overhead_pct=None,
                margin_pct=None, gst_pct=None):
    """
    Main costing function.
    Builds BOM and calculates totals.
    Uses rule percentages if not overridden.
    """
    # Use rule percentages if not manually overridden
    oh  = overhead_pct or design.get('overhead_pct', 7.0)
    mg  = margin_pct   or design.get('margin_pct',   25.0)
    gst = gst_pct      or design.get('gst_pct',      12.0)

    bom    = build_bom(design)
    totals = calculate_totals(bom, oh, mg, gst)

    return {
        'bom':    bom,
        'totals': totals,
    }