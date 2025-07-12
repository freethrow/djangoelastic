from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect


from elasticsearch import Elasticsearch
from django.conf import settings

from django.contrib import messages
from .forms import ArticleForm

from .models import Article

from bson import ObjectId
from bson.errors import InvalidId


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

    # Get the article or return 404
    article = get_object_or_404(Article, id=object_id)

    # Create context with all needed data
    context = {"article": article}

    return render(request, "articles/article_detail.html", context)


def test_search(request):
    """
    Search view with form that accepts user query
    """
    # Get search query from form
    query = request.GET.get("q", "").strip()

    # Connect to Elasticsearch
    es_config = settings.ELASTICSEARCH_DSL["default"]
    es = Elasticsearch([es_config["hosts"]])

    results = []
    total_hits = 0

    if query:  # Only search if query is provided
        try:
            # Multi-match search with title weighted higher than content
            response = es.search(
                index="articles",
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "content"],  # Title has 3x weight
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                        }
                    },
                    "size": 10,
                },
            )

            # Extract results
            for hit in response["hits"]["hits"]:
                results.append(
                    {
                        "id": hit["_id"],
                        "title": hit["_source"]["title"],
                        "category": hit["_source"]["category"],
                        "content": hit["_source"]["content"][:150] + "...",
                        "score": hit["_score"],
                    }
                )

            total_hits = response["hits"]["total"]["value"]

        except Exception as e:
            context = {"error": str(e), "query": query}
            return render(request, "articles/test_search.html", context)

    context = {"results": results, "total_hits": total_hits, "query": query}

    return render(request, "articles/test_search.html", context)


def add_article(request):
    """
    View for adding new articles
    """
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            try:
                # Save the article
                article = form.save()

                # Add success message
                messages.success(
                    request, f'Article "{article.title}" has been created successfully!'
                )

                # Redirect to the new article or back to form
                return redirect("detail", article_id=str(article.id))
                # Or redirect back to the form: return redirect('add_article')

            except Exception as e:
                messages.error(request, f"Error saving article: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ArticleForm()

    context = {"form": form, "title": "Add New Article"}
    return render(request, "articles/add_article.html", context)
