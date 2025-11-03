from django import forms
from .models import Cost, CostType

class CostForm(forms.ModelForm):
    class Meta:
        model = Cost
        fields = ['title', 'cost', 'cause', 'type']  # A kívánt mezők

    # Alapértelmezett widget beállítások
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Add meg a költség címét'})
    )
    cost = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Add meg a költség összegét (Ft)'}),
        required=False  # Mivel nem minden költség szükségszerűen numerikus, lehet opcionális
    )
    cause = forms.CharField(
        max_length=400,
        widget=forms.TextInput(attrs={'placeholder': 'Add meg a költség okát/célját'}),
        required=False  # Ha nem kötelező, akkor opcionális
    )
    type = forms.ModelChoiceField(
        queryset=CostType.objects.all(),
        empty_label="Válassz típust",
        required=True,
        widget=forms.Select(attrs={'placeholder': 'Válassz a költség típusai közül'})
    )


class CostTypeForm(forms.ModelForm):
    class Meta:
        model = CostType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Kategória neve', 'class': 'form-control'})
        }