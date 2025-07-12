# forms.py (create this file in your app)
from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "category", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter article title...", "required": True}
            ),
            "category": forms.TextInput(
                attrs={
                    "placeholder": "e.g., technology, programming, web development...",
                    "required": True,
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Write your article content here...",
                    "required": True,
                }
            ),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if len(content) < 50:
            raise forms.ValidationError("Content must be at least 50 characters long.")
        return content
