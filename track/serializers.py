from rest_framework import serializers


class PurchaseOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    po_number = serializers.IntegerField()
    delivery_date = serializers.DateField()


class SkipGateEntryStageRequestSerializer(serializers.Serializer):
    vehicle_tracking_number = serializers.CharField()
    stage_id = serializers.IntegerField()



class VehicleTrackingNumberSerializer(serializers.Serializer):
    vehicle_tracking_number = serializers.UUIDField()



class StageStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    entry_log_exist = serializers.BooleanField()
    exit_log_exist = serializers.BooleanField()
    completed = serializers.BooleanField()


class LogSerializer(serializers.Serializer):
    entry_timestamp = serializers.CharField(allow_null=True)
    exit_timestamp = serializers.CharField(allow_null=True)


class StageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    skipped = serializers.BooleanField()
    completed = serializers.BooleanField()
    logs = LogSerializer(allow_null=True)


class TimelineResponseSerializer(serializers.Serializer):
    current_stage_id = StageStatusSerializer()
    next_stage_id = StageStatusSerializer()
    timeline = StageSerializer(many=True)



class GateEntryDashboardRequestSerializer(serializers.Serializer):
    stage_id = serializers.IntegerField()
    organization_id = serializers.IntegerField()


class CurrentEntrySerializer(serializers.Serializer):
    gate_entry_number = serializers.CharField()
    vehicle_number = serializers.CharField()
    date = serializers.DateField()
    time = serializers.TimeField()


class IncomingEntrySerializer(serializers.Serializer):
    gate_entry_number = serializers.CharField()
    vehicle_number = serializers.CharField()


class CompletedExitSerializer(serializers.Serializer):
    gate_entry_number = serializers.CharField()
    vehicle_number = serializers.CharField()
    date = serializers.DateField()
    time = serializers.TimeField()


class GateEntryDashboardResponseSerializer(serializers.Serializer):
    current = CurrentEntrySerializer(many=True)
    incoming = IncomingEntrySerializer(many=True)
    completed = CompletedExitSerializer(many=True)