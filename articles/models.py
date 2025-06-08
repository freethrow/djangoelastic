from django.db import models


# https://www.kaggle.com/datasets/hgultekin/bbcnewsarchive


class Article(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField(blank=False)
    category = models.TextField(blank=False)

    class Meta:
        db_table = "articles"
        managed = False

    def __str__(self):
        return f"{self.title} ({self.category})"
