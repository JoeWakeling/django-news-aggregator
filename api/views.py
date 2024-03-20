import json
from datetime import datetime
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from api.models import Story, Author


@require_http_methods(["POST"])
def login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Authentication successful
        django_login(request, user)
        return HttpResponse(("Welcome ", user.first_name), status=200, content_type="text/plain")
    else:
        # Authentication failed
        return HttpResponse("Authentication failed, username or password incorrect.",
                            status=401, content_type="text/plain")


@require_http_methods(["POST"])
def logout(request):
    if request.user.is_authenticated:
        django_logout(request)
        return HttpResponse("Goodbye.", status=200, content_type="text/plain")
    else:
        return HttpResponse("Method not allowed, not logged in", status=405, content_type="text/plain")


@require_http_methods(["GET", "POST", "DELETE"])
def stories(request, story_id=None):
    # Get stories
    if request.method == "GET":
        story_cat = request.GET.get("story_cat")
        story_region = request.GET.get("story_region")
        story_date = request.GET.get("story_date")

        # Ensure required fields are present in the request
        if not story_cat or not story_region or not story_date:
            return HttpResponse("Missing required fields", status=503, content_type="text/plain")

        # Ensure the category and region fields are valid choices within the database constraints
        if story_cat not in [sublist[0] for sublist in Story._meta.get_field("category").choices] and story_cat != '*':
            return HttpResponse("Invalid category", status=503, content_type="text/plain")
        if (story_region not in [sublist[0] for sublist in Story._meta.get_field("region").choices]
                and story_region != '*'):
            return HttpResponse("Invalid region", status=503, content_type="text/plain")

        # Ensure the date field in format dd/mm/yyyy or *
        if story_date == "*":
            story_date_obj = datetime.strptime("01/01/1900", "%d/%m/%Y")
        else:
            try:
                story_date_obj = datetime.strptime(story_date, "%d/%m/%Y")
            except ValueError:
                return HttpResponse("Invalid date format", status=503, content_type="text/plain")

        # Get filter arguments
        filter_args = {}
        if story_cat != '*':
            filter_args["category"] = story_cat
        if story_region != '*':
            filter_args["region"] = story_region
        filter_args["date__gte"] = story_date_obj.strftime("%Y-%m-%d")

        # Get matching stories from the database
        stories_found = Story.objects.filter(**filter_args).order_by("date")

        # If not stories found return 404
        if not stories_found:
            return HttpResponse("No stories found", status=404, content_type="text/plain")

        # Return the stories as a JSON payload
        payload = {"stories": []}
        for story in stories_found:
            payload["stories"].append({
                "key": story.id,
                "headline": story.headline,
                "category": story.category,
                "region": story.region,
                "author": story.author.user.username,
                "date": story_date_obj.strftime("%d/%m/%Y"),
                "details": story.details,
            })
        return HttpResponse(json.dumps(payload), status=200, content_type="application/json")

    # Post story
    if request.method == "POST":
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse("Login required for this endpoint", status=503, content_type="text/plain")

        # Get JSON payload from respone and parse into dictionary
        payload = request.body.decode("utf-8")
        try:
            new_story_dict = json.loads(payload)
        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON payload", status=503, content_type="text/plain")

        # Ensure JSON payload contains correct fields
        required_keys = ["headline", "category", "region", "details"]
        for key in required_keys:
            if key not in new_story_dict:
                return HttpResponse("Missing required fields", status=503, content_type="text/plain")
            if not isinstance(new_story_dict[key], str):
                return HttpResponse("Invalid field value type", status=503, content_type="text/plain")

        # Ensure the headline and details string length is within the database constraints
        if len(new_story_dict["headline"]) > Story._meta.get_field("headline").max_length:
            return HttpResponse("Headline too long", status=503, content_type="text/plain")
        if len(new_story_dict["details"]) > Story._meta.get_field("details").max_length:
            return HttpResponse("Details too long", status=503, content_type="text/plain")

        # Ensure the category and region fields are valid choices within the database constraints
        if new_story_dict["category"] not in [sublist[0] for sublist in Story._meta.get_field("category").choices]:
            return HttpResponse("Invalid category", status=503, content_type="text/plain")
        if new_story_dict["region"] not in [sublist[0] for sublist in Story._meta.get_field("region").choices]:
            return HttpResponse("Invalid region", status=503, content_type="text/plain")

        # Write the new story to the database
        try:
            new_story = Story(
                headline=new_story_dict["headline"],
                category=new_story_dict["category"],
                region=new_story_dict["region"],
                author=Author.objects.get(user_id=request.user.id),
                date=datetime.today().date(),
                details=new_story_dict["details"]
            )
            new_story.save()
        except ValidationError or IntegrityError:
            return HttpResponse("Failed to save story", status=503, content_type="text/plain")

        # Return success response
        return HttpResponse("Story created sucessfully", status=201, content_type="text/plain")

    # Delete story
    if request.method == "DELETE":
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse("Login required for this endpoint", status=503, content_type="text/plain")

        # Ensure the story_id is present
        if not story_id:
            return HttpResponse("Missing required fields", status=503, content_type="text/plain")

        # Ensure the story_id exists in db
        try:
            story_to_delete = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return HttpResponse("Story does not exist", status=503, content_type="text/plain")

        # Ensure the story author is the user
        if story_to_delete.author.user_id != request.user.id:
            return HttpResponse("Only the author can delete this story", status=503, content_type="text/plain")

        # Delete the story
        story_to_delete.delete()

        # Return success
        return HttpResponse("Story deleted successfully", status=200, content_type="text/plain")
