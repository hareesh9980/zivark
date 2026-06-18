import os
import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.conf import settings


# ── COLORS ───────────────────────────────────────────
RED        = 'C00000'
DARK_BLUE  = '1F3864'
LIGHT_BLUE = 'D9E1F2'
YELLOW     = 'FFD966'
GREEN      = 'E2EFDA'
ORANGE     = 'FCE4D6'
GRAY       = 'F2F2F2'
WHITE      = 'FFFFFF'


# ── STYLE HELPERS ────────────────────────────────────
def hfill(color):
    return PatternFill('solid', fgColor=color)

def hfont(bold=True, size=10, color='000000'):
    return Font(bold=bold, size=size, color=color, name='Calibri')

def halign(h='center', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def hborder():
    s = Side(style='thin', color='BFBFBF')
    return Border(left=s, right=s, top=s, bottom=s)

def mborder():
    s = Side(style='medium', color='000000')
    return Border(left=s, right=s, top=s, bottom=s)

def sc(ws, r, c, value=None, formula=None,
       fill=None, font=None, align=None,
       border=None, fmt=None):
    """Set cell helper"""
    cell = ws.cell(row=r, column=c)
    if formula:
        cell.value = formula
    elif value is not None:
        cell.value = value
    if fill:   cell.fill   = fill
    if font:   cell.font   = font
    if align:  cell.alignment = align
    if border: cell.border = border
    if fmt:    cell.number_format = fmt
    return cell


# ── MAIN FUNCTION ────────────────────────────────────
def generate_costing_excel(rfq, results, edited_data=None):
    """
    Generate Excel costing sheet exactly like KMT format.
    All cells connected with real Excel formulas.
    """
    wb = Workbook()
    wb.remove(wb.active)

    for idx, r in enumerate(results):
        sheet_name = f"Box {idx+1}"[:31]
        ws = wb.create_sheet(title=sheet_name)
        _build_sheet(
            ws, rfq, r['box'], r['design'],
            r['bom'], r['totals'],
            edited_data=edited_data
        )

    # Save
    output_dir = settings.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{rfq.rfq_number.replace('/', '-')}_costing.xlsx"
    filepath = os.path.join(output_dir, filename)
    wb.save(filepath)
    return filepath


def _build_sheet(ws, rfq, box, design, bom, totals,
                 edited_data=None):
    """Build one box sheet — KMT Excel style"""

    # ── COLUMN WIDTHS ────────────────────────────────
    widths = {
        'A': 7,   # SR
        'B': 24,  # Description
        'C': 20,  # Material
        'D': 12,  # L
        'E': 12,  # W
        'F': 12,  # H/T
        'G': 10,  # QTY NOS
        'H': 13,  # TOTAL QTY
        'I': 8,   # UOM
        'J': 12,  # RATE
        'K': 14,  # TOTAL
        'L': 3,   # spacer
        'M': 14,  # sidebar W
        'N': 10,  # sidebar H
    }
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # ── ROW 1: COMPANY NAME ──────────────────────────
    ws.merge_cells('A1:K1')
    sc(ws, 1, 1,
       value='PRONK MULTISERVICE INDIA PVT. LTD.',
       fill=hfill(RED),
       font=Font(bold=True, size=14, color=WHITE, name='Calibri'),
       align=halign('center', 'center'))
    ws.row_dimensions[1].height = 30

    # ── ROW 2: BRANCH / DATE ─────────────────────────
    ws.row_dimensions[2].height = 18
    sc(ws, 2, 1, value='BRANCH:',
       font=hfont(bold=True, size=10))
    sc(ws, 2, 2, value='Bengaluru',
       font=hfont(bold=False, size=10))
    sc(ws, 2, 8, value='Date:',
       font=hfont(bold=True, size=10))
    from datetime import date
    sc(ws, 2, 9, value=date.today().strftime('%d-%m-%Y'),
       font=hfont(bold=False, size=10))
    # Sidebar headers
    sc(ws, 2, 13, value='W',
       font=hfont(bold=True, size=10), align=halign())
    sc(ws, 2, 14, value='H',
       font=hfont(bold=True, size=10), align=halign())

    # ── ROW 3: CUSTOMER ──────────────────────────────
    ws.row_dimensions[3].height = 18
    sc(ws, 3, 1, value='CUSTOMER :',
       font=hfont(bold=True, size=10))
    client = rfq.client.company_name if rfq.client else ''
    sc(ws, 3, 2, value=client,
       font=hfont(bold=False, size=10))
    # Sidebar: Pallet Deck
    sc(ws, 3, 12, value='Pallet Deck',
       font=hfont(bold=True, size=9), align=halign('right'))
    deck_w_display = design.get('deck_w', 150)
    if design.get('deck_uom') == 'SQM':
      deck_w_display = design.get('box_od_w', 0)
    sc(ws, 3, 13, value=deck_w_display,
       font=hfont(bold=False, size=10), align=halign())
    sc(ws, 3, 14, value=design.get('deck_h', 50),
       font=hfont(bold=False, size=10), align=halign())

    # ── ROW 4: PRODUCT + BOX ID ──────────────────────
    # KEY: E4=ID_L, F4=ID_W, G4=ID_H
    ws.row_dimensions[4].height = 20
    sc(ws, 4, 1, value='PRODUCT NAME:',
       font=hfont(bold=True, size=10))
    sc(ws, 4, 2, value=box.product_name,
       font=hfont(bold=False, size=10))
    sc(ws, 4, 4, value='BOX ID',
       fill=hfill(DARK_BLUE),
       font=Font(bold=True, size=10, color=WHITE, name='Calibri'),
       align=halign())
    # E4=ID_L, F4=ID_W, G4=ID_H ← KEY REFERENCE CELLS
    sc(ws, 4, 5, value=box.box_id_length,
       font=hfont(bold=True, size=10), align=halign(),
       fill=hfill(LIGHT_BLUE))
    sc(ws, 4, 6, value=box.box_id_width,
       font=hfont(bold=True, size=10), align=halign(),
       fill=hfill(LIGHT_BLUE))
    sc(ws, 4, 7, value=box.box_id_height,
       font=hfont(bold=True, size=10), align=halign(),
       fill=hfill(LIGHT_BLUE))
    sc(ws, 4, 8, value='Volume(CBM)',
       font=hfont(bold=True, size=9), align=halign('right'))
    sc(ws, 4, 10, value=design['volumes']['cbm'],
       font=hfont(bold=True, size=10), align=halign(),
       fmt='0.00')
    # Sidebar: Pallet w Runner
    sc(ws, 4, 12, value='Pallet w Runner',
       font=hfont(bold=True, size=9), align=halign('right'))
    sc(ws, 4, 13, value=design.get('runner_w', 75),
       font=hfont(bold=False, size=10), align=halign())
    sc(ws, 4, 14, value=design.get('runner_h', 100),
       font=hfont(bold=False, size=10), align=halign())

    # ── ROW 5: BOX OD ────────────────────────────────
    # KEY: E5=OD_L, F5=OD_W, G5=OD_H ← BOM uses these!
    ws.row_dimensions[5].height = 20
    sc(ws, 5, 4, value='BOX OD',
       fill=hfill(RED),
       font=Font(bold=True, size=10, color=WHITE, name='Calibri'),
       align=halign())
    # E5=OD_L, F5=OD_W, G5=OD_H
    sc(ws, 5, 5, value=design['box_od_l'],
       font=Font(bold=True, size=10, color='C00000', name='Calibri'),
       align=halign(), fill=hfill(YELLOW))
    sc(ws, 5, 6, value=design['box_od_w'],
       font=Font(bold=True, size=10, color='C00000', name='Calibri'),
       align=halign(), fill=hfill(YELLOW))
    sc(ws, 5, 7, value=design['box_od_h'],
       font=Font(bold=True, size=10, color='C00000', name='Calibri'),
       align=halign(), fill=hfill(YELLOW))
    sc(ws, 5, 8, value='Total Area(SQM)',
       font=hfont(bold=True, size=9), align=halign('right'))
    sc(ws, 5, 10, value=design['volumes']['total_area_sqm'],
       font=hfont(bold=True, size=10), align=halign(),
       fmt='0.00')
    # Sidebar: Walls
    sc(ws, 5, 12, value='Walls',
       font=hfont(bold=True, size=9), align=halign('right'))
    sc(ws, 5, 13, value=design.get('wall_t', 8),
       font=hfont(bold=False, size=10), align=halign())

    # ── ROW 6: PALLET OD ─────────────────────────────
    ws.row_dimensions[6].height = 18
    sc(ws, 6, 4, value='PALLET OD',
       fill=hfill(DARK_BLUE),
       font=Font(bold=True, size=10, color=WHITE, name='Calibri'),
       align=halign())
    sc(ws, 6, 5, value=design['box_od_l'],
       font=hfont(bold=False, size=10), align=halign())
    sc(ws, 6, 6, value=design['box_od_w'],
       font=hfont(bold=False, size=10), align=halign())
    pallet_h = design.get('deck_h', 50) + design.get('runner_h', 100)
    sc(ws, 6, 7, value=pallet_h,
       font=hfont(bold=False, size=10), align=halign())
    sc(ws, 6, 8, value='Base Area(SQM)',
       font=hfont(bold=True, size=9), align=halign('right'))
    sc(ws, 6, 10, value=design['volumes']['base_area_sqm'],
       font=hfont(bold=True, size=10), align=halign(),
       fmt='0.00')
    # Sidebar: Beading
    sc(ws, 6, 12, value='Beading',
       font=hfont(bold=True, size=9), align=halign('right'))
    sc(ws, 6, 13, value=design.get('beading_w', 75),
       font=hfont(bold=False, size=10), align=halign())
    sc(ws, 6, 14, value=design.get('beading_h', 50),
       font=hfont(bold=False, size=10), align=halign())

    # ── ROW 7: QUANTITY / WEIGHT ─────────────────────
    ws.row_dimensions[7].height = 18
    sc(ws, 7, 6, value='Quantity',
       font=hfont(bold=True, size=10))
    sc(ws, 7, 7, value=box.quantity,
       font=hfont(bold=False, size=10), align=halign())
    sc(ws, 7, 8, value='Weight',
       font=hfont(bold=True, size=10))
    sc(ws, 7, 9, value=f"{box.weight_kg} Kgs",
       font=hfont(bold=False, size=10))

    # ── ROW 8 ────────────────────────────────────────
    ws.row_dimensions[8].height = 18
    sc(ws, 8, 1, value='DRAWING AVL(Y/N):',
       font=hfont(bold=True, size=9))
    sc(ws, 8, 2, value='N', font=hfont(bold=False, size=10))

    # ── ROW 9: COSTING BY ────────────────────────────
    ws.row_dimensions[9].height = 18
    sc(ws, 9, 1, value='COSTING BY:',
       font=hfont(bold=True, size=9))
    eng = (rfq.engineer.full_name or rfq.engineer.username
           if rfq.engineer else '')
    sc(ws, 9, 2, value=eng, font=hfont(bold=False, size=10))

    # ── ROW 10: APPROVED BY ──────────────────────────
    ws.row_dimensions[10].height = 18
    sc(ws, 10, 1, value='APPROVED BY:',
       font=hfont(bold=True, size=9))

    # ── ROW 11: BOM COLUMN HEADERS ───────────────────
    ws.row_dimensions[11].height = 30
    ws.merge_cells('D11:F11')
    headers = [
        (1, 'SR. NO.'), (2, 'DESCRIPTION'),
        (3, 'MATERIAL'), (4, 'DIMENSIONS in mm'),
        (7, 'QTY IN\nNOS.'), (8, 'TOTAL QTY'),
        (9, 'UOM'), (10, 'RATE/UOM'), (11, 'TOTAL'),
    ]
    for col_num, text in headers:
        sc(ws, 11, col_num,
           value=text,
           fill=hfill(RED),
           font=Font(bold=True, size=9, color=WHITE, name='Calibri'),
           align=halign('center', 'center', wrap=True),
           border=hborder())

    # ── ROW 12: L/W/H SUBHEADERS ─────────────────────
    ws.row_dimensions[12].height = 16
    for col_num, text in [(4, 'L'), (5, 'W'), (6, 'H/T')]:
        sc(ws, 12, col_num,
           value=text,
           fill=hfill(RED),
           font=Font(bold=True, size=9, color=WHITE, name='Calibri'),
           align=halign(),
           border=hborder())

    # ── ROW 13: WOODEN BOX LABEL ─────────────────────
    ws.row_dimensions[13].height = 16
    ws.merge_cells('A13:K13')
    sc(ws, 13, 1,
       value='Wooden Box',
       fill=hfill(DARK_BLUE),
       font=Font(bold=True, size=10, color=WHITE, name='Calibri'),
       align=halign())

    # ── BOM ROWS (start row 14) ──────────────────────
    BOM_START = 14

    # KEY CELL REFERENCES
    OD_L = 'E5'   # OD_L
    OD_W = 'F5'   # OD_W
    OD_H = 'G5'   # OD_H
    ID_H = 'G4'   # ID_H
    CBM  = 'J4'   # CBM

    # L column formula map
    L_MAP = {
       'Deck': f'={OD_W}' if design['box_od_l'] > 2500 else f'={OD_L}',
        'Length Runner':    f'={OD_L}',
        'Length Wall':      f'={OD_L}',
        'Length Beading-L': f'={OD_L}',
        'Length Beading-H': f'={ID_H}',
        'Width Runner':     f'={OD_W}',
        'Width Wall':       f'={OD_W}',
        'Width Beading-W':  f'={OD_W}',
        'Width Beading-H':  f'={ID_H}',
        'Top Wall':         f'={OD_L}',
        'Top Beading-L':    f'={OD_L}',
        'Top Beading-W':    f'={OD_W}',
        'Top Chocking':     f'={OD_W}',
        'Bottom Chocking':  f'={OD_L}',
    }

    # Get rule for pitches
    rule = design.get('rule')

    for i, item in enumerate(bom):
        r = BOM_START + i
        ws.row_dimensions[r].height = 16
        desc = item['description']
        uom  = item['uom'].upper()

        # Use edited values if available
        if edited_data and i < len(edited_data):
            ed       = edited_data[i]
            qty_nos  = ed[6] if ed[6] else item['qty_nos']
            rate     = ed[9] if ed[9] else item['rate_per_uom']
            l_val    = ed[3] if ed[3] else item['length_mm']
            w_val    = ed[4] if ed[4] else item['width_mm']
            h_val    = ed[5] if ed[5] else item['thickness_mm']
        else:
            qty_nos  = item['qty_nos']
            rate     = item['rate_per_uom']
            l_val    = item['length_mm']
            w_val    = item['width_mm']
            h_val    = item['thickness_mm']

        # ── SR ───────────────────────────────────────
        sc(ws, r, 1, value=item['sr_no'],
           align=halign(), border=hborder(),
           font=hfont(bold=False, size=9))

        # ── DESCRIPTION ──────────────────────────────
        sc(ws, r, 2, value=desc,
           align=Alignment(horizontal='left', vertical='center'),
           border=hborder(), font=hfont(bold=False, size=9))

        # ── MATERIAL ─────────────────────────────────
        sc(ws, r, 3, value=item['material'],
           align=Alignment(horizontal='left', vertical='center'),
           border=hborder(), font=hfont(bold=False, size=9))

        # ── L COLUMN (=E5 connected formula!) ────────
        l_formula = None
        for key, formula in L_MAP.items():
            if key in desc:
                l_formula = formula
                break

        if l_formula:
            sc(ws, r, 4, formula=l_formula,
               align=halign(), border=hborder(),
               fill=hfill(GREEN),
               font=hfont(bold=False, size=9),
               fmt='0')
        elif l_val:
            sc(ws, r, 4, value=l_val,
               align=halign(), border=hborder(),
               font=hfont(bold=False, size=9),
               fmt='0')
        else:
            sc(ws, r, 4, value='',
               border=hborder())

        # ── W COLUMN ─────────────────────────────────
        sc(ws, r, 5, value=w_val if w_val else '',
           align=halign(), border=hborder(),
           font=hfont(bold=False, size=9), fmt='0')

        # ── H/T COLUMN ───────────────────────────────
        sc(ws, r, 6, value=h_val if h_val else '',
           align=halign(), border=hborder(),
           font=hfont(bold=False, size=9), fmt='0')

        # ── QTY NOS (ROUNDUP formula!) ───────────────
        qty_formula = _get_qty_formula(
            desc, rule, OD_L, OD_W, OD_H, ID_H, CBM)

        if qty_formula:
            sc(ws, r, 7, formula=qty_formula,
               align=halign(), border=hborder(),
               fill=hfill(GREEN),
               font=hfont(bold=False, size=9), fmt='0')
        else:
            sc(ws, r, 7, value=qty_nos,
               align=halign(), border=hborder(),
               font=hfont(bold=False, size=9), fmt='0.00')

        # ── TOTAL QTY (CFT/SQM formula!) ─────────────
        if uom == 'CFT' and l_val:
            tq_formula = (
                f'=((D{r}/1000)*(E{r}/1000)*(F{r}/1000))'
                f'*G{r}*(3.28^3)*1.05'
            )
            sc(ws, r, 8, formula=tq_formula,
               align=halign('right'), border=hborder(),
               fill=hfill(GREEN),
               font=hfont(bold=False, size=9), fmt='0.00')
        elif uom == 'SQM' and l_val:
            tq_formula = (
                f'=(D{r}/1000)*(E{r}/1000)'
                f'*G{r}*1.05'
            )
            sc(ws, r, 8, formula=tq_formula,
               align=halign('right'), border=hborder(),
               fill=hfill(GREEN),
               font=hfont(bold=False, size=9), fmt='0.00')
        else:
            sc(ws, r, 8,
               value=item['total_qty'],
               align=halign('right'), border=hborder(),
               font=hfont(bold=False, size=9), fmt='0.00')

        # ── UOM ──────────────────────────────────────
        sc(ws, r, 9, value=uom,
           align=halign(), border=hborder(),
           font=hfont(bold=False, size=9))

        # ── RATE ─────────────────────────────────────
        sc(ws, r, 10, value=rate,
           align=halign('right'), border=hborder(),
           font=hfont(bold=False, size=9), fmt='#,##0')

        # ── TOTAL (=H*J formula!) ────────────────────
        # Lashing, Silica, Tarpaulin: G*H*J
        if (uom == 'MTR' or
            'Silica' in desc or 'Tarpaulin' in desc):
            total_formula = f'=G{r}*H{r}*J{r}'
        else:
            total_formula = f'=H{r}*J{r}'

        sc(ws, r, 11, formula=total_formula,
           align=halign('right'), border=hborder(),
           fill=hfill(GREEN),
           font=Font(bold=True, size=9,
                     color='1B5E20', name='Calibri'),
           fmt='#,##0')

    # ── TOTALS SECTION ───────────────────────────────
    last_row  = BOM_START + len(bom) - 1
    tot_row   = last_row + 2
    K_range   = f'K{BOM_START}:K{last_row}'

    ws.row_dimensions[tot_row].height = 20

    def tot_row_add(label, formula, bg, r):
        ws.merge_cells(f'A{r}:J{r}')
        sc(ws, r, 1, value=label,
           fill=hfill(bg),
           font=Font(bold=True, size=10,
                     color=WHITE if bg in [RED, DARK_BLUE]
                     else '000000', name='Calibri'),
           align=halign('right'))
        sc(ws, r, 11, formula=formula,
           fill=hfill(bg),
           font=Font(bold=True, size=10,
                     color=WHITE if bg in [RED, DARK_BLUE]
                     else '000000', name='Calibri'),
           align=halign('right'), fmt='#,##0')
        ws.row_dimensions[r].height = 20

    r = tot_row
    tot_row_add('TOTAL COST',
                f'=SUM({K_range})', DARK_BLUE, r)
    r += 1
    tot_row_add(
        f'Overhead @ {totals["overhead_pct"]}%',
        f'=K{r-1}*{totals["overhead_pct"]}/100',
        ORANGE, r)
    r += 1
    tot_row_add('After Overhead',
                f'=K{r-2}+K{r-1}', GRAY, r)
    r += 1
    tot_row_add(
        f'Margin @ {totals["margin_pct"]}%',
        f'=K{r-1}*{totals["margin_pct"]}/100',
        ORANGE, r)
    r += 1
    tot_row_add('Before GST (CEILING to 100)',
                f'=CEILING(K{r-2}+K{r-1},100)',
                GRAY, r)
    r += 1
    tot_row_add(
        f'GST @ {totals["gst_pct"]}%',
        f'=K{r-1}*{totals["gst_pct"]}/100',
        ORANGE, r)
    r += 1
    tot_row_add('GRAND TOTAL',
                f'=K{r-2}+K{r-1}', RED, r)

    # ── FREEZE + PRINT ───────────────────────────────
    ws.freeze_panes = 'A14'
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToPage   = True
    ws.page_setup.fitToWidth  = 1


def _get_qty_formula(desc, rule,
                     OD_L, OD_W, OD_H, ID_H, CBM):
    """Return ROUNDUP formula for QTY NOS column"""
    def p(attr, default):
        return getattr(rule, attr) if rule else default

    if 'Deck' in desc:
        return f'=ROUNDUP({OD_L}/{p("deck_pitch",140)},0)'
    elif 'Length Runner' in desc:
        return f'=ROUNDUP({OD_W}/{p("l_runner_pitch",500)},0)'
    elif 'Width Runner' in desc:
        return f'=ROUNDUP({OD_L}/{p("w_runner_pitch",600)},0)'
    elif 'Length Beading-L' in desc:
        return f'=ROUNDUP({ID_H}/{p("lb_l_pitch",700)},0)*2'
    elif 'Length Beading-H' in desc:
        return f'=ROUNDUP({OD_L}/{p("lb_h_pitch",900)},0)*2'
    elif 'Width Beading-W' in desc:
        return f'=ROUNDUP({ID_H}/{p("wb_w_pitch",700)},0)*2'
    elif 'Width Beading-H' in desc:
        return f'=ROUNDUP({OD_W}/{p("wb_h_pitch",500)},0)*2'
    elif 'Top Beading-L' in desc:
        return f'=ROUNDUP({OD_W}/{p("top_bl_pitch",600)},0)*2'
    elif 'Top Beading-W' in desc:
        return f'=ROUNDUP({OD_L}/{p("top_bw_pitch",700)},0)*2'
    elif 'Top Chocking' in desc:
        return f'=ROUNDUP({OD_L}/{p("top_chock_pitch",500)},0)'
    elif 'Bottom Chocking' in desc:
        return f'=ROUNDUP({OD_W}/{p("bot_chock_pitch",500)},0)'
    elif 'Lashing' in desc:
        return f'=ROUNDUP({OD_L}/{p("lashing_pitch",600)},0)'
    elif 'Silica' in desc:
        return f'=ROUNDUP({CBM}*500/50,0)'
    elif 'N/B' in desc or 'Nut' in desc:
        return (f'=ROUNDUP(({OD_L}/250)*4+'
                f'({OD_W}/250)*4+'
                f'({OD_H}/250)*4,0)')
    return None