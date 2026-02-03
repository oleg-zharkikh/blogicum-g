from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Tag

@login_required
@require_http_methods(["POST"])
def toggle_tag_status(request, tag_id):
    try:
        tag = Tag.objects.get(id=tag_id)
        
        # Переключаем статус
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in ['active', 'inactive']:
            tag.status = new_status
            tag.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid status'
            }, status=400)
            
    except Tag.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tag not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_tag(request, tag_id):
    try:
        tag = Tag.objects.get(id=tag_id)
        tag.delete()
        
        return JsonResponse({
            'success': True
        })
        
    except Tag.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tag not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


"""
from django.urls import path
from . import views

urlpatterns = [
    path('api/tags/<int:tag_id>/toggle-status/', views.toggle_tag_status, name='toggle_tag_status'),
    path('api/tags/<int:tag_id>/delete/', views.delete_tag, name='delete_tag'),
    # ... другие маршруты
]



"""