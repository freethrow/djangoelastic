from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from django.conf import settings
from articles.models import Article  # Replace 'articles' with your actual app name


class Command(BaseCommand):
    help = "Index articles to Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-index",
            action="store_true",
            help="Delete the index before creating it",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Batch size for bulk indexing (default: 100)",
        )

    def handle(self, *args, **options):
        # Connect to Elasticsearch
        es_config = settings.ELASTICSEARCH_DSL["default"]
        es = Elasticsearch([es_config["hosts"]])

        index_name = "articles"

        # Delete index if requested
        if options["delete_index"]:
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
                self.stdout.write(f"Deleted index '{index_name}'")

        # Create index if it doesn't exist
        if not es.indices.exists(index=index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "category": {"type": "keyword"},
                        "content": {"type": "text", "analyzer": "standard"},
                    }
                }
            }
            es.indices.create(index=index_name, body=mapping)
            self.stdout.write(f"Created index '{index_name}'")

        # Get all articles
        articles = Article.objects.all()
        total_articles = articles.count()
        self.stdout.write(f"Indexing {total_articles} articles...")

        # Bulk index articles
        batch_size = options["batch_size"]
        batch = []
        indexed_count = 0

        for article in articles:
            doc = {
                "title": article.title,
                "category": article.category,
                "content": article.content,
            }

            # Convert ObjectId to string for the document ID
            doc_id = str(article.id)

            # Add to batch
            batch.append({"_index": index_name, "_id": doc_id, "_source": doc})

            # Index batch when it reaches batch_size
            if len(batch) >= batch_size:
                try:
                    from elasticsearch.helpers import bulk

                    bulk(es, batch)
                    indexed_count += len(batch)
                    self.stdout.write(
                        f"Indexed {indexed_count}/{total_articles} articles"
                    )
                    batch = []
                except Exception as e:
                    self.stdout.write(f"Error indexing batch: {e}")

        # Index remaining articles
        if batch:
            try:
                from elasticsearch.helpers import bulk

                bulk(es, batch)
                indexed_count += len(batch)
            except Exception as e:
                self.stdout.write(f"Error indexing final batch: {e}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {indexed_count} articles")
        )
