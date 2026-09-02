from django import forms
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.tenants.models import BusinessMember, Service

from .models import Booking
from .validators import calculate_end_datetime, validate_booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'staff', 'client', 'start_datetime', 'status']
        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'status': forms.Select(),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business

        if business:
            self.fields['service'].queryset = Service.objects.filter(
                business=business, is_active=True,
            )
            self.fields['staff'].queryset = BusinessMember.objects.filter(
                business=business, is_active=True,
            )
            self.fields['client'].queryset = Client.objects.filter(
                business=business,
            )

        if not self.instance.pk:
            self.fields['status'].initial = 'pending'

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        staff = cleaned_data.get('staff')
        start_datetime = cleaned_data.get('start_datetime')

        if not all([service, staff, start_datetime]):
            return cleaned_data

        end_datetime = calculate_end_datetime(start_datetime, service)
        cleaned_data['end_datetime'] = end_datetime

        if self.business:
            if service.business_id != self.business.pk:
                self.add_error('service', 'El servicio no pertenece a este negocio.')
            if staff.business_id != self.business.pk:
                self.add_error('staff', 'El personal no pertenece a este negocio.')
            client = cleaned_data.get('client')
            if client and client.business_id != self.business.pk:
                self.add_error('client', 'El cliente no pertenece a este negocio.')

        if self.errors:
            return cleaned_data

        try:
            validate_booking(
                staff=staff,
                service=service,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                exclude_booking=self.instance if self.instance.pk else None,
                is_new=not self.instance.pk,
            )
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.end_datetime = self.cleaned_data['end_datetime']
        if self.business and not instance.pk:
            instance.business = self.business
        if commit:
            instance.save()
        return instance

class BookingRequestForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        label='Servicio',
        widget=forms.Select(attrs={'class': 'w-full border border-light-gray rounded px-3 py-2 text-sm'}),
    )
    staff = forms.ModelChoiceField(
        queryset=BusinessMember.objects.none(),
        label='Personal',
        widget=forms.Select(attrs={'class': 'w-full border border-light-gray rounded px-3 py-2 text-sm'}),
    )
    start_datetime = forms.DateTimeField(
        label='Fecha y hora',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )
    notes = forms.CharField(
        label='Notas (opcional)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-light-gray rounded px-3 py-2 text-sm'}),
    )

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business
        if business:
            self.fields['service'].queryset = Service.objects.filter(business=business, is_active=True)
            self.fields['staff'].queryset = BusinessMember.objects.filter(business=business, is_active=True)

    def clean(self):
        cleaned = super().clean()
        service = cleaned.get('service')
        staff = cleaned.get('staff')
        start_datetime = cleaned.get('start_datetime')
        if not all([service, staff, start_datetime]):
            return cleaned
        end_datetime = calculate_end_datetime(start_datetime, service)
        cleaned['end_datetime'] = end_datetime
        try:
            validate_booking(
                staff=staff,
                service=service,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                is_new=True,
            )
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)
        return cleaned