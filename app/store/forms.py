from django import forms
from unfold.widgets import UnfoldAdminTextInputWidget

from app.store.models import OpeningHours


class OpeningHoursInlineForm(forms.ModelForm):
    from_hour = forms.TimeField(
        label="abre às",
        input_formats=["%H:%M", "%H:%M:%S"],
        widget=UnfoldAdminTextInputWidget(
            attrs={
                "type": "time",
                "step": 60,
            }
        ),
        required=True,
    )
    to_hour = forms.TimeField(
        label="fecha às",
        input_formats=["%H:%M", "%H:%M:%S"],
        widget=UnfoldAdminTextInputWidget(
            attrs={
                "type": "time",
                "step": 60,
            }
        ),
        required=True,
    )

    def clean_from_hour(self):
        v = self.cleaned_data.get("from_hour")
        return v.replace(second=0, microsecond=0) if v else v

    def clean_to_hour(self):
        v = self.cleaned_data.get("to_hour")
        return v.replace(second=0, microsecond=0) if v else v

    class Meta:
        model = OpeningHours
        fields = "__all__"
