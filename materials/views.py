from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Material, WeightRule, HardwareConfig


@login_required
def material_list(request):
    solid_woods  = Material.objects.filter(category='solid_wood', is_active=True)
    plywoods     = Material.objects.filter(category='plywood',    is_active=True)
    hardwares    = Material.objects.filter(category='hardware',   is_active=True)
    consumables  = Material.objects.filter(category='consumable', is_active=True)
    steels       = Material.objects.filter(category='steel',      is_active=True)
    weight_rules = WeightRule.objects.filter(is_active=True)

    return render(request, 'materials/list.html', {
        'solid_woods':  solid_woods,
        'plywoods':     plywoods,
        'hardwares':    hardwares,
        'consumables':  consumables,
        'steels':       steels,
        'weight_rules': weight_rules,
    })


@login_required
def material_add(request):
    if request.method == 'POST':
        mat = Material.objects.create(
            name        = request.POST.get('name'),
            category    = request.POST.get('category'),
            wood_type   = request.POST.get('wood_type', ''),
            wood_grade  = request.POST.get('wood_grade', 'NA'),
            width_mm    = float(request.POST.get('width_mm') or 0),
            height_mm   = float(request.POST.get('height_mm') or 0),
            thickness_mm= float(request.POST.get('thickness_mm') or 0),
            uom         = request.POST.get('uom'),
            rate        = float(request.POST.get('rate') or 0),
            notes       = request.POST.get('notes', ''),
        )
        messages.success(request, f'Material "{mat.name}" added successfully!')
        return redirect('materials:list')
    return render(request, 'materials/add.html', {
        'categories': Material.CATEGORY_CHOICES,
        'grades':     Material.GRADE_CHOICES,
        'uoms':       Material.UOM_CHOICES,
    })


@login_required
def material_edit(request, pk):
    mat = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        mat.name         = request.POST.get('name')
        mat.category     = request.POST.get('category')
        mat.wood_type    = request.POST.get('wood_type', '')
        mat.wood_grade   = request.POST.get('wood_grade', 'NA')
        mat.width_mm     = float(request.POST.get('width_mm') or 0)
        mat.height_mm    = float(request.POST.get('height_mm') or 0)
        mat.thickness_mm = float(request.POST.get('thickness_mm') or 0)
        mat.uom          = request.POST.get('uom')
        mat.rate         = float(request.POST.get('rate') or 0)
        mat.notes        = request.POST.get('notes', '')
        mat.save()
        messages.success(request, f'Material "{mat.name}" updated!')
        return redirect('materials:list')
    return render(request, 'materials/edit.html', {
        'mat':        mat,
        'categories': Material.CATEGORY_CHOICES,
        'grades':     Material.GRADE_CHOICES,
        'uoms':       Material.UOM_CHOICES,
    })


@login_required
def material_toggle(request, pk):
    mat = get_object_or_404(Material, pk=pk)
    mat.is_active = not mat.is_active
    mat.save()
    status = 'activated' if mat.is_active else 'deactivated'
    messages.success(request, f'Material "{mat.name}" {status}!')
    return redirect('materials:list')


@login_required
def weight_rule_add(request):
    materials = Material.objects.filter(is_active=True)
    if request.method == 'POST':
        def get_mat(field):
            val = request.POST.get(field)
            if val:
                try:
                    return Material.objects.get(pk=int(val))
                except:
                    return None
            return None

        rule = WeightRule.objects.create(
            name        = request.POST.get('name'),
            weight_from = float(request.POST.get('weight_from') or 0),
            weight_to   = float(request.POST.get('weight_to') or 0),

            deck_material     = get_mat('deck_material'),
            runner_material   = get_mat('runner_material'),
            l_runner_material = get_mat('l_runner_material'),
            beading_material  = get_mat('beading_material'),
            wall_material     = get_mat('wall_material'),
            top_material      = get_mat('top_material'),
            chock_material    = get_mat('chock_material'),

            deck_w    = float(request.POST.get('deck_w') or 150),
            deck_h    = float(request.POST.get('deck_h') or 50),
            runner_w  = float(request.POST.get('runner_w') or 75),
            runner_h  = float(request.POST.get('runner_h') or 100),
            l_runner_w= float(request.POST.get('l_runner_w') or 100),
            l_runner_h= float(request.POST.get('l_runner_h') or 100),
            beading_w = float(request.POST.get('beading_w') or 75),
            beading_h = float(request.POST.get('beading_h') or 50),
            wall_t    = float(request.POST.get('wall_t') or 8),
            use_l_runner = request.POST.get('use_l_runner') == 'on',

            deck_pitch      = float(request.POST.get('deck_pitch') or 140),
            l_runner_pitch  = float(request.POST.get('l_runner_pitch') or 500),
            w_runner_pitch  = float(request.POST.get('w_runner_pitch') or 600),
            lb_l_pitch      = float(request.POST.get('lb_l_pitch') or 700),
            lb_h_pitch      = float(request.POST.get('lb_h_pitch') or 900),
            wb_w_pitch      = float(request.POST.get('wb_w_pitch') or 700),
            wb_h_pitch      = float(request.POST.get('wb_h_pitch') or 500),
            top_bl_pitch    = float(request.POST.get('top_bl_pitch') or 600),
            top_bw_pitch    = float(request.POST.get('top_bw_pitch') or 700),
            top_chock_pitch = float(request.POST.get('top_chock_pitch') or 500),
            bot_chock_pitch = float(request.POST.get('bot_chock_pitch') or 500),
            lashing_pitch   = float(request.POST.get('lashing_pitch') or 600),

            overhead_pct = float(request.POST.get('overhead_pct') or 7),
            margin_pct   = float(request.POST.get('margin_pct') or 25),
            gst_pct      = float(request.POST.get('gst_pct') or 12),
            wastage_pct  = float(request.POST.get('wastage_pct') or 5),
        )
        messages.success(request, f'Weight Rule "{rule.name}" added!')
        return redirect('materials:list')

    return render(request, 'materials/weight_rule_add.html', {
        'materials':   materials,
        'solid_woods': materials.filter(category='solid_wood'),
        'plywoods':    materials.filter(category='plywood'),
    })


@login_required
def weight_rule_edit(request, pk):
    rule      = get_object_or_404(WeightRule, pk=pk)
    materials = Material.objects.filter(is_active=True)

    if request.method == 'POST':
        def get_mat(field):
            val = request.POST.get(field)
            if val:
                try:
                    return Material.objects.get(pk=int(val))
                except:
                    return None
            return None

        rule.name        = request.POST.get('name')
        rule.weight_from = float(request.POST.get('weight_from') or 0)
        rule.weight_to   = float(request.POST.get('weight_to') or 0)

        rule.deck_material     = get_mat('deck_material')
        rule.runner_material   = get_mat('runner_material')
        rule.l_runner_material = get_mat('l_runner_material')
        rule.beading_material  = get_mat('beading_material')
        rule.wall_material     = get_mat('wall_material')
        rule.top_material      = get_mat('top_material')
        rule.chock_material    = get_mat('chock_material')

        rule.deck_w    = float(request.POST.get('deck_w') or 150)
        rule.deck_h    = float(request.POST.get('deck_h') or 50)
        rule.runner_w  = float(request.POST.get('runner_w') or 75)
        rule.runner_h  = float(request.POST.get('runner_h') or 100)
        rule.beading_w = float(request.POST.get('beading_w') or 75)
        rule.beading_h = float(request.POST.get('beading_h') or 50)
        rule.wall_t    = float(request.POST.get('wall_t') or 8)
        rule.use_l_runner = request.POST.get('use_l_runner') == 'on'

        rule.deck_pitch      = float(request.POST.get('deck_pitch') or 140)
        rule.l_runner_pitch  = float(request.POST.get('l_runner_pitch') or 500)
        rule.w_runner_pitch  = float(request.POST.get('w_runner_pitch') or 600)
        rule.lb_l_pitch      = float(request.POST.get('lb_l_pitch') or 700)
        rule.lb_h_pitch      = float(request.POST.get('lb_h_pitch') or 900)
        rule.wb_w_pitch      = float(request.POST.get('wb_w_pitch') or 700)
        rule.wb_h_pitch      = float(request.POST.get('wb_h_pitch') or 500)
        rule.top_bl_pitch    = float(request.POST.get('top_bl_pitch') or 600)
        rule.top_bw_pitch    = float(request.POST.get('top_bw_pitch') or 700)
        rule.top_chock_pitch = float(request.POST.get('top_chock_pitch') or 500)
        rule.bot_chock_pitch = float(request.POST.get('bot_chock_pitch') or 500)
        rule.lashing_pitch   = float(request.POST.get('lashing_pitch') or 600)

        rule.overhead_pct = float(request.POST.get('overhead_pct') or 7)
        rule.margin_pct   = float(request.POST.get('margin_pct') or 25)
        rule.gst_pct      = float(request.POST.get('gst_pct') or 12)
        rule.wastage_pct  = float(request.POST.get('wastage_pct') or 5)

        rule.save()
        messages.success(request, f'Weight Rule "{rule.name}" updated!')
        return redirect('materials:list')

    return render(request, 'materials/weight_rule_edit.html', {
        'rule':        rule,
        'materials':   materials,
        'solid_woods': materials.filter(category='solid_wood'),
        'plywoods':    materials.filter(category='plywood'),
    })


from .models import Material, WeightRule, HardwareConfig, FormulaConfig

@login_required
def formula_config(request):
    cfg = FormulaConfig.get_active()
    if request.method == 'POST':
        cfg.cft_wastage_pct          = float(request.POST.get('cft_wastage_pct', 5))
        cfg.sqm_wastage_pct          = float(request.POST.get('sqm_wastage_pct', 5))
        cfg.steel_wastage_pct        = float(request.POST.get('steel_wastage_pct', 2))
        cfg.cft_conversion           = float(request.POST.get('cft_conversion', 35.315))
        cfg.overhead_pct             = float(request.POST.get('overhead_pct', 7))
        cfg.margin_pct               = float(request.POST.get('margin_pct', 25))
        cfg.gst_pct                  = float(request.POST.get('gst_pct', 12))
        cfg.labour_rate_per_hour     = float(request.POST.get('labour_rate_per_hour', 100))
        cfg.labour_hours_default     = float(request.POST.get('labour_hours_default', 8))
        cfg.lashing_belts_per_ton    = float(request.POST.get('lashing_belts_per_ton', 2))
        cfg.silica_gel_grams_per_cbm = float(request.POST.get('silica_gel_grams_per_cbm', 500))
        cfg.silica_gel_packet_grams  = float(request.POST.get('silica_gel_packet_grams', 50))
        cfg.nail_qty_per_sqm         = float(request.POST.get('nail_qty_per_sqm', 1))
        cfg.save()
        messages.success(request, 'Formula configuration saved!')
        return redirect('materials:formula_config')
    return render(request, 'materials/formula_config.html', {'cfg': cfg})