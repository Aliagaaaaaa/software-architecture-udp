# Service Command Summary

## Auth Service (`auth_service.py`)
**Class:** `AuthService`
**Methods:**

- **`service_info`**
    - Description: Returns information about the authentication service.
    - Parameters: None
    - Example: `00014AUTH_info`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00236AUTH_OK{"service_name": "auth", "description": "Servicio de autenticación...", "version": "3.0.0", "methods": ["info", "register", "login", "verify", "refresh", "users", "delete_user"], "status": "running", "total_users": 0, "database": {"type": "HTTP Proxy to Cloudflare D1", "proxy_url": "DB_PROXY_URL", "connection_test": true}}
          ```
        - **Error Response Example:**
          ```
          00049AUTH_NK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

- **`service_register`**
    - Description: Registra un nuevo usuario en el sistema.
    - Parameters: `email: str`, `password: str`, `rol: str = "estudiante"`
    - Example: `00045AUTH_register USER_EMAIL USER_PASSWORD estudiante`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00120AUTH_OK{"success": true, "message": "Usuario USER_EMAIL registrado exitosamente", "user": {"email": "USER_EMAIL", "rol": "ROL_HERE"}, "token": "TOKEN_HERE"}
          ```
        - **Error Response Example:**
          ```
          00040AUTH_NK{"success": false, "message": "Email inválido"}
          ```

- **`service_login`**
    - Description: Autentica un usuario y genera un token JWT.
    - Parameters: `email: str`, `password: str`
    - Example: `00037AUTH_login USER_EMAIL USER_PASSWORD`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00104AUTH_OK{"success": true, "message": "Bienvenido USER_EMAIL", "user": {"email": "USER_EMAIL", "rol": "ROL_HERE"}, "token": "TOKEN_HERE"}
          ```
        - **Error Response Example:**
          ```
          00047AUTH_NK{"success": false, "message": "Credenciales inválidas"}
          ```

- **`service_verify`**
    - Description: Verifica la validez de un token JWT.
    - Parameters: `token: str`
    - Example: `00024AUTH_verify USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00147AUTH_OK{"success": true, "message": "Token válido", "payload": {"email": "USER_EMAIL", "rol": "ROL_HERE", "id_usuario": 1, "exp": 1678886400, "iat": 1678800000, "iss": "auth_service"}}
          ```
        - **Error Response Example:**
          ```
          00050AUTH_NK{"success": false, "message": "Token inválido o expirado"}
          ```

- **`service_refresh`**
    - Description: Renueva un token JWT válido.
    - Parameters: `token: str`
    - Example: `00025AUTH_refresh USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00118AUTH_OK{"success": true, "message": "Token renovado exitosamente", "user": {"email": "USER_EMAIL", "rol": "ROL_HERE"}, "token": "NEW_TOKEN_HERE"}
          ```
        - **Error Response Example:**
          ```
          00060AUTH_NK{"success": false, "message": "Token inválido o expirado para renovar"}
          ```

- **`service_users`**
    - Description: Lista todos los usuarios registrados.
    - Parameters: None
    - Example: `00015AUTH_users`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00131AUTH_OK{"success": true, "message": "Se encontraron N usuarios", "users": [{"email": "user1@example.com", "rol": "estudiante", "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP"}]}
          ```
        - **Error Response Example:**
          ```
          00063AUTH_NK{"success": false, "message": "Error obteniendo usuarios: ERROR_MESSAGE_HERE"}
          ```

- **`service_delete_user`**
    - Description: Elimina un usuario del sistema.
    - Parameters: `email: str`
    - Example: `00030AUTH_delete_user USER_EMAIL`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00066AUTH_OK{"success": true, "message": "Usuario USER_EMAIL eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00044AUTH_NK{"success": false, "message": "Usuario no encontrado"}
          ```

## Comment Service (`comment_service.py`)
**Class:** `CommentService`
**Methods:**

- **`service_create_comment`**
    - Description: Crea un nuevo comentario en un post (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_post`, `contenido`
    - Example: `00048COMMScreate_comment USER_TOKEN POST_ID 'Comment content here'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00137COMMSOK{"success": true, "message": "Comentario creado exitosamente", "comment": {"contenido": "CONTENT_HERE", "id_post": 1, "autor_id": 1, "autor_email": "USER_EMAIL", "fecha": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00070COMMSNK{"success": false, "message": "Parámetros requeridos: token id_post 'contenido'"}
          ```

- **`service_get_comment`**
    - Description: Obtiene un comentario específico por ID (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_comentario`
    - Example: `00033COMMSget_comment USER_TOKEN COMMENT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00202COMMSOK{"success": true, "message": "Comentario encontrado", "comment": {"id_comentario": 1, "contenido": "CONTENT_HERE", "fecha": "TIMESTAMP", "id_post": 1, "autor_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "autor_email": "USER_EMAIL", "post_contenido": "POST_CONTENT_PREVIEW"}}
          ```
        - **Error Response Example:**
          ```
          00049COMMSNK{"success": false, "message": "Comentario no encontrado"}
          ```

- **`service_list_comments`**
    - Description: Lista todos los comentarios de un post específico (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_post`
    - Example: `00033COMMSlist_comments USER_TOKEN POST_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00268COMMSOK{"success": true, "message": "Se encontraron N comentarios en el post", "post": {"id_post": 1, "contenido": "POST_CONTENT"}, "post_preview": "POST_CONTENT_PREVIEW...", "comments": [ {"id_comentario": 1, "contenido": "COMMENT_CONTENT", "fecha": "TIMESTAMP", "id_post": 1, "autor_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "autor_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00060COMMSNK{"success": false, "message": "El post especificado no existe"}
          ```

- **`service_list_my_comments`**
    - Description: Lista los comentarios creados por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00028COMMSlist_my_comments USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00215COMMSOK{"success": true, "message": "Tienes N comentarios creados", "comments": [ {"id_comentario": 1, "contenido": "COMMENT_CONTENT", "fecha": "TIMESTAMP", "id_post": 1, "autor_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "autor_email": "USER_EMAIL", "post_preview": "POST_PREVIEW..."} ]}
          ```
        - **Error Response Example:**
          ```
          00072COMMSNK{"success": false, "message": "Error obteniendo tus comentarios: ERROR_MESSAGE_HERE"}
          ```

- **`service_update_comment`**
    - Description: Actualiza un comentario (solo el autor o moderador).
    - Parameters (from `params_str`): `token`, `id_comentario`, `contenido`
    - Example: `00052COMMSupdate_comment USER_TOKEN COMMENT_ID 'Updated content here'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00128COMMSOK{"success": true, "message": "Comentario actualizado exitosamente", "comment": {"id_comentario": 1, "contenido": "UPDATED_CONTENT", "updated_at": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00076COMMSNK{"success": false, "message": "No tienes permisos para actualizar este comentario"}
          ```

- **`service_delete_comment`**
    - Description: Elimina un comentario (solo el autor o moderador).
    - Parameters (from `params_str`): `token`, `id_comentario`
    - Example: `00036COMMSdelete_comment USER_TOKEN COMMENT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00060COMMSOK{"success": true, "message": "Comentario eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00075COMMSNK{"success": false, "message": "No tienes permisos para eliminar este comentario"}
          ```

- **`service_admin_delete_comment`**
    - Description: Elimina cualquier comentario (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_comentario`
    - Example: `00042COMMSadmin_delete_comment USER_TOKEN COMMENT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00074COMMSOK{"success": true, "message": "Comentario eliminado exitosamente por moderador"}
          ```
        - **Error Response Example:**
          ```
          00065COMMSNK{"success": false, "message": "Solo los moderadores pueden usar este método"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the comment service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011COMMSinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00136COMMSOK{"service": "comm", "description": "Servicio de gestión de comentarios en posts", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049COMMSNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

## Event Service (`event_service.py`)
**Class:** `EventService`
**Methods:**

- **`service_create_event`**
    - Description: Crea un nuevo evento (requiere autenticación).
    - Parameters (from `params_str`): `token`, `nombre`, `descripcion`, `fecha`
    - Example: `00062EVNTScreate_event USER_TOKEN 'Event Name' 'Event Description' 2024-12-31`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00157EVNTSOK{"success": true, "message": "Evento creado exitosamente", "event": {"nombre": "EVENT_NAME", "descripcion": "EVENT_DESC", "fecha": "YYYY-MM-DD", "creador_id": 1, "creador_email": "USER_EMAIL", "created_at": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00066EVNTSNK{"success": false, "message": "La fecha del evento no puede ser en el pasado"}
          ```

- **`service_get_event`**
    - Description: Obtiene un evento específico por ID (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_evento`
    - Example: `00031EVNTSget_event USER_TOKEN EVENT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00187EVNTSOK{"success": true, "message": "Evento encontrado", "event": {"id_evento": 1, "nombre": "EVENT_NAME", "descripcion": "EVENT_DESC", "fecha": "YYYY-MM-DD", "creador_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "creador_email": "USER_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00044EVNTSNK{"success": false, "message": "Evento no encontrado"}
          ```

- **`service_list_events`**
    - Description: Lista todos los eventos disponibles (requiere autenticación).
    - Parameters (from `params_str`): `token`
    - Example: `00026EVNTSlist_events USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00205EVNTSOK{"success": true, "message": "Se encontraron N eventos", "events": [ {"id_evento": 1, "nombre": "EVENT_NAME", "descripcion": "EVENT_DESC", "fecha": "YYYY-MM-DD", "creador_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "creador_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00061EVNTSNK{"success": false, "message": "Error obteniendo eventos: ERROR_MESSAGE_HERE"}
          ```

- **`service_list_my_events`**
    - Description: Lista los eventos creados por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00030EVNTSlist_my_events USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00204EVNTSOK{"success": true, "message": "Tienes N eventos creados", "events": [ {"id_evento": 1, "nombre": "EVENT_NAME", "descripcion": "EVENT_DESC", "fecha": "YYYY-MM-DD", "creador_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "creador_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00039EVNTSNK{"success": false, "message": "Token inválido"}
          ```

- **`service_update_event`**
    - Description: Actualiza un evento (solo el creador o moderador).
    - Parameters (from `params_str`): `token`, `id_evento`, `nombre`, `descripcion`, `fecha`
    - Example: `00071EVNTSupdate_event USER_TOKEN EVENT_ID 'New Name' 'New Description' 2025-01-01`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00147EVNTSOK{"success": true, "message": "Evento actualizado exitosamente", "event": {"id_evento": 1, "nombre": "NEW_NAME", "descripcion": "NEW_DESC", "fecha": "YYYY-MM-DD", "updated_at": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00072EVNTSNK{"success": false, "message": "No tienes permisos para actualizar este evento"}
          ```

- **`service_delete_event`**
    - Description: Elimina un evento (solo el creador o moderador).
    - Parameters (from `params_str`): `token`, `id_evento`
    - Example: `00033EVNTSdelete_event USER_TOKEN EVENT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00063EVNTSOK{"success": true, "message": "Evento 'EVENT_NAME' eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00071EVNTSNK{"success": false, "message": "No tienes permisos para eliminar este evento"}
          ```

- **`service_admin_delete_event`**
    - Description: Elimina cualquier evento (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_evento`
    - Example: `00039EVNTSadmin_delete_event USER_TOKEN EVENT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00079EVNTSOK{"success": true, "message": "Evento 'EVENT_NAME' eliminado exitosamente por moderador"}
          ```
        - **Error Response Example:**
          ```
          00063EVNTSNK{"success": false, "message": "Solo los moderadores pueden usar este método"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the event service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011EVNTSinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00124EVNTSOK{"service": "event", "description": "Servicio de gestión de eventos", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049EVNTSNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

## Forum Service (`forum_service.py`)
**Class:** `ForumService`
**Methods:**

- **`service_create_forum`**
    - Description: Crea un nuevo foro (requiere autenticación).
    - Parameters (from `params_str`): `token`, `titulo`, `categoria`
    - Example: `00048FORUMcreate_forum USER_TOKEN 'Forum Title' 'Category'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00117FORUMOK{"success": true, "message": "Foro 'FORUM_TITLE' creado exitosamente", "debug": {"titulo": "FORUM_TITLE", "categoria": "CATEGORY", "creador_id": 1}}
          ```
        - **Error Response Example:**
          ```
          00065FORUMNK{"success": false, "message": "El título no puede exceder 200 caracteres"}
          ```

- **`service_get_forum`**
    - Description: Obtiene un foro específico por ID (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_foro`
    - Example: `00031FORUMget_forum USER_TOKEN FORUM_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00170FORUMOK{"success": true, "message": "Foro encontrado", "forum": {"id_foro": 1, "titulo": "FORUM_TITLE", "categoria": "CATEGORY", "creador_id": 1, "creador_email": "USER_EMAIL", "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00043FORUMNK{"success": false, "message": "Foro no encontrado"}
          ```

- **`service_list_forums`**
    - Description: Lista todos los foros disponibles (requiere autenticación).
    - Parameters (from `params_str`): `token`
    - Example: `00027FORUMlist_forums USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00188FORUMOK{"success": true, "message": "Se encontraron N foros", "forums": [ {"id_foro": 1, "titulo": "FORUM_TITLE", "categoria": "CATEGORY", "creador_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "creador_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00060FORUMNK{"success": false, "message": "Error obteniendo foros: ERROR_MESSAGE_HERE"}
          ```

- **`service_list_my_forums`**
    - Description: Lista los foros creados por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00031FORUMlist_my_forums USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00187FORUMOK{"success": true, "message": "Tienes N foros creados", "forums": [ {"id_foro": 1, "titulo": "FORUM_TITLE", "categoria": "CATEGORY", "creador_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "creador_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00039FORUMNK{"success": false, "message": "Token inválido"}
          ```

- **`service_update_forum`**
    - Description: Actualiza un foro (solo el creador o moderador).
    - Parameters (from `params_str`): `token`, `id_foro`, `titulo`, `categoria`
    - Example: `00057FORUMupdate_forum USER_TOKEN FORUM_ID 'New Title' 'New Category'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00187FORUMOK{"success": true, "message": "Foro actualizado exitosamente", "forum": {"id_foro": 1, "titulo": "NEW_TITLE", "categoria": "NEW_CATEGORY", "creador_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "creador_email": "USER_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00071FORUMNK{"success": false, "message": "No tienes permisos para actualizar este foro"}
          ```

- **`service_delete_forum`**
    - Description: Elimina un foro (solo el creador o moderador).
    - Parameters (from `params_str`): `token`, `id_foro`
    - Example: `00033FORUMdelete_forum USER_TOKEN FORUM_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00062FORUMOK{"success": true, "message": "Foro 'FORUM_TITLE' eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00070FORUMNK{"success": false, "message": "No tienes permisos para eliminar este foro"}
          ```

- **`service_admin_delete_forum`**
    - Description: Elimina cualquier foro (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_foro`
    - Example: `00039FORUMadmin_delete_forum USER_TOKEN FORUM_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00078FORUMOK{"success": true, "message": "Foro 'FORUM_TITLE' eliminado exitosamente por moderador"}
          ```
        - **Error Response Example:**
          ```
          00063FORUMNK{"success": false, "message": "Solo los moderadores pueden usar este método"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the forum service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011FORUMinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00138FORUMOK{"service": "forum", "description": "Servicio de gestión de foros de discusión", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049FORUMNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

## Message Service (`message_service.py`)
**Class:** `MessageService` (`service_name="msg"`)
**Methods:**

- **`service_send_message`**
    - Description: Envía un mensaje a otro usuario (requiere autenticación).
    - Parameters (from `params_str`): `token`, `email_receptor`, `contenido`
    - Example: `00057MSGESsend_message USER_TOKEN RECIPIENT_EMAIL 'Message content'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00154MSGESOK{"success": true, "message": "Mensaje enviado exitosamente", "message_data": {"contenido": "MESSAGE_CONTENT", "fecha": "TIMESTAMP", "emisor_email": "SENDER_EMAIL", "receptor_email": "RECIPIENT_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00077MSGESNK{"success": false, "message": "Usuario receptor 'RECIPIENT_EMAIL' no encontrado"}
          ```

- **`service_get_message`**
    - Description: Obtiene un mensaje específico por ID (solo emisor, receptor o moderador).
    - Parameters (from `params_str`): `token`, `id_mensaje`
    - Example: `00033MSGESget_message USER_TOKEN MESSAGE_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00189MSGESOK{"success": true, "message": "Mensaje encontrado", "message_data": {"id_mensaje": 1, "contenido": "MESSAGE_CONTENT", "fecha": "TIMESTAMP", "emisor_id": 1, "receptor_id": 2, "emisor_email": "SENDER_EMAIL", "receptor_email": "RECIPIENT_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00069MSGESNK{"success": false, "message": "No tienes permisos para ver este mensaje"}
          ```

- **`service_list_sent_messages`**
    - Description: Lista los mensajes enviados por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00032MSGESlist_sent_messages USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00203MSGESOK{"success": true, "message": "Tienes N mensajes enviados", "messages": [ {"id_mensaje": 1, "contenido": "MESSAGE_CONTENT", "fecha": "TIMESTAMP", "emisor_id": 1, "receptor_id": 2, "emisor_email": "USER_EMAIL", "receptor_email": "RECIPIENT_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00072MSGESNK{"success": false, "message": "Error obteniendo mensajes enviados: ERROR_MESSAGE_HERE"}
          ```

- **`service_list_received_messages`**
    - Description: Lista los mensajes recibidos por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00036MSGESlist_received_messages USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00205MSGESOK{"success": true, "message": "Tienes N mensajes recibidos", "messages": [ {"id_mensaje": 1, "contenido": "MESSAGE_CONTENT", "fecha": "TIMESTAMP", "emisor_id": 2, "receptor_id": 1, "emisor_email": "SENDER_EMAIL", "receptor_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00074MSGESNK{"success": false, "message": "Error obteniendo mensajes recibidos: ERROR_MESSAGE_HERE"}
          ```

- **`service_list_conversation`**
    - Description: Lista la conversación entre el usuario autenticado y otro usuario.
    - Parameters (from `params_str`): `token`, `email_otro_usuario`
    - Example: `00045MSGESlist_conversation USER_TOKEN OTHER_USER_EMAIL`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00243MSGESOK{"success": true, "message": "Conversación con OTHER_USER_EMAIL (N mensajes)", "messages": [ {"id_mensaje": 1, "contenido": "MESSAGE_CONTENT", "fecha": "TIMESTAMP", "emisor_id": 1, "receptor_id": 2, "emisor_email": "USER_EMAIL", "receptor_email": "OTHER_USER_EMAIL", "is_sent": true} ], "other_user": "OTHER_USER_EMAIL"}
          ```
        - **Error Response Example:**
          ```
          00070MSGESNK{"success": false, "message": "Usuario 'OTHER_USER_EMAIL' no encontrado"}
          ```

- **`service_delete_message`**
    - Description: Elimina un mensaje (solo el emisor o moderador).
    - Parameters (from `params_str`): `token`, `id_mensaje`
    - Example: `00036MSGESdelete_message USER_TOKEN MESSAGE_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00058MSGESOK{"success": true, "message": "Mensaje eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00071MSGESNK{"success": false, "message": "No tienes permisos para eliminar este mensaje"}
          ```

- **`service_admin_delete_message`**
    - Description: Elimina cualquier mensaje (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_mensaje`
    - Example: `00042MSGESadmin_delete_message USER_TOKEN MESSAGE_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00070MSGESOK{"success": true, "message": "Mensaje eliminado exitosamente por moderador"}
          ```
        - **Error Response Example:**
          ```
          00063MSGESNK{"success": false, "message": "Solo los moderadores pueden usar este método"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the message service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011MSGESinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00120MSGESOK{"service": "msg", "description": "Servicio de gestión de mensajes", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049MSGESNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

## Notification Service (`notification_service.py`)
**Class:** `NotificationService`
**Methods:**

- **`service_list_notifications`**
    - Description: Lista las notificaciones del usuario autenticado.
    - Parameters (from `params_str`): `token`, `[limit]` (optional)
    - Example: `00036NOTIFlist_notifications USER_TOKEN 50`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00205NOTIFOK{"success": true, "message": "Tienes N notificaciones", "notifications": [ {"id_notificacion": 1, "usuario_id": 1, "titulo": "NOTIF_TITLE", "mensaje": "NOTIF_MESSAGE", "tipo": "TIPO_NOTIF", "referencia_id": 123, "leido": false, "fecha": "TIMESTAMP"} ]}
          ```
        - **Error Response Example:**
          ```
          00039NOTIFNK{"success": false, "message": "Token inválido"}
          ```

- **`service_get_unread_count`**
    - Description: Obtiene el número de notificaciones no leídas del usuario.
    - Parameters (from `params_str`): `token`
    - Example: `00032NOTIFget_unread_count USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00087NOTIFOK{"success": true, "message": "Tienes N notificaciones no leídas", "unread_count": 0}
          ```
        - **Error Response Example:**
          ```
          00039NOTIFNK{"success": false, "message": "Token inválido"}
          ```

- **`service_mark_as_read`**
    - Description: Marca una notificación específica como leída.
    - Parameters (from `params_str`): `token`, `id_notificacion`
    - Example: `00038NOTIFmark_as_read USER_TOKEN NOTIFICATION_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00056NOTIFOK{"success": true, "message": "Notificación marcada como leída"}
          ```
        - **Error Response Example:**
          ```
          00078NOTIFNK{"success": false, "message": "No tienes permisos para modificar esta notificación"}
          ```

- **`service_mark_all_as_read`**
    - Description: Marca todas las notificaciones del usuario como leídas.
    - Parameters (from `params_str`): `token`
    - Example: `00034NOTIFmark_all_as_read USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00064NOTIFOK{"success": true, "message": "Todas las notificaciones marcadas como leídas"}
          ```
        - **Error Response Example:**
          ```
          00039NOTIFNK{"success": false, "message": "Token inválido"}
          ```

- **`service_get_notification`**
    - Description: Obtiene una notificación específica por ID.
    - Parameters (from `params_str`): `token`, `id_notificacion`
    - Example: `00040NOTIFget_notification USER_TOKEN NOTIFICATION_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00189NOTIFOK{"success": true, "message": "Notificación encontrada", "notification": {"id_notificacion": 1, "usuario_id": 1, "titulo": "NOTIF_TITLE", "mensaje": "NOTIF_MESSAGE", "tipo": "TIPO_NOTIF", "referencia_id": 123, "leido": false, "fecha": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00051NOTIFNK{"success": false, "message": "Notificación no encontrada"}
          ```

- **`service_delete_notification`**
    - Description: Elimina una notificación específica.
    - Parameters (from `params_str`): `token`, `id_notificacion`
    - Example: `00043NOTIFdelete_notification USER_TOKEN NOTIFICATION_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00061NOTIFOK{"success": true, "message": "Notificación eliminada exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00077NOTIFNK{"success": false, "message": "No tienes permisos para eliminar esta notificación"}
          ```

- **`service_clear_all_notifications`**
    - Description: Elimina todas las notificaciones del usuario.
    - Parameters (from `params_str`): `token`
    - Example: `00041NOTIFclear_all_notifications USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00071NOTIFOK{"success": true, "message": "Todas las notificaciones eliminadas exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00039NOTIFNK{"success": false, "message": "Token inválido"}
          ```

- **`service_admin_list_all_notifications`**
    - Description: Lista todas las notificaciones del sistema (solo moderadores).
    - Parameters (from `params_str`): `token`, `[limit]` (optional)
    - Example: `00048NOTIFadmin_list_all_notifications USER_TOKEN 100`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00230NOTIFOK{"success": true, "message": "Se encontraron N notificaciones en el sistema", "notifications": [ {"id_notificacion": 1, "usuario_id": 1, "titulo": "NOTIF_TITLE", "mensaje": "NOTIF_MESSAGE", "tipo": "TIPO_NOTIF", "referencia_id": 123, "leido": false, "fecha": "TIMESTAMP", "usuario_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00084NOTIFNK{"success": false, "message": "Solo los moderadores pueden ver todas las notificaciones"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the notification service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011NOTIFinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00139NOTIFOK{"service": "notif", "description": "Servicio de gestión de notificaciones", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049NOTIFNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

## Post Service (`post_service.py`)
**Class:** `PostService`
**Methods:**

- **`service_create_post`**
    - Description: Crea un nuevo post en un foro (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_foro`, `contenido`
    - Example: `00045POSTScreate_post USER_TOKEN FORUM_ID 'Post content here'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00130POSTSOK{"success": true, "message": "Post creado exitosamente", "post": {"contenido": "POST_CONTENT", "id_foro": 1, "autor_id": 1, "autor_email": "USER_EMAIL", "fecha": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00057POSTSNK{"success": false, "message": "El foro especificado no existe"}
          ```

- **`service_get_post`**
    - Description: Obtiene un post específico por ID (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_post`
    - Example: `00029POSTSget_post USER_TOKEN POST_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00190POSTSOK{"success": true, "message": "Post encontrado", "post": {"id_post": 1, "contenido": "POST_CONTENT", "fecha": "TIMESTAMP", "id_foro": 1, "autor_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "autor_email": "USER_EMAIL", "foro_titulo": "FORUM_TITLE"}}
          ```
        - **Error Response Example:**
          ```
          00041POSTSNK{"success": false, "message": "Post no encontrado"}
          ```

- **`service_list_posts`**
    - Description: Lista todos los posts de un foro específico (requiere autenticación).
    - Parameters (from `params_str`): `token`, `id_foro`
    - Example: `00031POSTSlist_posts USER_TOKEN FORUM_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00251POSTSOK{"success": true, "message": "Se encontraron N posts en el foro 'FORUM_TITLE'", "foro": {"id_foro": 1, "titulo": "FORUM_TITLE"}, "posts": [ {"id_post": 1, "contenido": "POST_CONTENT", "fecha": "TIMESTAMP", "id_foro": 1, "autor_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "autor_email": "USER_EMAIL"} ]}
          ```
        - **Error Response Example:**
          ```
          00057POSTSNK{"success": false, "message": "El foro especificado no existe"}
          ```

- **`service_list_my_posts`**
    - Description: Lista los posts creados por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00029POSTSlist_my_posts USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00207POSTSOK{"success": true, "message": "Tienes N posts creados", "posts": [ {"id_post": 1, "contenido": "POST_CONTENT", "fecha": "TIMESTAMP", "id_foro": 1, "autor_id": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "autor_email": "USER_EMAIL", "foro_titulo": "FORUM_TITLE"} ]}
          ```
        - **Error Response Example:**
          ```
          00039POSTSNK{"success": false, "message": "Token inválido"}
          ```

- **`service_update_post`**
    - Description: Actualiza un post (solo el autor o moderador).
    - Parameters (from `params_str`): `token`, `id_post`, `contenido`
    - Example: `00049POSTSupdate_post USER_TOKEN POST_ID 'Updated post content'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00117POSTSOK{"success": true, "message": "Post actualizado exitosamente", "post": {"id_post": 1, "contenido": "UPDATED_CONTENT", "updated_at": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00069POSTSNK{"success": false, "message": "No tienes permisos para actualizar este post"}
          ```

- **`service_delete_post`**
    - Description: Elimina un post (solo el autor o moderador).
    - Parameters (from `params_str`): `token`, `id_post`
    - Example: `00031POSTSdelete_post USER_TOKEN POST_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00053POSTSOK{"success": true, "message": "Post eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00068POSTSNK{"success": false, "message": "No tienes permisos para eliminar este post"}
          ```

- **`service_admin_delete_post`**
    - Description: Elimina cualquier post (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_post`
    - Example: `00037POSTSadmin_delete_post USER_TOKEN POST_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00065POSTSOK{"success": true, "message": "Post eliminado exitosamente por moderador"}
          ```
        - **Error Response Example:**
          ```
          00063POSTSNK{"success": false, "message": "Solo los moderadores pueden usar este método"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the post service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011POSTSinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00141POSTSOK{"service": "post", "description": "Servicio de gestión de posts en foros de discusión", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049POSTSNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

## Profile Service (`prof_service.py`)
**Class:** `ProfileService`
**Methods:**

- **`service_info`**
    - Description: Returns information about the profile service.
    - Parameters: None
    - Example: `00013PROFSinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00260PROFSOK{"service_name": "prof", "description": "Servicio de gestión de perfiles de usuario...", "version": "3.0.0", "methods": ["list_of_methods"], "status": "running", "total_profiles": 0, "database": {"type": "HTTP Proxy to Cloudflare D1", "proxy_url": "DB_PROXY_URL", "connection_test": true}, "authentication": {"required": true, "jwt_algorithm": "HS256", "permissions": {"estudiante": "Solo gestión de su propio perfil", "moderador": "Gestión de todos los perfiles + métodos admin"}}}
          ```
        - **Error Response Example:**
          ```
          00049PROFSNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```

- **`service_create_profile`**
    - Description: Crea un perfil para el usuario autenticado.
    - Parameters: `token: str`, `avatar: str = ""`, `biografia: str = ""`
    - Example: `00054PROFScreate_profile USER_TOKEN 'avatar_url' 'User biography'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00173PROFSOK{"success": true, "message": "Perfil creado exitosamente para USER_EMAIL", "profile": {"id_perfil": 1, "avatar": "AVATAR_URL", "biografia": "BIO_HERE", "id_usuario": 1, "created_at": "TIMESTAMP", "updated_at": null, "email": "USER_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00084PROFSNK{"success": false, "message": "El usuario ya tiene un perfil. Use update_profile para modificarlo."}
          ```

- **`service_get_profile`**
    - Description: Obtiene el perfil del usuario autenticado.
    - Parameters: `token: str`
    - Example: `00026PROFSget_profile USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00176PROFSOK{"success": true, "message": "Perfil obtenido para USER_EMAIL", "profile": {"id_perfil": 1, "avatar": "AVATAR_URL", "biografia": "BIO_HERE", "id_usuario": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "email": "USER_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00090PROFSNK{"success": false, "message": "No se encontró perfil para este usuario. Use create_profile para crear uno."}
          ```

- **`service_update_profile`**
    - Description: Actualiza el perfil del usuario autenticado.
    - Parameters: `token: str`, `avatar: str = ""`, `biografia: str = ""`
    - Example: `00058PROFSupdate_profile USER_TOKEN 'new_avatar_url' 'New biography'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00180PROFSOK{"success": true, "message": "Perfil actualizado exitosamente para USER_EMAIL", "profile": {"id_perfil": 1, "avatar": "NEW_AVATAR_URL", "biografia": "NEW_BIO", "id_usuario": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "email": "USER_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00090PROFSNK{"success": false, "message": "Debe proporcionar al menos un campo para actualizar (avatar o biografía)"}
          ```

- **`service_delete_profile`**
    - Description: Elimina el perfil del usuario autenticado.
    - Parameters: `token: str`
    - Example: `00029PROFSdelete_profile USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00067PROFSOK{"success": true, "message": "Perfil eliminado exitosamente para USER_EMAIL"}
          ```
        - **Error Response Example:**
          ```
          00056PROFSNK{"success": false, "message": "No se encontró perfil para eliminar"}
          ```

- **`service_list_profiles`**
    - Description: Lista todos los perfiles (solo moderadores).
    - Parameters: `token: str`
    - Example: `00028PROFSlist_profiles USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00197PROFSOK{"success": true, "message": "Se encontraron N perfiles", "profiles": [ {"id_perfil": 1, "avatar": "AVATAR_URL", "biografia": "BIO_HERE", "id_usuario": 1, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "email": "USER_EMAIL", "rol": "ROL_HERE"} ]}
          ```
        - **Error Response Example:**
          ```
          00085PROFSNK{"success": false, "message": "Acceso denegado. Solo los moderadores pueden listar todos los perfiles."}
          ```

- **`service_admin_get_profile`**
    - Description: Obtiene el perfil de cualquier usuario (solo moderadores).
    - Parameters: `token: str`, `email: str`
    - Example: `00046PROFSadmin_get_profile MOD_TOKEN TARGET_USER_EMAIL`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00185PROFSOK{"success": true, "message": "Perfil obtenido para TARGET_USER_EMAIL", "profile": {"id_perfil": 2, "avatar": "AVATAR_URL", "biografia": "BIO_HERE", "id_usuario": 2, "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP", "email": "TARGET_USER_EMAIL"}}
          ```
        - **Error Response Example:**
          ```
          00062PROFSNK{"success": false, "message": "Usuario no encontrado: TARGET_USER_EMAIL"}
          ```

- **`service_admin_delete_profile`**
    - Description: Elimina el perfil de cualquier usuario (solo moderadores).
    - Parameters: `token: str`, `email: str`
    - Example: `00049PROFSadmin_delete_profile MOD_TOKEN TARGET_USER_EMAIL`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00075PROFSOK{"success": true, "message": "Perfil eliminado exitosamente para TARGET_USER_EMAIL"}
          ```
        - **Error Response Example:**
          ```
          00062PROFSNK{"success": false, "message": "Usuario no encontrado: TARGET_USER_EMAIL"}
          ```

## Report Service (`report_service.py`)
**Class:** `ReportService`
**Methods:**

- **`service_create_report`**
    - Description: Crea un nuevo reporte de contenido (requiere autenticación).
    - Parameters (from `params_str`): `token`, `contenido_id`, `tipo_contenido`, `razon`
    - Example: `00064REPORcreate_report USER_TOKEN CONTENT_ID post 'Reason for report'`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00176REPOROK{"success": true, "message": "Reporte creado exitosamente", "report": {"contenido_id": 1, "tipo_contenido": "post", "razon": "REASON_HERE", "fecha": "TIMESTAMP", "reportado_por": 1, "reportador_email": "USER_EMAIL", "estado": "pendiente"}}
          ```
        - **Error Response Example:**
          ```
          00069REPORNK{"success": false, "message": "Ya has reportado este contenido anteriormente"}
          ```

- **`service_get_report`**
    - Description: Obtiene un reporte específico por ID (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_reporte`
    - Example: `00033REPORget_report USER_TOKEN REPORT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00236REPOROK{"success": true, "message": "Reporte encontrado", "report": {"id_reporte": 1, "contenido_id": 1, "tipo_contenido": "post", "razon": "REASON_HERE", "fecha": "TIMESTAMP", "reportado_por": 1, "estado": "pendiente", "revisado_por": null, "fecha_revision": null, "reportador_email": "USER_EMAIL", "revisor_email": "No revisado"}}
          ```
        - **Error Response Example:**
          ```
          00046REPORNK{"success": false, "message": "Reporte no encontrado"}
          ```

- **`service_list_reports`**
    - Description: Lista todos los reportes (solo moderadores).
    - Parameters (from `params_str`): `token`
    - Example: `00028REPORlist_reports USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00254REPOROK{"success": true, "message": "Se encontraron N reportes", "reports": [ {"id_reporte": 1, "contenido_id": 1, "tipo_contenido": "post", "razon": "REASON_HERE", "fecha": "TIMESTAMP", "reportado_por": 1, "estado": "pendiente", "revisado_por": null, "fecha_revision": null, "reportador_email": "USER_EMAIL", "revisor_email": "No revisado"} ]}
          ```
        - **Error Response Example:**
          ```
          00076REPORNK{"success": false, "message": "Solo los moderadores pueden ver todos los reportes"}
          ```

- **`service_list_my_reports`**
    - Description: Lista los reportes creados por el usuario autenticado.
    - Parameters (from `params_str`): `token`
    - Example: `00032REPORlist_my_reports USER_TOKEN`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00253REPOROK{"success": true, "message": "Tienes N reportes creados", "reports": [ {"id_reporte": 1, "contenido_id": 1, "tipo_contenido": "post", "razon": "REASON_HERE", "fecha": "TIMESTAMP", "reportado_por": 1, "estado": "pendiente", "revisado_por": null, "fecha_revision": null, "reportador_email": "USER_EMAIL", "revisor_email": "No revisado"} ]}
          ```
        - **Error Response Example:**
          ```
          00039REPORNK{"success": false, "message": "Token inválido"}
          ```

- **`service_update_report_status`**
    - Description: Actualiza el estado de un reporte (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_reporte`, `estado`
    - Example: `00053REPORupdate_report_status USER_TOKEN REPORT_ID resolved`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00168REPOROK{"success": true, "message": "Estado del reporte actualizado a 'resolved'", "report": {"id_reporte": 1, "estado": "resolved", "revisado_por": 2, "revisor_email": "MODERATOR_EMAIL", "fecha_revision": "TIMESTAMP"}}
          ```
        - **Error Response Example:**
          ```
          00088REPORNK{"success": false, "message": "Estado debe ser uno de: pendiente, revisado, resuelto, descartado"}
          ```

- **`service_delete_report`**
    - Description: Elimina un reporte (solo el creador o moderador).
    - Parameters (from `params_str`): `token`, `id_reporte`
    - Example: `00036REPORdelete_report USER_TOKEN REPORT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00058REPOROK{"success": true, "message": "Reporte eliminado exitosamente"}
          ```
        - **Error Response Example:**
          ```
          00073REPORNK{"success": false, "message": "No tienes permisos para eliminar este reporte"}
          ```

- **`service_admin_delete_report`**
    - Description: Elimina cualquier reporte (solo moderadores).
    - Parameters (from `params_str`): `token`, `id_reporte`
    - Example: `00042REPORadmin_delete_report USER_TOKEN REPORT_ID`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00070REPOROK{"success": true, "message": "Reporte eliminado exitosamente por moderador"}
          ```
        - **Error Response Example:**
          ```
          00063REPORNK{"success": false, "message": "Solo los moderadores pueden usar este método"}
          ```

- **`service_info`**
    - Description: Método abstracto requerido por SOAServiceBase (Returns information about the report service).
    - Parameters (from `*args`): (effectively none for client)
    - Example: `00011REPORinfo`
    - #### Possible Responses
        - **Successful Response Example:**
          ```
          00128REPOROK{"service": "reprt", "description": "Servicio de gestión de reportes", "version": "1.0.0", "methods": ["list_of_methods"]}
          ```
        - **Error Response Example:**
          ```
          00049REPORNK{"success": false, "message": "Error interno: ERROR_MESSAGE_HERE"}
          ```
