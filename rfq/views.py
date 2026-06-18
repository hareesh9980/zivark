from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
import json
from django.http import FileResponse

from .models import RFQ, BoxDesign, Quotation
from clients.models import Client
from engine.design_engine import run_design
from engine.costing_engine import run_costing


# ── HELPERS ──────────────────────────────────────────

def generate_rfq_number():
    from datetime import datetime
    now   = datetime.now()
    count = RFQ.objects.count() + 1
    return f"RFQ-{now.strftime('%Y%m')}-{count:04d}"


def generate_quotation_number():
    from datetime import datetime
    now   = datetime.now()
    count = Quotation.objects.count() + 1
    return f"QTN-{now.strftime('%Y%m')}-{count:04d}"


def get_override(post, field):
    val = post.get(field, '').strip()
    if val:
        try:
            return float(val)
        except:
            return None
    return None


# ── RFQ LIST ─────────────────────────────────────────

@login_required
def rfq_list(request):
    rfqs = RFQ.objects.all().select_related('client', 'engineer')
    return render(request, 'rfq/list.html', {'rfqs': rfqs})


# ── RFQ NEW ──────────────────────────────────────────

@login_required
def rfq_new(request):
    clients = Client.objects.all().order_by('company_name')
    if request.method == 'POST':
        rfq = RFQ.objects.create(
            rfq_number     = generate_rfq_number(),
            client_id      = request.POST.get('client') or None,
            engineer       = request.user,
            status         = 'in_progress',
            engineer_notes = request.POST.get('notes', ''),
        )
        box_count = int(request.POST.get('box_count', 1))
        for i in range(1, box_count + 1):
            BoxDesign.objects.create(
                rfq           = rfq,
                product_name  = request.POST.get(
                    f'product_name_{i}', f'Box {i}'),
                quantity      = int(request.POST.get(
                    f'quantity_{i}', 1)),
                box_id_length = float(request.POST.get(
                    f'length_{i}', 0)),
                box_id_width  = float(request.POST.get(
                    f'width_{i}', 0)),
                box_id_height = float(request.POST.get(
                    f'height_{i}', 0)),
                weight_kg     = float(request.POST.get(
                    f'weight_{i}', 0)),
                access_type   = request.POST.get(
                    f'access_type_{i}', '2_access'),
                shipment_type = request.POST.get(
                    f'shipment_type_{i}', 'export'),
                packing_type  = request.POST.get(
                    f'packing_type_{i}', 'box'),
                pallet_deck_type = request.POST.get(
                    f'pallet_deck_type_{i}', 'auto'),
                override_beading_w  = get_override(
                    request.POST, f'beading_w_{i}'),
                override_beading_h  = get_override(
                    request.POST, f'beading_h_{i}'),
                override_wall_t     = get_override(
                    request.POST, f'wall_t_{i}'),
                override_deck_w     = get_override(
                    request.POST, f'deck_w_{i}'),
                override_deck_h     = get_override(
                    request.POST, f'deck_h_{i}'),
                override_runner_w   = get_override(
                    request.POST, f'runner_w_{i}'),
                override_runner_h   = get_override(
                    request.POST, f'runner_h_{i}'),
                override_l_runner_w = get_override(
                    request.POST, f'l_runner_w_{i}'),
                override_l_runner_h = get_override(
                    request.POST, f'l_runner_h_{i}'),
            )
        messages.success(request, f'RFQ {rfq.rfq_number} created!')
        return redirect('rfq:generate', pk=rfq.pk)
    return render(request, 'rfq/new.html', {'clients': clients})


# ── RFQ DETAIL ───────────────────────────────────────

@login_required
def rfq_detail(request, pk):
    rfq   = get_object_or_404(RFQ, pk=pk)
    boxes = rfq.boxes.all()
    return render(request, 'rfq/detail.html', {
        'rfq':   rfq,
        'boxes': boxes,
    })


# ── RFQ GENERATE ─────────────────────────────────────

@login_required
def rfq_generate(request, pk):
    rfq     = get_object_or_404(RFQ, pk=pk)
    boxes   = rfq.boxes.all()
    results = []

    for box in boxes:
        packing_type = getattr(box, 'packing_type', 'box') or 'box'

        # ── SELECT ENGINE ────────────────────────────
        if packing_type == 'pallet':
            from engine.pallet_engine import run_pallet_design
            design = run_pallet_design(
                id_l             = box.box_id_length,
                id_w             = box.box_id_width,
                id_h             = box.box_id_height,
                weight_kg        = box.weight_kg,
                shipment_type    = box.shipment_type,
                pallet_deck_type = getattr(
                    box, 'pallet_deck_type', 'auto') or 'auto',
                deck_w           = box.override_deck_w,
                deck_h           = box.override_deck_h,
                runner_w         = box.override_runner_w,
                runner_h         = box.override_runner_h,
                l_runner_w       = box.override_l_runner_w,
                l_runner_h       = box.override_l_runner_h,
                product_name     = box.product_name,
            )
        else:
            # Box or Box+Pallet → use box design engine
            design = run_design(
                id_l                = box.box_id_length,
                id_w                = box.box_id_width,
                id_h                = box.box_id_height,
                weight_kg           = box.weight_kg,
                access_type         = box.access_type,
                shipment_type       = box.shipment_type,
                product_name        = box.product_name,
                override_beading_w  = box.override_beading_w,
                override_beading_h  = box.override_beading_h,
                override_wall_t     = box.override_wall_t,
                override_deck_w     = box.override_deck_w,
                override_deck_h     = box.override_deck_h,
                override_runner_w   = box.override_runner_w,
                override_runner_h   = box.override_runner_h,
                override_l_runner_w = box.override_l_runner_w,
                override_l_runner_h = box.override_l_runner_h,
            )

        # ── SAVE OD TO DB ────────────────────────────
        box.box_od_length  = design['box_od_l']
        box.box_od_width   = design['box_od_w']
        box.box_od_height  = design['box_od_h']
        box.volume_cbm     = design['volumes']['cbm']
        box.total_area_sqm = design['volumes']['total_area_sqm']
        box.base_area_sqm  = design['volumes']['base_area_sqm']
        box.save()

        # ── LOAD EDITED BOM IF EXISTS ─────────────────
        if box.edited_bom:
            try:
                edited_rows   = json.loads(box.edited_bom)
                edited_totals = json.loads(box.edited_totals)
                bom = []
                for i, r in enumerate(edited_rows):
                    bom.append({
                        'sr_no':        i + 1,
                        'description':  r[1] or '',
                        'material':     r[2] or '',
                        'length_mm':    r[3] or 0,
                        'width_mm':     r[4] or 0,
                        'thickness_mm': r[5] or 0,
                        'qty_nos':      r[6] or 0,
                        'total_qty':    r[7] or 0,
                        'uom':          r[8] or '',
                        'rate_per_uom': r[9] or 0,
                        'total_cost':   r[10] or 0,
                    })
                totals = edited_totals
            except:
                result = run_costing(design)
                bom    = result['bom']
                totals = result['totals']
        else:
            result = run_costing(design)
            bom    = result['bom']
            totals = result['totals']

        box.unit_cost = totals.get('grand_total', 0)
        box.save(update_fields=['unit_cost'])

        results.append({
            'box':    box,
            'design': design,
            'bom':    bom,
            'totals': totals,
        })

    grand_total = sum(
        r['totals'].get('grand_total', 0) * r['box'].quantity
        for r in results
    )

    quotation, created = Quotation.objects.get_or_create(
        rfq=rfq,
        defaults={
            'quotation_number': generate_quotation_number(),
            'grand_total':      grand_total,
            'status':           'draft',
        }
    )
    if not created:
        quotation.grand_total = grand_total
        quotation.save()

    rfq.status = 'design_review'
    rfq.save()

    return render(request, 'rfq/generate.html', {
        'rfq':         rfq,
        'quotation':   quotation,
        'results':     results,
        'grand_total': grand_total,
    })


# ── RFQ STATUS UPDATE ────────────────────────────────

@login_required
def rfq_status(request, pk):
    if request.method == 'POST':
        rfq    = get_object_or_404(RFQ, pk=pk)
        status = request.POST.get('status')
        if status in ['sent', 'won', 'lost', 'in_progress']:
            rfq.status = status
            rfq.save()
            try:
                q        = rfq.quotation
                q.status = status
                q.save()
            except:
                pass
            messages.success(
                request,
                f'Status updated to {status.upper()}!'
            )
    return redirect('rfq:detail', pk=pk)


# ── EXCEL DOWNLOAD ───────────────────────────────────

@login_required
def rfq_excel(request, pk):
    rfq     = get_object_or_404(RFQ, pk=pk)
    boxes   = rfq.boxes.all()
    results = []

    for box in boxes:
        packing_type = getattr(box, 'packing_type', 'box') or 'box'

        if packing_type == 'pallet':
            from engine.pallet_engine import run_pallet_design
            design = run_pallet_design(
                id_l             = box.box_id_length,
                id_w             = box.box_id_width,
                id_h             = box.box_id_height,
                weight_kg        = box.weight_kg,
                shipment_type    = box.shipment_type,
                pallet_deck_type = getattr(
                    box, 'pallet_deck_type', 'auto') or 'auto',
                product_name     = box.product_name,
            )
        else:
            design = run_design(
                id_l          = box.box_id_length,
                id_w          = box.box_id_width,
                id_h          = box.box_id_height,
                weight_kg     = box.weight_kg,
                access_type   = box.access_type,
                shipment_type = box.shipment_type,
                product_name  = box.product_name,
            )

        result = run_costing(design)
        results.append({
            'box':    box,
            'design': design,
            'bom':    result['bom'],
            'totals': result['totals'],
        })

    edited_data = None
    if request.method == 'POST':
        try:
            edited_data = json.loads(
                request.POST.get('edited_bom', '[]'))
        except:
            edited_data = None

    # Use correct generator based on packing type
    first_box = boxes.first()
    packing_type = getattr(
        first_box, 'packing_type', 'box') or 'box'

    if packing_type == 'pallet':
        from documents.pallet_excel_generator import (
            generate_pallet_excel)
        filepath = generate_pallet_excel(
            rfq, results, edited_data)
    else:
        from documents.excel_generator import (
            generate_costing_excel)
        filepath = generate_costing_excel(
            rfq, results, edited_data)

    filename = os.path.basename(filepath)
    response = FileResponse(
        open(filepath, 'rb'),
        content_type=(
            'application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.sheet'
        )
    )
    response['Content-Disposition'] = (
        f'attachment; filename="{filename}"'
    )
    return response