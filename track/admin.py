from django.contrib import admin
from track.models import (
    TargetVsActual,
    VehicleTracking,
    VehicleTrackingLogs,
    Tenant,
    Profile,
    PurchaseOrderHeader,
    PurchaseOrderLineItem,
    BusinessPartner,
    Organisation,
    VehicleTrackingStage,
    StageAssignment,
    OraganisationAssignment
)

admin.site.register(VehicleTracking)
admin.site.register(TargetVsActual)
admin.site.register(VehicleTrackingLogs)
admin.site.register(Tenant)
admin.site.register(Profile)
admin.site.register(BusinessPartner)
admin.site.register(Organisation)
admin.site.register(PurchaseOrderHeader)
admin.site.register(PurchaseOrderLineItem)
admin.site.register(VehicleTrackingStage)
admin.site.register(StageAssignment)
admin.site.register(OraganisationAssignment)

