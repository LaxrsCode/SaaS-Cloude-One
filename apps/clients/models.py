from django.db import models


class Client(models.Model):
    business = models.ForeignKey(
        'tenants.Business',
        on_delete=models.CASCADE,
        related_name='clients',
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True, verbose_name='Internal notes')
    total_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email or self.phone


class ClientNote(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='client_notes',
    )
    author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Client Note'
        verbose_name_plural = 'Client Notes'
        ordering = ['-created_at']

    def __str__(self):
        return f'Note on {self.client} by {self.author}'
