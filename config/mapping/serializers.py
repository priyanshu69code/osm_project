# mapping/serializers.py
from rest_framework_gis import serializers
from .models import Perimeter, RouteRequest

class PerimeterSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Perimeter
        geo_field = 'geometry'
        fields = ('id', 'name', 'created_at')

class RouteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRequest
        fields = '__all__'
