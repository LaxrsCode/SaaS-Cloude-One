# Registro de cambios — Módulo Clientes y Solicitudes de Reserva

## Resumen

Implementación del CRUD de clientes, historial de citas por cliente y flujo de
solicitud de reserva con trazabilidad de estado (reutilizando `Booking` en estado
`pending`).

---

## ✅ Hecho (implementado)

### App `clients` — CRUD + historial
- Modelo `Client` (nombre, email, teléfono, notas, `total_visits`, `last_visit`) y
  `ClientNote`. Se añadió `user` FK (nullable) para vincular el cliente del CRM con la
  cuenta que solicita.
- CRUD completo: `client_list`, `client_create`, `client_detail`, `client_edit`,
  `client_delete` con permisos (owner o miembro activo), búsqueda (`?q=`), y notas.
- `forms.py` (`ClientForm`), `urls.py` (app `clients`, 5 rutas con `business_slug` /
  `client_id`), `admin.py` (`Client` + `ClientNoteInline`).
- Incluido `path('clients/', ...)` en `core/urls.py`.

### Historial de citas por cliente (métodos y SQL)
En `Client`:
- `booking_history()` — ORM, citas ordenadas de más reciente a más antigua.
- `booking_history_raw()` — consulta SQL cruda con `JOIN` a `service` y `staff`.
- `refresh_visits()` — recalcula `total_visits` y `last_visit`.
- `count_bookings()`, `last_booking()`, `completed_bookings()`.

### Solicitud de reserva (trazabilidad de estado)
- `Booking` con campos de trazabilidad: `notes`, `status_changed_at`, `status_history`
  (JSON) y método `change_status()`.
- `BookingRequestForm` con validación de disponibilidad/solapamiento reutilizada.
- El **cliente autenticado** solicita en `/bookings/<slug>/request/` (crea/asocia `Client`
  y genera `Booking` en `pending`), con página de éxito.
- El **dueño/miembro** gestiona en `/bookings/<slug>/requests/`: ver solicitudes
  pendientes y acciones `accept` (→ `confirmed` + actualiza visitas), `reject`
  (→ `cancelled`) y `delete`.
- Notificaciones internas (`Notification`): a los dueños al crear la solicitud y al
  cliente al confirmar/rechazar.
- Rutas añadidas en `apps/bookings/urls.py`.

### Migraciones (ejecutadas)
- `python manage.py makemigrations clients bookings` generó:
  - `bookings/0002_booking_notes_booking_status_changed_at_and_more.py`
  - `clients/0002_client_user_clientnote.py`
- `python manage.py migrate` aplicado correctamente.
- `python manage.py check` → sin errores.

### Corrección aplicada durante migración
- Colisión `Client.notes` / reverse accessor de `ClientNote` resuelta cambiando el
  `related_name` de `ClientNote.client` a `client_notes` (y su uso en `views.py`).

---

## ❌ Faltante / pendiente

1. **Templates nuevas de solicitudes** (no se crearon por indicación):
   - `templates/bookings/request_form.html`
   - `templates/bookings/request_success.html`
   - `templates/bookings/requests_list.html`
   - Sin ellas, `/bookings/<slug>/request/` y `/bookings/<slug>/requests/` lanzan
     `TemplateDoesNotExist`.
2. **Breadcrumbs de templates de clients** (no se tocaron por indicación): en
   `client_list.html`, `client_detail.html` y `client_form.html` hay enlaces a
   `tenants:business_detail` (nombre **inexistente**) y el "Back to ..." de `client_list`
   → `NoReverseMatch` (500) al renderizar esas páginas.

---

## ⚠️ Sigue fallando / pendiente pre-existente (fuera de este alcance)

- `bookings/views.py` y `tenants/views.py` siguen renderizando templates inexistentes
  (`tenants/bookings_list.html`, `tenants/booking_form.html`, etc.) y redirigen a
  `tenants:bookings_list` (nombre no definido). Requiere revisar URLconf + templates.
- El sidebar y varias templates referencian `tenants:business_detail`,
  `bookings:service_list`, `bookings:staff_list`, `bookings:booking_list` con
  `business_slug`, que no coinciden con el URLconf actual de `bookings`/`tenants`.
- No se ejecutó aún `ruff check .` ni `python manage.py test`.

---

## Verificación (pasos sugeridos tras completar lo pendiente)

```bash
python manage.py check
ruff check .
python manage.py test
```
