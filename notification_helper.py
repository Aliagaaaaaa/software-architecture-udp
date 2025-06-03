#!/usr/bin/env python3
"""
Helper de Notificaciones - SOA
Permite a otros servicios crear notificaciones directamente en la DB
"""

import logging
from datetime import datetime
from database_client import DatabaseClient
from typing import Optional

class NotificationHelper:
    def __init__(self):
        self.db_client = DatabaseClient()
        self.logger = logging.getLogger('NotificationHelper')

    def create_notification(self, 
                          usuario_id: int, 
                          titulo: str, 
                          mensaje: str, 
                          tipo: str, 
                          referencia_id: Optional[int] = None) -> bool:
        """
        Crea una notificación en la base de datos
        
        Args:
            usuario_id: ID del usuario que recibirá la notificación
            titulo: Título de la notificación (máximo 100 caracteres)
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación (mensaje, reporte, foro, post, comentario, evento, sistema)
            referencia_id: ID del objeto relacionado (opcional)
            
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        try:
            # Validar parámetros
            if not usuario_id or not titulo or not mensaje or not tipo:
                self.logger.error("Parámetros requeridos faltantes para crear notificación")
                return False
            
            if len(titulo) > 100:
                titulo = titulo[:97] + "..."  # Truncar si es muy largo
            
            # Insertar notificación
            now = datetime.now().isoformat()
            query = """
            INSERT INTO NOTIFICACION (usuario_id, titulo, mensaje, tipo, referencia_id, leido, fecha)
            VALUES (?, ?, ?, ?, ?, FALSE, ?)
            """
            
            result = self.db_client.execute_query(query, [usuario_id, titulo, mensaje, tipo, referencia_id, now])
            
            if result.get('success'):
                self.logger.info(f"✅ Notificación creada para usuario {usuario_id}: {titulo}")
                return True
            else:
                self.logger.error(f"❌ Error creando notificación: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error en create_notification: {e}")
            return False

    def notify_new_message(self, receptor_id: int, emisor_email: str, contenido_preview: str, mensaje_id: int) -> bool:
        """Notifica sobre un nuevo mensaje recibido"""
        titulo = f"Nuevo mensaje de {emisor_email}"
        preview = contenido_preview[:50] + ("..." if len(contenido_preview) > 50 else "")
        mensaje = f"Has recibido un nuevo mensaje: '{preview}'"
        return self.create_notification(receptor_id, titulo, mensaje, "mensaje", mensaje_id)

    def notify_new_report(self, moderadores_ids: list, tipo_contenido: str, contenido_id: int, reportador_email: str, reporte_id: int) -> bool:
        """Notifica a moderadores sobre un nuevo reporte"""
        titulo = f"Nuevo reporte de {tipo_contenido}"
        mensaje = f"{reportador_email} ha reportado un {tipo_contenido} (ID: {contenido_id}). Requiere revisión."
        
        success = True
        for moderador_id in moderadores_ids:
            if not self.create_notification(moderador_id, titulo, mensaje, "reporte", reporte_id):
                success = False
        return success

    def notify_new_forum(self, usuarios_ids: list, creador_email: str, titulo_foro: str, foro_id: int) -> bool:
        """Notifica sobre un nuevo foro creado"""
        titulo = f"Nuevo foro creado"
        mensaje = f"{creador_email} ha creado el foro '{titulo_foro}'. ¡Únete a la discusión!"
        
        success = True
        for usuario_id in usuarios_ids:
            if not self.create_notification(usuario_id, titulo, mensaje, "foro", foro_id):
                success = False
        return success

    def notify_new_post(self, foro_participantes_ids: list, autor_email: str, foro_titulo: str, post_id: int, autor_id: int) -> bool:
        """Notifica a participantes del foro sobre un nuevo post"""
        titulo = f"Nuevo post en {foro_titulo}"
        mensaje = f"{autor_email} ha publicado un nuevo post en el foro '{foro_titulo}'"
        
        success = True
        for usuario_id in foro_participantes_ids:
            # No notificar al autor
            if usuario_id != autor_id:
                if not self.create_notification(usuario_id, titulo, mensaje, "post", post_id):
                    success = False
        return success

    def notify_new_comment(self, post_participantes_ids: list, autor_email: str, post_preview: str, comentario_id: int, autor_id: int) -> bool:
        """Notifica a participantes del post sobre un nuevo comentario"""
        titulo = f"Nuevo comentario"
        post_preview = post_preview[:30] + ("..." if len(post_preview) > 30 else "")
        mensaje = f"{autor_email} ha comentado en el post '{post_preview}'"
        
        success = True
        for usuario_id in post_participantes_ids:
            # No notificar al autor del comentario
            if usuario_id != autor_id:
                if not self.create_notification(usuario_id, titulo, mensaje, "comentario", comentario_id):
                    success = False
        return success

    def notify_new_event(self, usuarios_ids: list, creador_email: str, evento_nombre: str, evento_fecha: str, evento_id: int) -> bool:
        """Notifica sobre un nuevo evento"""
        titulo = f"Nuevo evento: {evento_nombre}"
        mensaje = f"{creador_email} ha creado el evento '{evento_nombre}' para el {evento_fecha}"
        
        success = True
        for usuario_id in usuarios_ids:
            if not self.create_notification(usuario_id, titulo, mensaje, "evento", evento_id):
                success = False
        return success

    def notify_report_status_change(self, reportador_id: int, nuevo_estado: str, tipo_contenido: str, reporte_id: int) -> bool:
        """Notifica al reportador sobre un cambio de estado en su reporte"""
        titulo = f"Actualización de reporte"
        mensaje = f"Tu reporte de {tipo_contenido} ha sido actualizado a estado: {nuevo_estado}"
        return self.create_notification(reportador_id, titulo, mensaje, "reporte", reporte_id)

    def notify_system_message(self, usuario_id: int, titulo: str, mensaje: str) -> bool:
        """Notifica un mensaje del sistema"""
        return self.create_notification(usuario_id, titulo, mensaje, "sistema")

    def get_moderators_ids(self) -> list:
        """Obtiene los IDs de todos los moderadores del sistema"""
        try:
            query = "SELECT id_usuario FROM USUARIO WHERE rol = 'moderador'"
            result = self.db_client.execute_query(query)
            
            if result.get('success') and result.get('results'):
                moderators = []
                for user_data in result['results']:
                    if isinstance(user_data, dict):
                        moderators.append(user_data.get('id_usuario'))
                    else:
                        moderators.append(user_data[0])
                return moderators
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error obteniendo moderadores: {e}")
            return []

    def get_all_users_ids(self, exclude_user_id: Optional[int] = None) -> list:
        """Obtiene los IDs de todos los usuarios del sistema"""
        try:
            if exclude_user_id:
                query = "SELECT id_usuario FROM USUARIO WHERE id_usuario != ?"
                result = self.db_client.execute_query(query, [exclude_user_id])
            else:
                query = "SELECT id_usuario FROM USUARIO"
                result = self.db_client.execute_query(query)
            
            if result.get('success') and result.get('results'):
                users = []
                for user_data in result['results']:
                    if isinstance(user_data, dict):
                        users.append(user_data.get('id_usuario'))
                    else:
                        users.append(user_data[0])
                return users
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}")
            return [] 