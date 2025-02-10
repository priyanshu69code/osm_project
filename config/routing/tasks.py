# routes/tasks.py (Celery tasks)
from celery import shared_task
from django.db import transaction
from .models import RouteRequest
from .routing import OSRMEngine

@shared_task
def batch_process_routes(route_ids):
    routes = RouteRequest.objects.filter(id__in=route_ids).select_related('start_point', 'end_point')

    results = []
    for route in routes:
        try:
            route_data = OSRMEngine.get_route(
                (route.start_point.x, route.start_point.y),
                (route.end_point.x, route.end_point.y)
            )
            results.append({
                'id': route.id,
                'status': 'success',
                'data': route_data
            })
            # Bulk update with transaction
            with transaction.atomic():
                RouteRequest.objects.filter(id=route.id).update(
                    duration=route_data['duration'],
                    distance=route_data['distance'],
                    route_geometry=route_data['geometry']
                )
        except Exception as e:
            results.append({
                'id': route.id,
                'status': 'error',
                'message': str(e)
            })

    return results
