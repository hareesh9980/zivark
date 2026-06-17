import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from engine.design_engine import run_design
from engine.costing_engine import run_costing

# Test with sample dimensions
design = run_design(
    id_l=3940,
    id_w=1250,
    id_h=2250,
    weight_kg=3000,
)

print('OD:', design['box_od_l'], 'x',
      design['box_od_w'], 'x', design['box_od_h'])
print('CBM:', design['volumes']['cbm'])
print('Rule:', design['rule'])

result = run_costing(design)
print('\nBOM Items:', len(result['bom']))
for item in result['bom']:
    print(f"  {item['sr_no']}. {item['description']}"
          f" → {item['total_qty']} {item['uom']}"
          f" @ ₹{item['rate_per_uom']}"
          f" = ₹{item['total_cost']}")

print('\nTotals:')
for k, v in result['totals'].items():
    print(f"  {k}: {v}")