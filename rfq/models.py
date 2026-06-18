from django.db import models
from django.conf import settings


class RFQ(models.Model):
    STATUS_CHOICES = [
        ('draft',         'Draft'),
        ('in_progress',   'In Progress'),
        ('design_review', 'Design Review'),
        ('sent',          'Sent to Customer'),
        ('won',           'Won'),
        ('lost',          'Lost'),
    ]

    rfq_number     = models.CharField(max_length=50, unique=True)
    client         = models.ForeignKey(
                       'clients.Client',
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='rfqs'
                     )
    engineer       = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='rfqs'
                     )
    status         = models.CharField(
                       max_length=20,
                       choices=STATUS_CHOICES,
                       default='draft'
                     )
    engineer_notes = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rfq_number

    class Meta:
        ordering = ['-created_at']


class BoxDesign(models.Model):
    ACCESS_CHOICES = [
        ('2_access', '2 Access (Runners)'),
        ('4_access', '4 Access (Blocks)'),
    ]
    SHIPMENT_CHOICES = [
        ('domestic', 'Domestic'),
        ('export',   'Export / International'),
    ]
    
    PACKING_TYPE_CHOICES = [
    ('box',       'Wooden Box'),
    ('pallet',    'Pallet Only'),
    ('box_pallet','Box + Pallet'),
]

    packing_type     = models.CharField(
    max_length=20,
    choices=PACKING_TYPE_CHOICES,
    default='box'
    ) 
    pallet_deck_type = models.CharField(
    max_length=20,
    default='auto'
)

    rfq          = models.ForeignKey(
                     RFQ,
                     on_delete=models.CASCADE,
                     related_name='boxes'
                   )
    product_name = models.CharField(max_length=200)
    quantity     = models.PositiveIntegerField(default=1)

    # Inside Dimensions
    box_id_length = models.FloatField()
    box_id_width  = models.FloatField()
    box_id_height = models.FloatField()

    # Outside Dimensions (calculated)
    box_od_length = models.FloatField(default=0)
    box_od_width  = models.FloatField(default=0)
    box_od_height = models.FloatField(default=0)

    # Machine info
    weight_kg     = models.FloatField()
    access_type   = models.CharField(
                      max_length=20,
                      choices=ACCESS_CHOICES,
                      default='2_access'
                    )
    shipment_type = models.CharField(
                      max_length=20,
                      choices=SHIPMENT_CHOICES,
                      default='export'
                    )

    # Volumes
    volume_cbm     = models.FloatField(default=0)
    total_area_sqm = models.FloatField(default=0)
    base_area_sqm  = models.FloatField(default=0)

    # Manual overrides (all optional)
    override_deck_w     = models.FloatField(null=True, blank=True)
    override_deck_h     = models.FloatField(null=True, blank=True)
    override_runner_w   = models.FloatField(null=True, blank=True)
    override_runner_h   = models.FloatField(null=True, blank=True)
    override_l_runner_w = models.FloatField(null=True, blank=True)
    override_l_runner_h = models.FloatField(null=True, blank=True)
    override_beading_w  = models.FloatField(null=True, blank=True)
    override_beading_h  = models.FloatField(null=True, blank=True)
    override_wall_t     = models.FloatField(null=True, blank=True)

    # Costing
    unit_cost  = models.FloatField(default=0)

    # Edited BOM storage
    edited_bom    = models.TextField(blank=True, null=True)
    edited_totals = models.TextField(blank=True, null=True)

    # Status
    status     = models.CharField(max_length=20, default='pending')
    PACKING_TYPE_CHOICES = [
    ('box',       'Wooden Box'),
    ('pallet',    'Pallet Only'),
    ('box_pallet','Box + Pallet'),
]

    packing_type     = models.CharField(
    max_length=20,
    choices=PACKING_TYPE_CHOICES,
    default='box'
)
    pallet_deck_type = models.CharField(
    max_length=20,
    default='auto'
)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} ({self.rfq.rfq_number})"


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent',  'Sent'),
        ('won',   'Won'),
        ('lost',  'Lost'),
    ]

    rfq              = models.OneToOneField(
                         RFQ,
                         on_delete=models.CASCADE,
                         related_name='quotation'
                       )
    quotation_number = models.CharField(max_length=50, unique=True)
    subtotal         = models.FloatField(default=0)
    overhead_pct     = models.FloatField(default=7)
    overhead_amount  = models.FloatField(default=0)
    margin_pct       = models.FloatField(default=25)
    margin_amount    = models.FloatField(default=0)
    before_gst       = models.FloatField(default=0)
    gst_pct          = models.FloatField(default=12)
    gst_amount       = models.FloatField(default=0)
    grand_total      = models.FloatField(default=0)
    status           = models.CharField(
                         max_length=20,
                         choices=STATUS_CHOICES,
                         default='draft'
                       )
    valid_until      = models.DateField(null=True, blank=True)
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quotation_number