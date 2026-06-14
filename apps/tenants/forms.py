from django import forms
from django.utils.text import slugify
from .models import Business, BusinessSettings

class RegisterBusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'description', 'category']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if Business.objects.filter(name=name).exists():
            raise forms.ValidationError("El nombre de la empresa ya existe")
        return name
    
    def save(self,commit=True):
        instance = super().save(commit=False)
        base_slug = slugify(self.cleaned_data['name'])
        slug = base_slug
        counter = 1
        while Business.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        instance.slug = slug
        instance.subdomain = slug
        instance.owner = self.owner
        instance.subscription_tier = 'trial'
        if commit:
            instance.save()
            BusinessSettings.objects.create(business=instance)
        return instance


class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = [
            'logo', 'primary_color', 'secondary_color', 'font_family',
            'phone_contact', 'email_contact', 'address_contact',
            'facebook_url', 'instagram_url', 'working_hours',
            'google_maps_url', 'google_calendar_enabled', 'google_calendar_id',
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'working_hours': forms.Textarea(attrs={'rows': 6}),
        }