import math


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def cft(l_mm, w_mm, h_mm, qty, wastage_pct=5.0):
    """
    CFT = (L/1000) × (W/1000) × (H/1000)
          × qty × 35.315 × wastage_factor
    All dimensions in mm
    """
    if not l_mm or not w_mm or not h_mm:
        return 0
    wastage = 1 + (wastage_pct / 100)
    return round(
        (l_mm / 1000) *
        (w_mm / 1000) *
        (h_mm / 1000) *
        qty *
        35.315 *
        wastage,
        4
    )


def sqm(l_mm, w_mm, qty, wastage_pct=5.0):
    """
    SQM = (L/1000) × (W/1000) × qty × wastage
    All dimensions in mm
    """
    if not l_mm or not w_mm:
        return 0
    wastage = 1 + (wastage_pct / 100)
    return round(
        (l_mm / 1000) *
        (w_mm / 1000) *
        qty *
        wastage,
        4
    )


def roundup(value, divisor):
    """ROUNDUP(value/divisor, 0)"""
    if divisor == 0:
        return 0
    return math.ceil(value / divisor)


def ceiling(value, multiple):
    """CEILING(value, multiple) — round up to nearest multiple"""
    if multiple == 0:
        return value
    return math.ceil(value / multiple) * multiple


# ─────────────────────────────────────────────
# GET WEIGHT RULE
# ─────────────────────────────────────────────

def get_weight_rule(weight_kg):
    """
    Find matching WeightRule from database
    based on machine weight
    """
    from materials.models import WeightRule
    try:
        rule = WeightRule.objects.filter(
            weight_from__lte=weight_kg,
            weight_to__gte=weight_kg,
            is_active=True,
        ).order_by('weight_from').first()
        return rule
    except Exception as e:
        print(f"WeightRule error: {e}")
        return None


# ─────────────────────────────────────────────
# OD CALCULATION
# ─────────────────────────────────────────────

def calculate_od(id_l, id_w, id_h, rule,
                 override_beading_h=None,
                 override_wall_t=None,
                 override_deck_h=None,
                 override_runner_h=None):
    """
    OD_L = ID_L + beading_h + wall_t + wall_t + beading_h
    OD_W = ID_W + beading_h + wall_t + wall_t + beading_h
    OD_H = ID_H + deck_h + runner_h + wall_t + beading_h
    """
    beading_h = override_beading_h or (rule.beading_h if rule else 50)
    wall_t    = override_wall_t    or (rule.wall_t    if rule else 8)
    deck_h    = override_deck_h    or (rule.deck_h    if rule else 25)
    runner_h  = override_runner_h  or (rule.runner_h  if rule else 100)

    od_l = id_l + beading_h + wall_t + wall_t + beading_h
    od_w = id_w + beading_h + wall_t + wall_t + beading_h
    od_h = id_h + deck_h + runner_h + wall_t + beading_h

    return round(od_l), round(od_w), round(od_h)


# ─────────────────────────────────────────────
# VOLUME CALCULATION
# ─────────────────────────────────────────────

def calculate_volumes(od_l, od_w, od_h):
    """CBM, Total Area, Base Area"""
    cbm = round((od_l/1000) * (od_w/1000) * (od_h/1000), 3)

    total_area = round(
        2 * (od_l/1000) * (od_w/1000) +
        2 * (od_l/1000) * (od_h/1000) +
        2 * (od_w/1000) * (od_h/1000),
        3
    )

    base_area = round((od_l/1000) * (od_w/1000), 3)

    return {
        'cbm':            cbm,
        'total_area_sqm': total_area,
        'base_area_sqm':  base_area,
    }


# ─────────────────────────────────────────────
# MAIN DESIGN ENGINE
# ─────────────────────────────────────────────

def run_design(
    id_l, id_w, id_h,
    weight_kg,
    access_type='2_access',
    shipment_type='export',
    wood_type='ad',
    wastage_pct=5.0,
    product_name='Box',

    # Manual overrides (all optional)
    override_deck_w=None,
    override_deck_h=None,
    override_runner_w=None,
    override_runner_h=None,
    override_l_runner_w=None,
    override_l_runner_h=None,
    override_beading_w=None,
    override_beading_h=None,
    override_wall_t=None,
):
    """
    Main design engine — reads from Material Master
    and Weight Rules in database.
    Returns complete design dict with all BOM data.
    """

    # ── GET WEIGHT RULE ──────────────────────
    rule = get_weight_rule(weight_kg)

    if not rule:
        # Fallback defaults if no rule found
        return _fallback_design(
            id_l, id_w, id_h, weight_kg,
            wastage_pct, product_name
        )

    # ── APPLY OVERRIDES ──────────────────────
    deck_w    = override_deck_w    or rule.deck_w
    deck_h    = override_deck_h    or rule.deck_h
    runner_w  = override_runner_w  or rule.runner_w
    runner_h  = override_runner_h  or rule.runner_h
    l_runner_w= override_l_runner_w or rule.l_runner_w
    l_runner_h= override_l_runner_h or rule.l_runner_h
    beading_w = override_beading_w or rule.beading_w
    beading_h = override_beading_h or rule.beading_h
    wall_t    = override_wall_t    or rule.wall_t

    # ── OD CALCULATION ───────────────────────
    od_l, od_w, od_h = calculate_od(
        id_l, id_w, id_h, rule,
        override_beading_h=override_beading_h,
        override_wall_t=override_wall_t,
        override_deck_h=override_deck_h,
        override_runner_h=override_runner_h,
    )

    # ── VOLUMES ──────────────────────────────
    volumes = calculate_volumes(od_l, od_w, od_h)
    cbm          = volumes['cbm']
    total_area   = volumes['total_area_sqm']
    base_area    = volumes['base_area_sqm']

    # ── DECK ─────────────────────────────────
    # If OD_L > 2500, planks run along width
    if od_l > 2500:
        deck_length = od_w
        deck_span   = od_l
    else:
        deck_length = od_l
        deck_span   = od_w

    deck_qty = roundup(deck_span, rule.deck_pitch)

    # Deck material
    deck_mat = rule.deck_material
    if deck_mat and deck_mat.category == 'plywood':
        # Plywood deck → SQM
        deck_total_qty = sqm(od_l, od_w, 1, wastage_pct)
        deck_uom       = 'SQM'
    else:
        # Solid wood deck → CFT
        deck_total_qty = cft(deck_length, deck_w, deck_h,
                             deck_qty, wastage_pct)
        deck_uom       = 'CFT'

    # ── LENGTH RUNNER ────────────────────────
    use_l_runner = rule.use_l_runner
    if use_l_runner and rule.l_runner_material:
        l_runner_qty       = roundup(od_w, rule.l_runner_pitch)
        l_runner_total_qty = cft(od_l, l_runner_w, l_runner_h,
                                  l_runner_qty, wastage_pct)
    else:
        l_runner_qty       = 0
        l_runner_total_qty = 0

    # ── WIDTH RUNNER ─────────────────────────
    w_runner_qty       = roundup(od_l, rule.w_runner_pitch)
    w_runner_total_qty = cft(od_w, runner_w, runner_h,
                              w_runner_qty, wastage_pct)

    # ── LENGTH WALL ──────────────────────────
    lwall_sqm = sqm(od_l, id_h, 2, wastage_pct)

    # ── LENGTH BEADING-L ─────────────────────
    lb_l_qty       = roundup(id_h, rule.lb_l_pitch) * 2
    lb_l_total_qty = cft(od_l, beading_w, beading_h,
                          lb_l_qty, wastage_pct)

    # ── LENGTH BEADING-H ─────────────────────
    lb_h_qty       = roundup(od_l, rule.lb_h_pitch) * 2
    lb_h_total_qty = cft(id_h, beading_w, beading_h,
                          lb_h_qty, wastage_pct)

    # ── WIDTH WALL ───────────────────────────
    wwall_sqm = sqm(od_w, id_h, 2, wastage_pct)

    # ── WIDTH BEADING-W ──────────────────────
    wb_w_qty       = roundup(id_h, rule.wb_w_pitch) * 2
    wb_w_total_qty = cft(od_w, beading_w, beading_h,
                          wb_w_qty, wastage_pct)

    # ── WIDTH BEADING-H ──────────────────────
    wb_h_qty       = roundup(od_w, rule.wb_h_pitch) * 2
    wb_h_total_qty = cft(id_h, beading_w, beading_h,
                          wb_h_qty, wastage_pct)

    # ── TOP WALL ─────────────────────────────
    twall_sqm = sqm(od_l, od_w, 1, wastage_pct)

    # ── TOP BEADING-L ────────────────────────
    top_bl_qty       = roundup(od_w, rule.top_bl_pitch) * 2
    top_bl_total_qty = cft(od_l, beading_w, beading_h,
                            top_bl_qty, wastage_pct)

    # ── TOP BEADING-W ────────────────────────
    top_bw_qty       = roundup(od_l, rule.top_bw_pitch) * 2
    top_bw_total_qty = cft(od_w, beading_w, beading_h,
                            top_bw_qty, wastage_pct)

    # ── TOP CHOCKING ─────────────────────────
    top_chock_qty       = roundup(od_l, rule.top_chock_pitch)
    top_chock_total_qty = cft(od_w, runner_w, runner_h,
                               top_chock_qty, wastage_pct)

    # ── BOTTOM CHOCKING ──────────────────────
    bot_chock_qty       = roundup(od_w, rule.bot_chock_pitch)
    bot_chock_total_qty = cft(od_l, runner_w, 75,
                               bot_chock_qty, wastage_pct)

    # ── NAILS ────────────────────────────────
    nails_qty       = max(l_runner_qty or 1, 1) * w_runner_qty
    nails_total_qty = base_area

    # ── NUT BOLT ─────────────────────────────
    nb_qty = roundup(
        (od_l/250)*4 + (od_w/250)*4 + (od_h/250)*4,
        1
    )

    # ── LASHING BELT ─────────────────────────
    lashing_qty       = roundup(od_l, rule.lashing_pitch)
    lashing_total_qty = round(
        (od_w/1000 * 2) + (id_h/1000 * 2), 3
    )

    # ── SILICA GEL ───────────────────────────
    # 500g per CBM → calculate packets (use 50g packets)
    silica_qty = round(cbm * 500 / 50)  # number of 50g packets

    # ── BW + SW ──────────────────────────────
    bw_qty = total_area

    # ── VCI SHEET ────────────────────────────
    vci_qty = total_area

    # ── RETURN COMPLETE DESIGN ───────────────
    return {
        'product_name': product_name,
        'packing_type': 'box',

        # ID / OD
        'box_id_l': id_l,
        'box_id_w': id_w,
        'box_id_h': id_h,
        'box_od_l': od_l,
        'box_od_w': od_w,
        'box_od_h': od_h,

        # Volumes
        'volumes': volumes,

        # Weight
        'weight_kg': weight_kg,

        # Rule used
        'rule': rule,

        # Materials from rule
        'deck_material':      rule.deck_material,
        'runner_material':    rule.runner_material,
        'l_runner_material':  rule.l_runner_material,
        'beading_material':   rule.beading_material,
        'wall_material':      rule.wall_material,
        'top_material':       rule.top_material or rule.wall_material,
        'chock_material':     rule.chock_material,

        # Dimensions used
        'deck_w':    deck_w,
        'deck_h':    deck_h,
        'runner_w':  runner_w,
        'runner_h':  runner_h,
        'l_runner_w':l_runner_w,
        'l_runner_h':l_runner_h,
        'beading_w': beading_w,
        'beading_h': beading_h,
        'wall_t':    wall_t,

        # Deck
        'deck_qty':       deck_qty,
        'deck_total_qty': deck_total_qty,
        'deck_length':    deck_length,
        'deck_span':      deck_span,
        'deck_uom':       deck_uom,

        # Runners
        'use_l_runner':         use_l_runner,
        'l_runner_qty':         l_runner_qty,
        'l_runner_total_qty':   l_runner_total_qty,
        'w_runner_qty':         w_runner_qty,
        'w_runner_total_qty':   w_runner_total_qty,

        # Walls
        'lwall_sqm':  lwall_sqm,
        'wwall_sqm':  wwall_sqm,
        'twall_sqm':  twall_sqm,

        # Beading
        'lb_l_qty':       lb_l_qty,
        'lb_l_total_qty': lb_l_total_qty,
        'lb_h_qty':       lb_h_qty,
        'lb_h_total_qty': lb_h_total_qty,
        'wb_w_qty':       wb_w_qty,
        'wb_w_total_qty': wb_w_total_qty,
        'wb_h_qty':       wb_h_qty,
        'wb_h_total_qty': wb_h_total_qty,
        'top_bl_qty':       top_bl_qty,
        'top_bl_total_qty': top_bl_total_qty,
        'top_bw_qty':       top_bw_qty,
        'top_bw_total_qty': top_bw_total_qty,

        # Chocking
        'top_chock_qty':       top_chock_qty,
        'top_chock_total_qty': top_chock_total_qty,
        'bot_chock_qty':       bot_chock_qty,
        'bot_chock_total_qty': bot_chock_total_qty,

        # Hardware
        'nails_qty':       nails_qty,
        'nails_total_qty': nails_total_qty,
        'nb_qty':          nb_qty,

        # Lashing
        'lashing_qty':       lashing_qty,
        'lashing_total_qty': lashing_total_qty,

        # Consumables
        'silica_qty': silica_qty,
        'bw_qty':     bw_qty,
        'vci_qty':    vci_qty,

        # Formula config from rule
        'overhead_pct': rule.overhead_pct,
        'margin_pct':   rule.margin_pct,
        'gst_pct':      rule.gst_pct,
        'wastage_pct':  rule.wastage_pct,

        # Access / shipment
        'access_type':   access_type,
        'shipment_type': shipment_type,
    }


# ─────────────────────────────────────────────
# FALLBACK DESIGN (if no weight rule in DB)
# ─────────────────────────────────────────────

def _fallback_design(id_l, id_w, id_h,
                     weight_kg, wastage_pct,
                     product_name):
    """
    Emergency fallback — uses hardcoded defaults
    when no weight rule exists in database
    """
    beading_h = 50
    wall_t    = 8
    deck_h    = 25
    runner_h  = 100
    beading_w = 75
    runner_w  = 75
    deck_w    = 150

    od_l = round(id_l + beading_h*2 + wall_t*2)
    od_w = round(id_w + beading_h*2 + wall_t*2)
    od_h = round(id_h + deck_h + runner_h + wall_t + beading_h)

    volumes  = calculate_volumes(od_l, od_w, od_h)

    return {
        'product_name': product_name,
        'packing_type': 'box',
        'box_id_l': id_l,
        'box_id_w': id_w,
        'box_id_h': id_h,
        'box_od_l': od_l,
        'box_od_w': od_w,
        'box_od_h': od_h,
        'volumes':  volumes,
        'weight_kg': weight_kg,
        'rule':     None,
        'deck_material':    None,
        'runner_material':  None,
        'l_runner_material':None,
        'beading_material': None,
        'wall_material':    None,
        'top_material':     None,
        'chock_material':   None,
        'deck_w': deck_w, 'deck_h': deck_h,
        'runner_w': runner_w, 'runner_h': runner_h,
        'beading_w': beading_w, 'beading_h': beading_h,
        'wall_t': wall_t,
        'deck_qty': 0, 'deck_total_qty': 0,
        'deck_length': od_l, 'deck_span': od_w,
        'deck_uom': 'CFT',
        'use_l_runner': False,
        'l_runner_qty': 0, 'l_runner_total_qty': 0,
        'w_runner_qty': 0, 'w_runner_total_qty': 0,
        'lwall_sqm': 0, 'wwall_sqm': 0, 'twall_sqm': 0,
        'lb_l_qty': 0, 'lb_l_total_qty': 0,
        'lb_h_qty': 0, 'lb_h_total_qty': 0,
        'wb_w_qty': 0, 'wb_w_total_qty': 0,
        'wb_h_qty': 0, 'wb_h_total_qty': 0,
        'top_bl_qty': 0, 'top_bl_total_qty': 0,
        'top_bw_qty': 0, 'top_bw_total_qty': 0,
        'top_chock_qty': 0, 'top_chock_total_qty': 0,
        'bot_chock_qty': 0, 'bot_chock_total_qty': 0,
        'nails_qty': 0, 'nails_total_qty': 0,
        'nb_qty': 0,
        'lashing_qty': 0, 'lashing_total_qty': 0,
        'silica_qty': 0, 'bw_qty': 0, 'vci_qty': 0,
        'overhead_pct': 7.0, 'margin_pct': 25.0,
        'gst_pct': 12.0, 'wastage_pct': 5.0,
        'access_type': '2_access',
        'shipment_type': 'export',
    }