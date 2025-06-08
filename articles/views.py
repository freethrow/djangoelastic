from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Article

from bson import ObjectId
from bson.errors import InvalidId


# Create your views here.
def index(request):
    articles = Article.objects.order_by("title")[:10]
    return render(request, "articles/index.html", {"articles": articles})


def detail(request, article_id):
    """
    Display an article by its MongoDB ObjectId

    Args:
        request: Django request object
        article_id: String representation of the MongoDB ObjectId
    """
    # Convert string ID to MongoDB ObjectId
    try:
        object_id = ObjectId(article_id)
    except InvalidId:
        raise Http404(f"Invalid recipe ID format: {article_id}")

    # Get the recipe or return 404
    article = get_object_or_404(Article, id=object_id)

    # Create context with all needed data
    context = {"article": article}

    return render(request, "articles/article_detail.html", context)
