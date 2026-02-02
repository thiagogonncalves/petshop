"""
Scheduling serializers
"""
from rest_framework import serializers
from .models import Appointment, BusinessHoursConfig, BusinessHoursRule, BusinessClosure
from .services.availability import get_available_slots, _is_date_closed, _get_rule_for_weekday


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=10, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    created_via_display = serializers.CharField(source='get_created_via_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'pet', 'pet_name',
            'service', 'service_name', 'service_price',
            'scheduled_date', 'start_at', 'end_at', 'status', 'status_display',
            'observations', 'created_via', 'created_via_display',
            'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'start_at', 'end_at']

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    def validate(self, attrs):
        """Valida data/hora: dia aberto, horário de funcionamento, sem conflito."""
        scheduled = attrs.get('scheduled_date')
        service = attrs.get('service') or (self.instance.service if self.instance else None)
        if not scheduled or not service:
            return attrs
        target_date = scheduled.date() if hasattr(scheduled, 'date') else scheduled
        time_str = scheduled.strftime('%H:%M') if hasattr(scheduled, 'strftime') else None
        if not time_str:
            return attrs
        if _is_date_closed(target_date):
            raise serializers.ValidationError({
                'scheduled_date': f'Data {target_date.strftime("%d/%m/%Y")} está fechada (feriado/folga).'
            })
        weekday = target_date.weekday()
        rule = _get_rule_for_weekday(weekday)
        if not rule or not rule.is_open:
            raise serializers.ValidationError({
                'scheduled_date': f'Dia {target_date.strftime("%d/%m/%Y")} não está configurado para atendimento.'
            })
        exclude_id = self.instance.pk if self.instance else None
        available = get_available_slots(service.id, target_date, exclude_appointment_id=exclude_id)
        if time_str not in available:
            raise serializers.ValidationError({
                'scheduled_date': f'Horário {time_str} não disponível para esta data. '
                f'Horários disponíveis: {", ".join(available) if available else "nenhum"}.'
            })
        return attrs

    def create(self, validated_data):
        from datetime import timedelta
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        validated_data['created_via'] = 'admin'
        service = validated_data.get('service')
        scheduled = validated_data.get('scheduled_date')
        if scheduled and service:
            validated_data['start_at'] = scheduled
            validated_data['end_at'] = scheduled + timedelta(minutes=service.duration_minutes)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        from datetime import timedelta
        service = validated_data.get('service') or instance.service
        scheduled = validated_data.get('scheduled_date') or instance.scheduled_date or instance.start_at
        if scheduled and service:
            validated_data['start_at'] = scheduled
            validated_data['end_at'] = scheduled + timedelta(minutes=service.duration_minutes)
        return super().update(instance, validated_data)


class BusinessHoursRuleSerializer(serializers.ModelSerializer):
    open_time_str = serializers.SerializerMethodField()
    close_time_str = serializers.SerializerMethodField()
    break_start_str = serializers.SerializerMethodField()
    break_end_str = serializers.SerializerMethodField()

    class Meta:
        model = BusinessHoursRule
        fields = ['id', 'weekday', 'is_open', 'open_time', 'close_time', 'break_start', 'break_end',
                  'open_time_str', 'close_time_str', 'break_start_str', 'break_end_str']

    def get_open_time_str(self, obj):
        return obj.open_time.strftime('%H:%M') if obj.open_time else None

    def get_close_time_str(self, obj):
        return obj.close_time.strftime('%H:%M') if obj.close_time else None

    def get_break_start_str(self, obj):
        return obj.break_start.strftime('%H:%M') if obj.break_start else None

    def get_break_end_str(self, obj):
        return obj.break_end.strftime('%H:%M') if obj.break_end else None


class BusinessHoursConfigSerializer(serializers.ModelSerializer):
    rules = BusinessHoursRuleSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessHoursConfig
        fields = ['id', 'slot_minutes', 'timezone', 'rules', 'updated_at']


class BusinessClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClosure
        fields = ['id', 'date', 'reason']
