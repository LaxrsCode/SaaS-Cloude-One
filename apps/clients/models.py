from django.conf import settings
from django.db import models
from apps.tenants.models import Business

class Client(models.Model):
    business        = models.ForeignKey(Business, related_name='clients', on_delete=models.CASCADE)
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profiles')
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100, blank=True)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=20, blank=True)
    notes           = models.TextField(blank=True)
    total_visits    = models.IntegerField(default=0)
    last_visit      = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()

    VISIT_STATUSES = ('confirmed', 'in_progress', 'completed')

    def booking_history(self):
        """Todas las citas del cliente, de la más reciente a la más antigua (ORM)."""
        return self.bookings.select_related('service', 'staff').order_by('-start_datetime')

    def booking_history_raw(self):
        """Historial de citas con SQL crudo (consulta de referencia)."""
        sql = '''
            SELECT b.*, s.name AS service_name, sm.email AS staff_email
            FROM bookings_booking b
            JOIN tenants_service s ON s.id = b.service_id
            JOIN tenants_businessmember sm ON sm.id = b.staff_id
            WHERE b.client_id = %s
            ORDER BY b.start_datetime DESC
        '''
        return list(self.bookings.raw(sql, [self.id]))

    def completed_bookings(self):
        return self.bookings.filter(status__in=self.VISIT_STATUSES)

    def count_bookings(self):
        return self.completed_bookings().count()

    def last_booking(self):
        return self.completed_bookings().order_by('-start_datetime').first()

    def refresh_visits(self):
        """Recalcula total_visits y last_visit a partir de las citas."""
        from django.db.models import Max
        qs = self.completed_bookings()
        self.total_visits = qs.count()
        self.last_visit = qs.aggregate(Max('start_datetime'))['start_datetime__max']
        self.save(update_fields=['total_visits', 'last_visit', 'updated_at'])


class ClientNote(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_notes')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='client_notes',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Nota de {self.client}'