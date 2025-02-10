from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.


# routes/views.py
from rest_framework.decorators import api_view
from .tasks import batch_process_routes

@api_view(['POST'])
def batch_route_calculation(request):
    route_ids = request.data.get('route_ids', [])
    task = batch_process_routes.delay(route_ids)
    return Response({'task_id': task.id}, status=202)
