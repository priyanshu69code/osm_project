from django.db import models

# Create your models here.
# mapping/models.py
from django.contrib.gis.db import models

class Perimeter(models.Model):
    name = models.CharField(max_length=255)
    geometry = models.PolygonField(srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class RouteRequest(models.Model):
    start_point = models.PointField(srid=4326)
    end_point = models.PointField(srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True)
    distance = models.FloatField(null=True)
    route_geometry = models.LineStringField(srid=4326, null=True)
