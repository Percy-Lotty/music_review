from django import forms

from .models import UserRating


class RatingForm(forms.ModelForm):
    class Meta:
        model = UserRating
        fields = ["score"]
        widgets = {
            "score": forms.NumberInput(
                attrs={"min": 0, "max": 10, "class": "rating-input"}
            ),
        }
