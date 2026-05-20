# Modelos — CloudCO One

Documentación de la estructura completa de modelos para el SaaS de Gestión de Reservas y Presencia Digital.

---

## Apps existentes (ya creados)

### `apps.accounts` — Autenticación

| Modelo | Descripción |
|--------|-------------|
| **CustomUser** | Usuario personalizado. Login por email (sin username). Base para todo el sistema. |

**Campos actuales:**
```
email           — EmailField(unique=True)
first_name      — heredado de AbstractUser
last_name       — heredado de AbstractUser
is_staff        — heredado
is_active       — heredado
is_superuser    — heredado
date_joined     — heredado
last_login      — heredado
```

**Campos a añadir:**
```
phone           — CharField(max_length=20, blank=True)
avatar          — ImageField(upload_to='avatars/', blank=True)
google_id       — CharField(max_length=255, blank=True, unique=True) — para Google OAuth
```

---

### `apps.dashboard` — Dashboard del usuario

| Modelo | Descripción |
|--------|-------------|
| **SubscriptionPlan** | Planes de suscripción del SaaS (Free, Pro, Business). |
| **UserSettings** | Preferencias del usuario: notificaciones, API key, estado de suscripción. |

**SubscriptionPlan campos actuales:**
```
name            — CharField(max_length=100)
slug            — SlugField(unique=True)
description     — TextField()
price           — DecimalField(max_digits=10, decimal_places=2)
interval        — CharField(choices=[monthly, yearly])
features        — JSONField(default=list)
is_active       — BooleanField(default=True)
created_at      — DateTimeField
updated_at      — DateTimeField
```

**UserSettings campos actuales:**
```
user                    — OneToOneField(CustomUser)
notify_comments         — BooleanField
notify_updates          — BooleanField
notify_marketing        — BooleanField
subscription_plan       — ForeignKey(SubscriptionPlan)
subscription_status     — CharField(choices=[active, inactive, cancelled, trial])
subscription_start_date — DateTimeField(null, blank)
subscription_end_date   — DateTimeField(null, blank)
trial_end_date          — DateTimeField(null, blank)
created_at              — DateTimeField
updated_at              — DateTimeField
```

---

### `apps.subscriptions` — Integración Stripe

| Modelo | Descripción |
|--------|-------------|
| **StripeCustomer** | Vincula usuario con cliente de Stripe. |

**Campos actuales:**
```
user                     — OneToOneField(CustomUser)
stripe_customer_id       — CharField(max_length=255)
stripe_subscription_id   — CharField(max_length=255, blank)
subscription_status      — CharField(max_length=50, blank)
created_at               — DateTimeField
updated_at               — DateTimeField
```

---

## Apps nuevos (por crear)

### `apps.tenants` — Multi-tenant / Negocios

> **Fase 1 del plan.** Aislamiento lógico de datos por negocio.

| Modelo | Descripción |
|--------|-------------|
| **Business** | Entidad principal del tenant. Cada negocio registrado es un Business. |
| **BusinessSettings** | Configuración visual y operativa del negocio (colores, logo, horarios, etc). |
| **BusinessMember** | Relación usuario-negocio con roles (Owner, Admin, Staff). |

```python
class Business(models.Model):
    name            — CharField(max_length=200)
    slug            — SlugField(unique=True) — usado en URL: /app/{slug}/
    subdomain       — CharField(max_length=100, unique=True, blank) — opcional: {slug}.domain.com
    description     — TextField(blank)
    category        — CharField(choices=[barberia, salon, spa, clinica, gimnasio, restaurante, consultorio, tatuador, entrenador, otro])
    owner           — ForeignKey(CustomUser, related_name='owned_businesses')
    subscription_tier — CharField(choices=[free, pro, business], default='free')
    is_active       — BooleanField(default=True)
    created_at      — DateTimeField(auto_now_add)
    updated_at      — DateTimeField(auto_now)

class BusinessSettings(models.Model):
    business        — OneToOneField(Business, related_name='settings')
    logo            — ImageField(upload_to='businesses/logos/', blank)
    cover_image     — ImageField(upload_to='businesses/covers/', blank)
    primary_color   — CharField(max_length=7, default='#000000') — hex
    secondary_color — CharField(max_length=7, default='#666666')
    font_family     — CharField(max_length=100, blank)
    tagline         — CharField(max_length=200, blank)
    phone           — CharField(max_length=20, blank)
    email           — EmailField(blank)
    address         — CharField(max_length=300, blank)
    website         — URLField(blank)
    social_facebook — URLField(blank)
    social_instagram— URLField(blank)
    social_tiktok   — URLField(blank)
    working_hours   — JSONField(default=dict) — ej: {"mon": {"open": "09:00", "close": "18:00"}, ...}
    timezone        — CharField(max_length=50, default='America/Santo_Domingo')
    currency        — CharField(max_length=3, default='DOP')

class BusinessMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    business    — ForeignKey(Business, related_name='members', on_delete=CASCADE)
    user        — ForeignKey(CustomUser, related_name='business_memberships', on_delete=CASCADE)
    role        — CharField(choices=ROLE_CHOICES, default='staff')
    is_active   — BooleanField(default=True)
    joined_at   — DateTimeField(auto_now_add)

    class Meta:
        unique_together = ('business', 'user')
```

---

### `apps.bookings` — Sistema de Reservas

> **Fase 2 del plan.** Gestión completa de reservas y disponibilidad.

| Modelo | Descripción |
|--------|-------------|
| **Service** | Servicios que ofrece cada negocio (corte, tinte, consulta, etc). |
| **Staff** | Miembro del equipo que presta servicios. Vinculado a BusinessMember. |
| **StaffService** | Relación muchos-a-muchos entre Staff y Service con duración personalizada. |
| **AvailabilitySlot** | Bloques de disponibilidad del staff (horario semanal, excepciones). |
| **Booking** | Reserva realizada por un cliente. |
| **BookingBlock** | Bloqueo manual de horario (vacaciones, día libre, mantenimiento). |

```python
class Service(models.Model):
    business        — ForeignKey(Business, related_name='services', on_delete=CASCADE)
    name            — CharField(max_length=200)
    description     — TextField(blank)
    duration        — IntegerField() — en minutos
    price           — DecimalField(max_digits=10, decimal_places=2)
    is_active       — BooleanField(default=True)
    created_at      — DateTimeField(auto_now_add)
    updated_at      — DateTimeField(auto_now)

class Staff(models.Model):
    business        — ForeignKey(Business, related_name='staff', on_delete=CASCADE)
    member          — OneToOneField(BusinessMember, on_delete=CASCADE, related_name='staff_profile')
    bio             — TextField(blank)
    photo           — ImageField(upload_to='staff/', blank)
    is_active       — BooleanField(default=True)

class StaffService(models.Model):
    staff           — ForeignKey(Staff, related_name='service_assignments', on_delete=CASCADE)
    service         — ForeignKey(Service, on_delete=CASCADE)
    duration        — IntegerField() — override de duración del servicio
    is_active       — BooleanField(default=True)

class AvailabilitySlot(models.Model):
    staff           — ForeignKey(Staff, related_name='availability', on_delete=CASCADE)
    day_of_week     — IntegerField(choices=[0=Lun..6=Dom])
    start_time      — TimeField()
    end_time        — TimeField()
    is_active       — BooleanField(default=True)

class BookingBlock(models.Model):
    staff           — ForeignKey(Staff, related_name='blocks', on_delete=CASCADE)
    start_datetime  — DateTimeField()
    end_datetime    — DateTimeField()
    reason          — CharField(max_length=200, blank)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    business        — ForeignKey(Business, related_name='bookings', on_delete=CASCADE)
    service         — ForeignKey(Service, on_delete=PROTECT)
    staff           — ForeignKey(Staff, on_delete=PROTECT)
    client          — ForeignKey('clients.Client', on_delete=PROTECT, related_name='bookings')
    start_datetime  — DateTimeField()
    end_datetime    — DateTimeField()
    status          — CharField(choices=STATUS_CHOICES, default='pending')
    notes           — TextField(blank)
    client_notes    — TextField(blank)
    created_at      — DateTimeField(auto_now_add)
    updated_at      — DateTimeField(auto_now)
```

---

### `apps.clients` — Gestión de Clientes / CRM

> **Fase 4 del plan.** Centralización de clientes por negocio.

| Modelo | Descripción |
|--------|-------------|
| **Client** | Cliente final del negocio (quien reserva). |
| **ClientNote** | Notas internas sobre el cliente. |

```python
class Client(models.Model):
    business        — ForeignKey(Business, related_name='clients', on_delete=CASCADE)
    first_name      — CharField(max_length=100)
    last_name       — CharField(max_length=100, blank)
    email           — EmailField(blank)
    phone           — CharField(max_length=20, blank)
    notes           — TextField(blank)
    total_visits    — IntegerField(default=0)
    last_visit      — DateTimeField(null, blank)
    created_at      — DateTimeField(auto_now_add)
    updated_at      — DateTimeField(auto_now)

class ClientNote(models.Model):
    client          — ForeignKey(Client, related_name='notes', on_delete=CASCADE)
    author          — ForeignKey(CustomUser, on_delete=SET_NULL, null=True)
    content         — TextField()
    created_at      — DateTimeField(auto_now_add)
```

---

### `apps.notifications` — Notificaciones

> **Fase 5 del plan.** Sistema de alertas y recordatorios.

| Modelo | Descripción |
|--------|-------------|
| **NotificationTemplate** | Plantillas de email personalizables por negocio. |
| **NotificationLog** | Registro de notificaciones enviadas. |

```python
class NotificationTemplate(models.Model):
    TYPE_CHOICES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_reminder_24h', 'Booking Reminder 24h'),
        ('booking_reminder_1h', 'Booking Reminder 1h'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_completed', 'Booking Completed'),
    ]
    business        — ForeignKey(Business, related_name='notification_templates', on_delete=CASCADE)
    type            — CharField(choices=TYPE_CHOICES)
    subject         — CharField(max_length=300)
    body            — TextField()
    is_active       — BooleanField(default=True)
    created_at      — DateTimeField(auto_now_add)
    updated_at      — DateTimeField(auto_now)

class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    business        — ForeignKey(Business, on_delete=CASCADE)
    recipient_email — EmailField()
    template        — ForeignKey(NotificationTemplate, on_delete=SET_NULL, null=True)
    booking         — ForeignKey(Booking, on_delete=SET_NULL, null=True, blank)
    status          — CharField(choices=STATUS_CHOICES, default='pending')
    sent_at         — DateTimeField(null, blank)
    error_message   — TextField(blank)
    created_at      — DateTimeField(auto_now_add)
```

---

## Diagrama de relaciones

```
CustomUser
    ├── owned_businesses → Business (owner)
    ├── business_memberships → BusinessMember
    ├── settings → UserSettings
    └── stripe_customer → StripeCustomer

Business
    ├── settings → BusinessSettings
    ├── members → BusinessMember → Staff
    ├── services → Service → StaffService
    ├── clients → Client → ClientNote
    ├── bookings → Booking
    ├── notification_templates → NotificationTemplate
    └── notification_log → NotificationLog

Booking
    └── client → Client
    └── service → Service
    └── staff → Staff
```

---

## Notas de implementación

- **Aislamiento de datos:** Todos los modelos de negocio (Service, Staff, Client, Booking, etc) tienen `ForeignKey(Business)` con `on_delete=CASCADE`. El middleware de tenant filtra automáticamente por `business_id`.
- **Google OAuth:** Se añadirá `google_id` a `CustomUser` y se configurará `django-allauth` con el provider de Google.
- **Migraciones:** Crear las apps nuevas con `python manage.py startapp <app>` dentro de `apps/` y registrar en `INSTALLED_APPS`.
- **Campos comunes:** Todos los modelos nuevos incluyen `created_at` y `updated_at` para auditoría.
