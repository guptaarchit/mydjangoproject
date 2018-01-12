from django import forms

class DeviceDetails(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        fields = ('username','email','password')
