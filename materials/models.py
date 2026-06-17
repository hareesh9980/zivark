from django.db import models

class Material(models.Model):

    CATEGORY_CHOICES = [
        ('solid_wood', 'Solid Wood'),
        ('plywood',    'Plywood / Sheet'),
        ('hardware',   'Hardware'),
        ('consumable', 'Consumable'),
        ('steel',      'Steel'),
        ('other',      'Other'),
    ]

    UOM_CHOICES = [
        ('CFT', 'CFT - Cubic Feet'),
        ('SQM', 'SQM - Square Meter'),
        ('KG',  'KG - Kilogram'),
        ('NOS', 'NOS - Numbers'),
        ('MTR', 'MTR - Meter'),
        ('SQF', 'SQF - Square Feet'),
    ]

    GRADE_CHOICES = [
        ('AD',  'AD - Air Dried'),
        ('KD',  'KD - Kiln Dried'),
        ('BWR', 'BWR - Boiling Water Resistant'),
        ('BWP', 'BWP - Marine Grade'),
        ('COM', 'Commercial Grade'),
        ('NA',  'Not Applicable'),
    ]

    # Basic info
    name        = models.CharField(max_length=200)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Wood specific
    wood_type   = models.CharField(max_length=100, blank=True,
                    help_text='e.g. Pinewood, Rubber Wood, Sal, Teak, Eucalyptus')
    wood_grade  = models.CharField(max_length=10, choices=GRADE_CHOICES,
                    default='NA')

    # Dimensions (for solid wood and plywood)
    width_mm     = models.FloatField(default=0,
                    help_text='Width in mm (for solid wood: actual width)')
    height_mm    = models.FloatField(default=0,
                    help_text='Height in mm (for solid wood: actual height)')
    thickness_mm = models.FloatField(default=0,
                    help_text='Thickness in mm (for plywood/sheet only)')

    # Pricing
    uom  = models.CharField(max_length=10, choices=UOM_CHOICES, default='CFT')
    rate = models.FloatField(default=0)

    # Status
    is_active  = models.BooleanField(default=True)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.uom}) @ ₹{self.rate}"

    @property
    def formula_type(self):
        if self.category == 'solid_wood':
            return 'CFT'
        elif self.category == 'plywood':
            return 'SQM'
        elif self.category == 'steel':
            return 'KG'
        else:
            return 'DIRECT'

    @property
    def display_size(self):
        if self.category == 'solid_wood':
            return f"{self.width_mm}×{self.height_mm}mm"
        elif self.category == 'plywood':
            return f"{self.thickness_mm}mm"
        return ''

    class Meta:
        ordering = ['category', 'name']


class WeightRule(models.Model):
    name        = models.CharField(max_length=200)
    weight_from = models.FloatField()
    weight_to   = models.FloatField()
    is_active   = models.BooleanField(default=True)

    # Materials — FK to Material
    deck_material     = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='deck_rules')
    runner_material   = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='runner_rules')
    l_runner_material = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='l_runner_rules')
    beading_material  = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='beading_rules')
    wall_material     = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='wall_rules')
    top_material      = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='top_rules')
    chock_material    = models.ForeignKey(Material, on_delete=models.SET_NULL,
                         null=True, blank=True, related_name='chock_rules')

    # Dimensions
    deck_w    = models.FloatField(default=150)
    deck_h    = models.FloatField(default=50)
    runner_w  = models.FloatField(default=75)
    runner_h  = models.FloatField(default=100)
    l_runner_w= models.FloatField(default=100)
    l_runner_h= models.FloatField(default=100)
    beading_w = models.FloatField(default=75)
    beading_h = models.FloatField(default=50)
    wall_t    = models.FloatField(default=8)
    use_l_runner = models.BooleanField(default=False)

    # Pitches
    deck_pitch      = models.FloatField(default=140)
    l_runner_pitch  = models.FloatField(default=500)
    w_runner_pitch  = models.FloatField(default=600)
    lb_l_pitch      = models.FloatField(default=700)
    lb_h_pitch      = models.FloatField(default=900)
    wb_w_pitch      = models.FloatField(default=700)
    wb_h_pitch      = models.FloatField(default=500)
    top_bl_pitch    = models.FloatField(default=600)
    top_bw_pitch    = models.FloatField(default=700)
    top_chock_pitch = models.FloatField(default=500)
    bot_chock_pitch = models.FloatField(default=500)
    lashing_pitch   = models.FloatField(default=600)

    # Formula config
    overhead_pct = models.FloatField(default=7.0)
    margin_pct   = models.FloatField(default=25.0)
    gst_pct      = models.FloatField(default=12.0)
    wastage_pct  = models.FloatField(default=5.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.weight_from}-{self.weight_to}kg)"

    class Meta:
        ordering = ['weight_from']


class HardwareConfig(models.Model):
    """
    Links hardware/consumable materials to
    auto-calculation formulas
    """
    CALC_CHOICES = [
        ('per_sqm_base',  'Per SQM Base Area'),
        ('per_sqm_total', 'Per SQM Total Area'),
        ('per_cbm',       'Per CBM × factor'),
        ('per_ton',       'Per Ton weight'),
        ('per_runner_qty','Runner qty × W_runner qty'),
        ('per_od_l',      'ROUNDUP(OD_L / pitch)'),
        ('manual',        'Manual entry only'),
    ]

    material       = models.OneToOneField(Material,
                      on_delete=models.CASCADE,
                      related_name='hardware_config')
    calc_method    = models.CharField(max_length=30,
                      choices=CALC_CHOICES, default='manual')
    calc_factor    = models.FloatField(default=1.0,
                      help_text='Multiplier for calculation')
    calc_pitch     = models.FloatField(default=0,
                      help_text='Pitch for OD_L based calc')
    include_by_default = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.material.name} → {self.calc_method}"