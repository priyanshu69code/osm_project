# mapping/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.gis.geos import Point, LineString
from .models import Perimeter, RouteRequest
from .serializers import PerimeterSerializer, RouteRequestSerializer
import requests
import json

class PerimeterViewSet(viewsets.ModelViewSet):
    queryset = Perimeter.objects.all()
    serializer_class = PerimeterSerializer

class RouteViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Extract coordinates
            start_lon = request.data['start_point']['coordinates'][0]
            start_lat = request.data['start_point']['coordinates'][1]
            end_lon = request.data['end_point']['coordinates'][0]
            end_lat = request.data['end_point']['coordinates'][1]

            # Call OSRM API
            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
            response = requests.get(osrm_url, params={
                'overview': 'full',
                'steps': 'true'
            })

            if response.status_code == 200:
                route_data = response.json()
                # Save to database
                route_request = RouteRequest.objects.create(
                    start_point=Point(start_lon, start_lat),
                    end_point=Point(end_lon, end_lat),
                    duration=route_data['routes'][0]['duration'],
                    distance=route_data['routes'][0]['distance'],
                    route_geometry=LineString(
                        [tuple(point) for point in decode_polyline(route_data['routes'][0]['geometry'])]
                    )
                )
                return Response({
                    'status': 'success',
                    'data': route_data,
                    'db_id': route_request.id
                })
            return Response({'error': 'Routing failed'}, status=400)
        return Response(serializer.errors, status=400)

def decode_polyline(polyline_str):
    index = 0
    lat = 0
    lng = 0
    coordinates = []
    while index < len(polyline_str):
        shift = 0
        result = 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append((round(lng * 1e-5, 6), round(lat * 1e-5, 6)))
    return coordinates
