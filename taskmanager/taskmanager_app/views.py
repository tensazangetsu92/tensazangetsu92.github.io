from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CardsCollections, Cards
import json

@csrf_exempt
def show_collections(request):
    collections = CardsCollections.objects.all().values('id', 'collection_name')
    collections_list = list(collections)  # Преобразуем QuerySet в список
    return JsonResponse(collections_list, safe=False)

@csrf_exempt
def add_collection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        collection_name = data.get('collection_name')

        if collection_name:
            CardsCollections.objects.create(
                collection_name=collection_name,
            )
            return JsonResponse({'message': 'Collection created successfully'}, status=201)
        return JsonResponse({'error': 'Invalid data'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_collection(request, collection_id):
    if request.method == 'DELETE':
        try:
            collection = CardsCollections.objects.get(id=collection_id)
            collection.delete()
            return JsonResponse({'message': 'Collection deleted successfully'}, status=204)
        except CardsCollections.DoesNotExist:
            return JsonResponse({'error': 'Collection not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_cards(request,collection_id):
    if request.method == 'DELETE':
        try:
            Cards.objects.filter(collection=collection_id).delete()
            return JsonResponse({'message': 'Collection deleted successfully'}, status=204)
        except Cards.DoesNotExist:
            return JsonResponse({'error': 'Collection not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def show_cards(request, collection_id):
    cards = Cards.objects.filter(collection_id=collection_id).all().values('id','text_english','text_russian')
    cards_list = list(cards)  # Преобразуем QuerySet в список
    return JsonResponse(cards_list, safe=False)

@csrf_exempt
def add_card(request, collection_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        text_russian = data.get('text_russian')
        text_english = data.get('text_english')
        if text_russian and text_english:
            Cards.objects.create(
                text_russian=text_russian,
                text_english=text_english,
                collection_id=collection_id
            )
            return JsonResponse({'message': 'Card created successfully'}, status=201)
        return JsonResponse({'error': 'Invalid data'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)