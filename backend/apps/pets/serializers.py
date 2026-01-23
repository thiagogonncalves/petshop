"""
Pet serializers
"""
from rest_framework import serializers
from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    """Serializer for Pet model"""
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    sex_display = serializers.CharField(source='get_sex_display', read_only=True)
    age = serializers.ReadOnlyField()
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'species', 'species_display', 'breed',
            'birth_date', 'weight', 'sex', 'sex_display', 'color',
            'photo', 'observations', 'client', 'client_name', 'age',
            'is_active', 'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'age']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Override to return full photo URL"""
        representation = super().to_representation(instance)
        if instance.photo:
            request = self.context.get('request')
            if request:
                representation['photo'] = request.build_absolute_uri(instance.photo.url)
            else:
                representation['photo'] = instance.photo.url
        return representation
