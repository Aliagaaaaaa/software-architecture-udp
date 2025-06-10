# Service Command Summary

## Auth Service (`auth_service.py`)
**Class:** `AuthService`
**Methods:**
- `service_info`: Returns information about the authentication service.
- `service_register`: Registers a new user in the system.
- `service_login`: Authenticates a user and generates a JWT.
- `service_verify`: Verifies the validity of a JWT.
- `service_refresh`: Renews a valid JWT.
- `service_users`: Lists all registered users.
- `service_delete_user`: Deletes a user from the system.

## Comment Service (`comment_service.py`)
**Class:** `CommentService`
**Methods:**
- `service_create_comment`: Creates a new comment in a post (requiere autenticación).
- `service_get_comment`: Obtiene un comentario específico por ID (requiere autenticación).
- `service_list_comments`: Lista todos los comentarios de un post específico (requiere autenticación).
- `service_list_my_comments`: Lista los comentarios creados por el usuario autenticado.
- `service_update_comment`: Actualiza un comentario (solo el autor o moderador).
- `service_delete_comment`: Elimina un comentario (solo el autor o moderador).
- `service_admin_delete_comment`: Elimina cualquier comentario (solo moderadores).
- `service_info`: Returns information about the comment service.

## Event Service (`event_service.py`)
**Class:** `EventService`
**Methods:**
- `service_create_event`: Crea un nuevo evento (requiere autenticación).
- `service_get_event`: Obtiene un evento específico por ID (requiere autenticación).
- `service_list_events`: Lista todos los eventos disponibles (requiere autenticación).
- `service_list_my_events`: Lista los eventos creados por el usuario autenticado.
- `service_update_event`: Actualiza un evento (solo el creador o moderador).
- `service_delete_event`: Elimina un evento (solo el creador o moderador).
- `service_admin_delete_event`: Elimina cualquier evento (solo moderadores).
- `service_info`: Returns information about the event service.

## Forum Service (`forum_service.py`)
**Class:** `ForumService`
**Methods:**
- `service_create_forum`: Crea un nuevo foro (requiere autenticación).
- `service_get_forum`: Obtiene un foro específico por ID (requiere autenticación).
- `service_list_forums`: Lista todos los foros disponibles (requiere autenticación).
- `service_list_my_forums`: Lista los foros creados por el usuario autenticado.
- `service_update_forum`: Actualiza un foro (solo el creador o moderador).
- `service_delete_forum`: Elimina un foro (solo el creador o moderador).
- `service_admin_delete_forum`: Elimina cualquier foro (solo moderadores).
- `service_info`: Returns information about the forum service.

## Message Service (`message_service.py`)
**Class:** `MessageService`
**Methods:**
- `service_send_message`: Envía un mensaje a otro usuario (requiere autenticación).
- `service_get_message`: Obtiene un mensaje específico por ID (solo emisor, receptor o moderador).
- `service_list_sent_messages`: Lista los mensajes enviados por el usuario autenticado.
- `service_list_received_messages`: Lista los mensajes recibidos por el usuario autenticado.
- `service_list_conversation`: Lista la conversación entre el usuario autenticado y otro usuario.
- `service_delete_message`: Elimina un mensaje (solo el emisor o moderador).
- `service_admin_delete_message`: Elimina cualquier mensaje (solo moderadores).
- `service_info`: Returns information about the message service.

## Notification Service (`notification_service.py`)
**Class:** `NotificationService`
**Methods:**
- `service_list_notifications`: Lista las notificaciones del usuario autenticado.
- `service_get_unread_count`: Obtiene el número de notificaciones no leídas del usuario.
- `service_mark_as_read`: Marca una notificación específica como leída.
- `service_mark_all_as_read`: Marca todas las notificaciones del usuario como leídas.
- `service_get_notification`: Obtiene una notificación específica por ID.
- `service_delete_notification`: Elimina una notificación específica.
- `service_clear_all_notifications`: Elimina todas las notificaciones del usuario.
- `service_admin_list_all_notifications`: Lista todas las notificaciones del sistema (solo moderadores).
- `service_info`: Returns information about the notification service.

## Post Service (`post_service.py`)
**Class:** `PostService`
**Methods:**
- `service_create_post`: Crea un nuevo post en un foro (requiere autenticación).
- `service_get_post`: Obtiene un post específico por ID (requiere autenticación).
- `service_list_posts`: Lista todos los posts de un foro específico (requiere autenticación).
- `service_list_my_posts`: Lista los posts creados por el usuario autenticado.
- `service_update_post`: Actualiza un post (solo el autor o moderador).
- `service_delete_post`: Elimina un post (solo el autor o moderador).
- `service_admin_delete_post`: Elimina cualquier post (solo moderadores).
- `service_info`: Returns information about the post service.

## Profile Service (`prof_service.py`)
**Class:** `ProfileService`
**Methods:**
- `service_create_profile`: Crea un perfil para el usuario autenticado.
- `service_get_profile`: Obtiene el perfil del usuario autenticado.
- `service_update_profile`: Actualiza el perfil del usuario autenticado.
- `service_delete_profile`: Elimina el perfil del usuario autenticado.
- `service_list_profiles`: Lista todos los perfiles (solo moderadores).
- `service_admin_get_profile`: Obtiene el perfil de cualquier usuario (solo moderadores).
- `service_admin_delete_profile`: Elimina el perfil de cualquier usuario (solo moderadores).
- `service_info`: Returns information about the profile service.

## Report Service (`report_service.py`)
**Class:** `ReportService`
**Methods:**
- `service_create_report`: Crea un nuevo reporte de contenido (requiere autenticación).
- `service_get_report`: Obtiene un reporte específico por ID (solo moderadores).
- `service_list_reports`: Lista todos los reportes (solo moderadores).
- `service_list_my_reports`: Lista los reportes creados por el usuario autenticado.
- `service_update_report_status`: Actualiza el estado de un reporte (solo moderadores).
- `service_delete_report`: Elimina un reporte (solo el creador o moderador).
- `service_admin_delete_report`: Elimina cualquier reporte (solo moderadores).
- `service_info`: Returns information about the report service.
