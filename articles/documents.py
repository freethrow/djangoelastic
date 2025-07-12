# documents.py
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Article
from bson import ObjectId


@registry.register_document
class ArticleDocument(Document):
    # Explicitly define the id field to ensure it's treated as text
    id = fields.TextField()

    class Index:
        name = "articles"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Article
        fields = [
            "title",
            "category",
            "content",
        ]

    def prepare_id(self, instance):
        """Convert ObjectId to string for the id field"""
        return str(instance.id)

    def get_queryset(self):
        """Return the queryset for indexing"""
        return self.Django.model.objects.all()

    def prepare(self, instance):
        """Override prepare to handle ObjectId conversion"""
        data = super().prepare(instance)
        # Ensure all ObjectId fields are converted to strings
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
        return data

    def _prepare_action(self, object_instance, action):
        """Override to ensure ObjectId is converted to string in action metadata"""
        # Get the document data
        doc = self.prepare(object_instance)

        # Convert ObjectId to string for document ID
        doc_id = str(object_instance.pk)

        # Return the action with converted ID
        return {
            "_op_type": action,
            "_index": self._index._name,
            "_id": doc_id,
            "_source": doc,
        }

    def to_dict(self, include_meta=False, skip_empty=True):
        """Override to_dict to handle ObjectId in meta"""
        data = super().to_dict(include_meta=False, skip_empty=skip_empty)

        if include_meta:
            meta_dict = {}
            if hasattr(self.meta, "id") and self.meta.id is not None:
                # Convert ObjectId to string in meta
                meta_dict["_id"] = str(self.meta.id)
            if hasattr(self.meta, "index"):
                meta_dict["_index"] = self.meta.index
            data["_meta"] = meta_dict

        return data
