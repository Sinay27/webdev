from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from newsapi.models import Story
import json
from django.db.models import Q
import datetime

# Exempts the view from CSRF checks for API accessibility.
@csrf_exempt
def login_view(request):
    # Process only POST requests for login.
    if request.method == 'POST':
        # Parses username and password from request body.
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        # Authenticates user; logs them in if credentials are valid.
        if user is not None:
            login(request, user)
            return HttpResponse("Login successful", content_type="text/plain")
        else:
            return HttpResponse("Login failed", status=401, content_type="text/plain")

    # Returns a method not allowed response if request method is not POST.
    return HttpResponse("Method not allowed", status=405, content_type="text/plain")

# Handles logout; CSRF exempt since it doesn't pose a data change risk.
@csrf_exempt
def logout_view(request):
    # Logs out the user.
    logout(request)
    return HttpResponse('Logged out successfully.', content_type='text/plain')

# Handles story deletion, requiring user login.
@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_story(request, story_id):
    # Attempts to delete the story if it exists and belongs to the user.
    try:
        story = Story.objects.get(id=story_id, author=request.user)
        story.delete()
        return HttpResponse("Story deleted successfully", status=200)
    except Story.DoesNotExist:
        return HttpResponse("Story not found or not authorized to delete", status=404, content_type="text/plain")

# Combines story retrieval and posting in one view.
@csrf_exempt
@require_http_methods(["GET", "POST"])
def stories(request):
    # Processes POST requests to add a new story.
    if request.method == 'POST':
        # Ensures the user is logged in before adding a story.
        if not request.user.is_authenticated:
            return HttpResponse("Login required to add a story.", status=401, content_type="text/plain")
        
        # Creates a new story with the provided data.
        try:
            data = json.loads(request.body.decode('utf-8'))
            story = Story(
                headline=data['headline'],
                category=data['category'],
                region=data['region'],
                details=data['details'],
                author=request.user.author  # Assumes OneToOne relation User to Author.
            )
            story.save()
            return HttpResponse("Story added successfully.", status=201, content_type="text/plain")
        # Catches various exceptions and returns appropriate errors.
        except KeyError as e:
            return HttpResponse(f"Missing data: {str(e)}", status=400, content_type="text/plain")
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON", "detail": str(e)}, status=400)
        except Exception as e:
            return HttpResponseServerError(f"Error adding story: {str(e)}")

    # Processes GET requests to retrieve stories.
    elif request.method == 'GET':
        # Retrieves filter parameters from the request.
        story_cat = request.GET.get('story_cat', '*')
        story_region = request.GET.get('story_region', '*')
        story_date = request.GET.get('story_date', '*')

        # Builds a Q object to filter stories based on provided parameters.
        filters = Q()
        if story_cat != '*':
            filters &= Q(category=story_cat)
        if story_region != '*':
            filters &= Q(region=story_region)
        if story_date != '*':
            try:
                parsed_date = datetime.datetime.strptime(story_date, "%Y-%m-%d").date()
                filters &= Q(date__gte=parsed_date)
            except ValueError:
                return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400, content_type="text/plain")

        # Filters and returns the stories as a JSON response.
        stories = Story.objects.filter(filters).values('id', 'headline', 'category', 'region', 'details')
        return JsonResponse({'stories': list(stories)})
