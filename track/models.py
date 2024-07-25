from django.db import models
import uuid
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class PurchaseOrderHeader(models.Model):
    tenant_organisation = models.IntegerField()
    po_number = models.CharField("PO Number", max_length=32)
    business_partner = models.IntegerField()
    STATUS_CHOICES = (
        ('1', 'registered'),
        ('2', 'approved'),
        ('3', 'confirmed'),
        ('4', 'cancelled'),
        ('5', 'delivered')
    )
    status = models.CharField(
        "Status",
        max_length=1,
        null=False,
        blank=False,
        choices=STATUS_CHOICES
    )
    delivery_date = models.DateField("Delivery Date")
    total_value = models.IntegerField("Total Value")
    weight = models.IntegerField("Weight", null=True, blank=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    modified = models.DateTimeField("Modified", auto_now=True)

    def __str__(self):
        return f"PurchaseOrder({self.id}, {self.po_number})"
    
    class Meta:
        managed = False
        db_table = 'track_purchaseorderheader'


class BusinessPartner(models.Model):
    name = models.CharField("Name", max_length=64)
    email = models.EmailField("Email")
    mobile = models.CharField("Mobile no", max_length=10)
    PARTNER_CATEGORY = (
        ('1', 'person'),
        ('2', 'organization'),
        ('3', 'group')
    )
    partner_category = models.CharField(
        "Partner",
        max_length=1,
        null=False, 
        choices=PARTNER_CATEGORY
    )
    organisation = models.IntegerField()
    gst_number = models.CharField("GST Number", max_length=64)
    created = models.DateTimeField("Created", auto_now_add=True)
    modified = models.DateTimeField("Modified", auto_now=True)	

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = False
        db_table = 'track_businesspartner'


class Organisation(models.Model):
    tenant = models.IntegerField()
    name = models.CharField(max_length=64)
    gst_number = models.CharField(max_length=64)
    description = models.TextField(null=True)
    STATUS_CHOICES = (
        ('1', 'Active'),
        ('2', 'Expired'),
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'track_organisation'


class Tenant(models.Model):
    tenant_code = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=64)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    domain = models.CharField(max_length=64, null=True)
    description = models.TextField(null=True)
    STATUS_CHOICES = (
        ('1', 'Active'),
        ('2', 'Expired'),
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'track_tenant'


class PurchaseOrderLineItem(models.Model):
    tenant_organisation = models.IntegerField()
    purchase_order = models.IntegerField()
    name = models.CharField("Name", max_length=64)
    material_code = models.CharField("Material Code", max_length=64)
    quantity = models.IntegerField("Quantity")
    per_unit_price = models.DecimalField(
        "Per Unit Price",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    per_unit_weight = models.DecimalField(
        "Per Unit Weight",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    unit_of_measurement = models.CharField(max_length=8)
    sgst = models.IntegerField("SGST")
    cgst = models.IntegerField("CGST")
    igst = models.IntegerField("IGST")
    discount = models.IntegerField("Discount", null=True, blank=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    modified = models.DateTimeField("Modified", auto_now=True)

    def __str__(self):
        return (
            f"PurchaseOrderLineItem("
            f"{self.id, self.purchase_order.po_number}, "
            f"{self.name})"
        )


class VehicleTrackingStage(models.Model):
    tenant_organisation = models.IntegerField()
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    stage_order = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
   

class StageAssignment(models.Model):
    tenant_organisation = models.IntegerField()
    stage = models.IntegerField()
    profile = models.IntegerField()


class OraganisationAssignment(models.Model):
    organisation = models.IntegerField()
    profile = models.IntegerField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    USER_TYPE_CHOICES = [
        ('1', 'SuperAdmin'),
        ('2', 'Admin'),
        ('3', 'User'),
    ]
    user_type = models.CharField(
        max_length=1,
        choices=USER_TYPE_CHOICES,
        blank=True,
        null=True
    )
    tenant_organisation = models.IntegerField()
    name = models.CharField(max_length=64)
    email = models.EmailField()
    mobile_no = models.CharField(max_length=20)
    address = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
 
    def __str__(self):
        return f"{self.user}"


class VehicleTracking(models.Model):
    tenant_organisation = models.IntegerField()
    vehicle_number = models.CharField("Vehicle Number", max_length=10)
    vehicle_tracking_number = models.UUIDField(
        verbose_name="Vehicle Tracking Number",
        default=uuid.uuid4
    )
    purchase_order = models.IntegerField()
    stage = models.IntegerField()
    completed = models.BooleanField("Completed", null=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    modified = models.DateTimeField("Modified", auto_now=True)

    def __str__(self):
        return f"{self.vehicle_tracking_number}"
  

class TargetVsActual(models.Model):
    tenant_organisation = models.IntegerField()
    stage = models.IntegerField()
    gate_entry = models.IntegerField()
    table = models.CharField(max_length=64)
    field = models.CharField(max_length=64)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True
    )
    object_id = models.PositiveIntegerField(null=True)
    target = GenericForeignKey('content_type', 'object_id')
    target_value = models.CharField(max_length=64)
    actual_value = models.CharField(max_length=64)
    remarks = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.object_id}"


class VehicleTrackingLogs(models.Model):
    vehicle_tracking = models.IntegerField()
    stage = models.IntegerField()
    LOG_CHOICES = (
        ('1', 'entry'),
        ('2', 'exit'),
    )
    log_type = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        choices=LOG_CHOICES
    )

    skipped = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f"{self.gate_entry}"
