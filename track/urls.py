from django.urls import path
from track.views import purchase_order_list, skip_gate_entry_stage, timeline, gate_entry_dashboard


urlpatterns = [
    path('get/purchase_order_list/', purchase_order_list, name='get-po'),
    path(
        'skip-stage/',
        skip_gate_entry_stage,
        name='skip-stage'
    ), 
    path(
        'get-timeline/',
        timeline,
        name='get-timeline'
    ),
    path(
        'gate-entry/dashboard/',
        gate_entry_dashboard,
        name='gate-entry-dashboard'
    ),
]
