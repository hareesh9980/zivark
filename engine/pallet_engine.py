import math


def get_formula_config():
    try:
        from materials.models import FormulaConfig
        return FormulaConfig.get_active()
    except:
        return None


def cft(l, w, h, qty, wastage_pct=5.0):
    wastage = 1 + (wastage_pct / 100)
    return round(
        (l/1000)*(w/1000)*(h/1000)*qty*(3.28**3)*wastage, 4
    )


def sqm(l, w, qty, wastage_pct=5.0):
    wastage = 1 + (wastage_pct / 100)
    return round((l/1000)*(w/1000)*qty*wastage, 4)


def get_weight_rule(weight_kg):
    from materials.models import WeightRule
    try:
        return WeightRule.objects.filter(
            weight_from__lte=weight_kg,
            weight_to__gte=weight_kg,
            is_active=True,
        ).order_by('weight_from').first()
    except:
        return None


def run_pallet_design(
    id_l, id_w, id_h,
    weight_kg,
    shipment_type='domestic',
    pallet_deck_type='auto',
    wood_type='ad',
    product_name='Pallet',
    deck_w=None, deck_h=None,
    runner_w=None, runner_h=None,
    l_runner_w=None, l_runner_h=None,
    deck_pitch=140,
    l_runner_pitch=500,
    w_runner_pitch=600,
    bot_chock_pitch=500,
    lashing_pitch=600,
    lashing_size='32mm',
):
    # ── GET CONFIG ───────────────────────────
    cfg         = get_formula_config()
    wastage_pct = cfg.cft_wastage_pct if cfg else 5.0
    sqm_wastage = cfg.sqm_wastage_pct if cfg else 5.0

    silica_grams_per_cbm = cfg.silica_gel_grams_per_cbm if cfg else 500.0
    silica_packet_grams  = cfg.silica_gel_packet_grams  if cfg else 50.0

    # ── GET WEIGHT RULE ──────────────────────
    rule = get_weight_rule(weight_kg)

    # ── DIMENSIONS ──────────────────────────
    p_deck_w  = deck_w     or (rule.deck_w     if rule else 150)
    p_deck_h  = deck_h     or (rule.deck_h     if rule else 50)
    p_run_w   = runner_w   or (rule.runner_w   if rule else 100)
    p_run_h   = runner_h   or (rule.runner_h   if rule else 100)
    p_lrun_w  = l_runner_w or (rule.l_runner_w if rule else 100)
    p_lrun_h  = l_runner_h or (rule.l_runner_h if rule else 100)

    # ── OD (pallet) ──────────────────────────
    # Pallet OD = ID + 50mm each side (standard overhang)
    od_l = id_l + 50
    od_w = id_w + 50
    od_h = p_run_h + p_deck_h

    # ── VOLUMES ──────────────────────────────
    cbm        = round((od_l/1000)*(od_w/1000)*(id_h/1000), 3)
    total_area = round(
        2*(od_l/1000)*(od_w/1000) +
        2*(od_l/1000)*(id_h/1000) +
        2*(od_w/1000)*(id_h/1000), 3)
    base_area  = round((od_l/1000)*(od_w/1000), 3)
    volumes    = {
        'cbm':            cbm,
        'total_area_sqm': total_area,
        'base_area_sqm':  base_area,
    }

    # ── DECK TYPE ────────────────────────────
    # Auto: if id_l <= 1500 → plywood, else by weight rule
    if pallet_deck_type == 'auto':
        if id_l <= 1500:
            final_deck_type = 'plywood'
        else:
            deck_mat = rule.deck_material if rule else None
            final_deck_type = (
                'plywood' if deck_mat and
                deck_mat.category == 'plywood'
                else 'solid_wood'
            )
    else:
        final_deck_type = pallet_deck_type

    # ── DECK CALCULATION ─────────────────────
    if od_l > 2500:
        deck_length = od_w
        deck_span   = od_l
    else:
        deck_length = od_l
        deck_span   = od_w

    deck_qty = math.ceil(deck_span / deck_pitch)

    deck_material = rule.deck_material if rule else None

    if final_deck_type == 'plywood':
        deck_qty        = 1
        deck_h_use      = deck_h or 8  # use override if given
        deck_total_qty  = sqm(od_l, od_w, 1, sqm_wastage)
        deck_uom        = 'SQM'
    else:
        deck_h_use      = p_deck_h
        deck_total_qty  = cft(deck_length, p_deck_w,
                              p_deck_h, deck_qty, wastage_pct)
        deck_uom        = 'CFT'

    # ── WIDTH RUNNER ─────────────────────────
    w_runner_pitch_val = (rule.w_runner_pitch
                          if rule else w_runner_pitch)
    w_runner_qty       = math.ceil(od_l / w_runner_pitch_val)
    w_runner_total_qty = cft(od_w, p_run_w, p_run_h,
                             w_runner_qty, wastage_pct)
    runner_material    = rule.runner_material if rule else None

    # ── LENGTH RUNNER ─────────────────────────
    use_l_runner       = rule.use_l_runner if rule else False
    l_runner_material  = rule.l_runner_material if rule else None

    if use_l_runner and l_runner_material:
        l_runner_pitch_val = (rule.l_runner_pitch
                              if rule else l_runner_pitch)
        l_runner_qty       = math.ceil(od_w / l_runner_pitch_val)
        l_runner_total_qty = cft(od_l, p_lrun_w, p_lrun_h,
                                 l_runner_qty, wastage_pct)
    else:
        l_runner_qty       = 0
        l_runner_total_qty = 0

    # ── BOTTOM CHOCKING ───────────────────────
    bot_chock_pitch_val = (rule.bot_chock_pitch
                           if rule else bot_chock_pitch)
    bot_chock_qty       = math.ceil(od_w / bot_chock_pitch_val)
    bot_chock_total_qty = cft(od_l, p_run_w, 75,
                              bot_chock_qty, wastage_pct)
    chock_material      = rule.chock_material if rule else None

    # ── NAILS ────────────────────────────────
    nails_qty       = max(l_runner_qty or 1, 1) * w_runner_qty
    nails_total_qty = base_area

    # ── NUT BOLT ─────────────────────────────
    nb_qty = math.ceil(
        (od_l/250)*4 + (od_w/250)*4 + (od_h/250)*4)

    # ── LASHING ──────────────────────────────
    lashing_pitch_val = (rule.lashing_pitch
                         if rule else lashing_pitch)
    lashing_qty       = math.ceil(od_l / lashing_pitch_val)
    lashing_total_qty = round(
        (od_w/1000*2) + (id_h/1000*2), 3)

    # ── SILICA GEL ───────────────────────────
    silica_qty = round(
        cbm * silica_grams_per_cbm / silica_packet_grams)

    return {
        'product_name':    product_name,
        'packing_type':    'pallet',

        'box_id_l': id_l,
        'box_id_w': id_w,
        'box_id_h': id_h,
        'box_od_l': od_l,
        'box_od_w': od_w,
        'box_od_h': od_h,

        'weight_kg':     weight_kg,
        'shipment_type': shipment_type,
        'wood_type':     wood_type,
        'access_type':   '2_access',
        'volumes':       volumes,

        'rule':              rule,
        'pallet_deck_type':  final_deck_type,
        'cft_wastage_pct':   wastage_pct,
        'sqm_wastage_pct':   sqm_wastage,

        # Materials
        'deck_material':     deck_material,
        'runner_material':   runner_material,
        'l_runner_material': l_runner_material,
        'beading_material':  None,
        'wall_material':     None,
        'top_material':      None,
        'chock_material':    chock_material,

        # Dimensions
        'deck_w':     p_deck_w,
        'deck_h':     deck_h_use,
        'runner_w':   p_run_w,
        'runner_h':   p_run_h,
        'l_runner_w': p_lrun_w,
        'l_runner_h': p_lrun_h,
        'beading_w':  0,
        'beading_h':  0,
        'wall_t':     0,

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

        # Walls (pallet has none)
        'lwall_sqm': 0, 'wwall_sqm': 0, 'twall_sqm': 0,

        # Beading (pallet has none)
        'lb_l_qty': 0, 'lb_l_total_qty': 0,
        'lb_h_qty': 0, 'lb_h_total_qty': 0,
        'wb_w_qty': 0, 'wb_w_total_qty': 0,
        'wb_h_qty': 0, 'wb_h_total_qty': 0,
        'top_bl_qty': 0, 'top_bl_total_qty': 0,
        'top_bw_qty': 0, 'top_bw_total_qty': 0,
        'top_chock_qty': 0, 'top_chock_total_qty': 0,

        # Chocking
        'bot_chock_qty':       bot_chock_qty,
        'bot_chock_total_qty': bot_chock_total_qty,

        # Hardware
        'nails_qty':       nails_qty,
        'nails_total_qty': nails_total_qty,
        'nb_qty':          nb_qty,

        # Lashing
        'lashing_size':       lashing_size,
        'lashing_qty':        lashing_qty,
        'lashing_total_qty':  lashing_total_qty,

        # Consumables
        'silica_qty': silica_qty,
        'bw_qty':     total_area,
        'vci_qty':    total_area,

        # Pricing from rule
        'overhead_pct': rule.overhead_pct if rule else 7.0,
        'margin_pct':   rule.margin_pct   if rule else 25.0,
        'gst_pct':      rule.gst_pct      if rule else 12.0,
        'wastage_pct':  wastage_pct,
    }