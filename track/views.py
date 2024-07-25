from rest_framework.response import Response
from rest_framework import status as status
from rest_framework.decorators import api_view
from track.models import (
    PurchaseOrderHeader,
    VehicleTracking,
    VehicleTrackingLogs,
    VehicleTrackingStage
)
from track.serializers import (
    PurchaseOrderSerializer,
    # PurchaseOrderRequestSerializer,
    SkipGateEntryStageRequestSerializer,
    VehicleTrackingNumberSerializer,
    TimelineResponseSerializer,
    GateEntryDashboardRequestSerializer,
    GateEntryDashboardResponseSerializer
)

# def get_queryset(queryset):
#     if isinstance(queryset, QuerySet):
#         for query in queryset:
#             query.po = PurchaseOrderHeader.objects.using("core").get(
#                 id=query.purchase_order
#             )
#         return queryset
#     else:
#         queryset.po = PurchaseOrderHeader.objects.using("core").get(
#             id=queryset.purchase_order
#         )
#         return queryset


@api_view(['GET'])
def purchase_order_list(request):
    orders = PurchaseOrderHeader.objects.using('core').all()
    print(orders)
    serializer = PurchaseOrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def skip_gate_entry_stage(request):
    request_serializer = SkipGateEntryStageRequestSerializer(
        data=request.query_params
    )
    if request_serializer.is_valid():
        vehicle_tracking_number = request_serializer.validated_data.get(
            'vehicle_tracking_number'
        )
        stage_id = request_serializer.validated_data.get('stage_id')

        try:
            vehicle_entry_number = VehicleTracking.objects.get(
                vehicle_tracking_number=vehicle_tracking_number
            )
        except VehicleTracking.DoesNotExist:
            return Response(
                {"error": "Gate entry not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            stage = VehicleTrackingStage.objects.get(id=stage_id)
        except VehicleTrackingStage.DoesNotExist:
            return Response(
                {"error": "Stage not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        VehicleTrackingLogs.objects.create(
            vehicle_tracking=vehicle_entry_number.id,
            stage=stage.id,
            log_type='1',
            skipped=True
        )
        VehicleTrackingLogs.objects.create(
            vehicle_tracking=vehicle_entry_number.id,
            stage=stage.id,
            log_type='2',
            skipped=True
        )

        next_stage = VehicleTrackingStage.objects.filter(
            stage_order__gt=stage.stage_order
        ).order_by('stage_order').first()

        if next_stage:
            vehicle_entry_number.stage = next_stage.id
            vehicle_entry_number.save()
            return Response(
                {"message": "vehicle_tracking stage skipped successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "No next stage available to skip to"},
                status=status.HTTP_204_NO_CONTENT
            )
    return Response(request_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def timeline(request):
    request_serializer = VehicleTrackingNumberSerializer(
        data=request.query_params
    )
    if request_serializer.is_valid():
        vehicle_tracking_number = request_serializer.validated_data.get(
            'vehicle_tracking_number'
        )
        try:
            vehicle_entry = VehicleTracking.objects.get(
                vehicle_tracking_number=vehicle_tracking_number
            )
        except VehicleTracking.DoesNotExist:
            return Response(
                {"error": "Vehicle tracking number not found"},
                status=status.HTTP_404_NOT_FOUND
            )
      
        logs = VehicleTrackingLogs.objects.filter(
            vehicle_tracking=vehicle_entry.id
        )
        stages = VehicleTrackingStage.objects.all().order_by('stage_order')

        response_data = {
            "current_stage_id": None,
            "next_stage_id": None,
            "timeline": []
        }
        current_stage = vehicle_entry.stage if vehicle_entry.stage else None

        check_logs = True
        
        for index, stage in enumerate(stages):
            if check_logs:
                entry_log = logs.filter(stage=stage.id, log_type='1').first()
                exit_log = logs.filter(stage=stage.id, log_type='2').first()
                
                if not entry_log and not exit_log:
                    check_logs = False

            entry_timestamp = entry_log.created.strftime(
                "%dth %b '%y %I:%M %p"
            ) if entry_log else None

            exit_timestamp = exit_log.created.strftime(
                "%dth %b '%y %I:%M %p"
            ) if exit_log else None

            skipped = False

            if (
                entry_log and entry_log.skipped and
                exit_log and exit_log.skipped
            ):
                skipped = True
            
            completed = True if exit_log else False
            response_data["timeline"].append(
                {
                    "id": stage.id,
                    "name": stage.name,
                    "skipped": skipped,
                    "completed": completed,
                    "logs": {
                        "entry_timestamp": entry_timestamp,
                        "exit_timestamp": exit_timestamp
                    }
                }
            )
            entry = True if entry_timestamp else False
            exit = True if exit_timestamp else False
            
            if stage.id == current_stage:
                response_data["current_stage_id"] = {
                    "id": stage.id,
                    "name": stage.name,
                    "entry_log_exist": entry,
                    "exit_log_exist": exit,
                    "completed": vehicle_entry.completed
                }
                if index + 1 < len(stages):
                    next_stage = stages[index + 1]
                    response_data["next_stage_id"] = {
                        "id": next_stage.id,
                        "name": next_stage.name,
                        "entry_log_exist": False,
                        "exit_log_exist": False,
                        "completed": False
                    }
        response_serializer = TimelineResponseSerializer(response_data)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )
    return Response(
        request_serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
def gate_entry_dashboard(request):
    request_serializer = GateEntryDashboardRequestSerializer(data=request.query_params)
    if request_serializer.is_valid():
        stage_id = request_serializer.validated_data.get('stage_id')
        organisation_id = request_serializer.validated_data.get('organization_id')

        try:
            stage = VehicleTrackingStage.objects.get(id=stage_id)
            previous_stage = VehicleTrackingStage.objects.filter(stage_order__lt=stage.stage_order).order_by('-stage_order').first()
            previous_stage_id = previous_stage.id if previous_stage else None

            gate_entries = VehicleTracking.objects.filter(stage=stage_id, tenant_organisation=organisation_id)

            current_gate_id = []
            incoming_gate_id = []
            completed_gate_id = []

            if previous_stage_id is not None:
                previous_stage_completed_entries = VehicleTrackingLogs.objects.filter(
                    log_type='2',
                    stage=previous_stage_id,
                    vehicle_tracking__tenant_organisation=organisation_id,
                )
                previous_stage_completed_entries = [entry.vehicle_tracking_id for entry in gate_entries]
                print(previous_stage_completed_entries)
                incoming_gate_entries = VehicleTracking.objects.filter(
                    id__in=previous_stage_completed_entries,
                    stage=previous_stage_id,
                    tenant_organisation=organisation_id,
                    completed=True
                )
                print("Incoming Gate Entries:", incoming_gate_entries)
                for incoming_entry in incoming_gate_entries:
                    incoming_gate_id = {
                        "gate_entry_number": incoming_entry.vehicle_tracking_number,
                        "vehicle_number": incoming_entry.vehicle_number
                    }

            for entry in gate_entries:
                entry_log_not_skipped = VehicleTrackingLogs.objects.filter(
                    vehicle_tracking=entry.id,
                    log_type='1',
                    stage=stage_id,
                    skipped=False
                ).order_by('-created').first()

                entry_log_skipped = VehicleTrackingLogs.objects.filter(
                    vehicle_tracking=entry.id,
                    log_type='1',
                    stage=stage_id,
                    skipped=True
                ).order_by('-created').first()

                exit_log_not_skipped = VehicleTrackingLogs.objects.filter(
                    vehicle_tracking=entry.id,
                    log_type='2',
                    stage=stage_id,
                    skipped=False
                ).order_by('-created').first()

                exit_log_skipped = VehicleTrackingLogs.objects.filter(
                    vehicle_tracking=entry.id,
                    log_type='2',
                    stage=stage_id,
                    skipped=True
                ).order_by('-created').first()

                if entry_log_not_skipped and not entry.completed:
                    current_gate_id.append({
                        "gate_entry_number": entry.vehicle_tracking_number,
                        "vehicle_number": entry.vehicle_number,
                        "date": entry_log_not_skipped.created.date(),
                        "time": entry_log_not_skipped.created.time()
                    })

                if exit_log_not_skipped and entry_log_not_skipped:
                    completed_gate_id.append({
                        "gate_entry_number": entry.vehicle_tracking_number,
                        "vehicle_number": entry.vehicle_number,
                        "date": exit_log_not_skipped.created.date(),
                        "time": exit_log_not_skipped.created.time(),
                    })

                if exit_log_skipped and entry_log_skipped:
                    completed_gate_id.append({
                        "gate_entry_number": entry.vehicle_tracking_number,
                        "vehicle_number": entry.vehicle_number,
                        "date": exit_log_skipped.created.date(),
                        "time": exit_log_skipped.created.time(),
                    })

            response_data = {
                "current": current_gate_id,
                "incoming": incoming_gate_id,
                "completed": completed_gate_id
            }

            response_serializer = GateEntryDashboardResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except VehicleTrackingStage.DoesNotExist:
            return Response({"error": "Stage not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
