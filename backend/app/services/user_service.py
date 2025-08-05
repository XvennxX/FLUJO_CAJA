from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.models.rol import Rol
from app.core.security import get_password_hash
from app.services.audit_service import AuditService

class UserService:
    """Servicio para gestión de usuarios"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def crear_usuario(
        self,
        nombre_completo: str,
        correo: str,
        contraseña: str,
        id_rol: int,
        created_by: int
    ) -> Dict[str, Any]:
        """
        Crea un nuevo usuario en el sistema
        
        Args:
            nombre_completo: Nombre completo del usuario
            correo: Email del usuario
            contraseña: Contraseña en texto plano
            id_rol: ID del rol asignado
            created_by: ID del usuario que crea este usuario
            
        Returns:
            Dict con información del usuario creado
            
        Raises:
            HTTPException: Si hay errores en la validación o creación
        """
        try:
            # Validar que el correo no exista
            existing_user = self.db.query(Usuario).filter(
                Usuario.correo == correo
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está registrado"
                )
            
            # Validar que el rol exista
            rol = self.db.query(Rol).filter(Rol.id_rol == id_rol).first()
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El rol especificado no existe"
                )
            
            # Crear el usuario
            nuevo_usuario = Usuario(
                nombre_completo=nombre_completo,
                correo=correo,
                contraseña=get_password_hash(contraseña),
                id_rol=id_rol,
                estado=True
            )
            
            self.db.add(nuevo_usuario)
            self.db.flush()  # Para obtener el ID sin hacer commit
            
            # Registrar en auditoría
            self.audit_service.registrar_accion(
                id_usuario=created_by,
                accion=f"Creó usuario: {correo}",
                tabla_afectada="usuario",
                id_registro_afectado=nuevo_usuario.id_usuario
            )
            
            self.db.commit()
            
            return {
                "id_usuario": nuevo_usuario.id_usuario,
                "nombre_completo": nuevo_usuario.nombre_completo,
                "correo": nuevo_usuario.correo,
                "id_rol": nuevo_usuario.id_rol,
                "estado": nuevo_usuario.estado,
                "rol_nombre": rol.nombre_rol
            }
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
    
    def obtener_usuario_por_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con información del usuario o None si no existe
        """
        try:
            usuario = self.db.query(Usuario).filter(
                Usuario.id_usuario == user_id
            ).first()
            
            if not usuario:
                return None
            
            return {
                "id_usuario": usuario.id_usuario,
                "nombre_completo": usuario.nombre_completo,
                "correo": usuario.correo,
                "id_rol": usuario.id_rol,
                "estado": usuario.estado,
                "rol_nombre": usuario.rol.nombre_rol if usuario.rol else None
            }
            
        except Exception as e:
            print(f"Error al obtener usuario: {str(e)}")
            return None
    
    def listar_usuarios(
        self,
        skip: int = 0,
        limit: int = 100,
        filtro_estado: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista todos los usuarios del sistema
        
        Args:
            skip: Número de registros a saltar
            limit: Máximo número de registros a devolver
            filtro_estado: Filtrar por estado activo/inactivo
            
        Returns:
            Lista de usuarios
        """
        try:
            query = self.db.query(Usuario)
            
            if filtro_estado is not None:
                query = query.filter(Usuario.estado == filtro_estado)
            
            usuarios = query.offset(skip).limit(limit).all()
            
            return [
                {
                    "id_usuario": usuario.id_usuario,
                    "nombre_completo": usuario.nombre_completo,
                    "correo": usuario.correo,
                    "id_rol": usuario.id_rol,
                    "estado": usuario.estado,
                    "rol_nombre": usuario.rol.nombre_rol if usuario.rol else None
                }
                for usuario in usuarios
            ]
            
        except Exception as e:
            print(f"Error al listar usuarios: {str(e)}")
            return []
    
    def actualizar_usuario(
        self,
        user_id: int,
        nombre_completo: Optional[str] = None,
        correo: Optional[str] = None,
        id_rol: Optional[int] = None,
        updated_by: int = None
    ) -> Dict[str, Any]:
        """
        Actualiza un usuario existente
        
        Args:
            user_id: ID del usuario a actualizar
            nombre_completo: Nuevo nombre completo
            correo: Nuevo correo electrónico
            id_rol: Nuevo rol
            updated_by: ID del usuario que realiza la actualización
            
        Returns:
            Dict con información del usuario actualizado
        """
        try:
            usuario = self.db.query(Usuario).filter(
                Usuario.id_usuario == user_id
            ).first()
            
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Actualizar campos si se proporcionan
            cambios = []
            
            if nombre_completo is not None:
                old_name = usuario.nombre_completo
                usuario.nombre_completo = nombre_completo
                cambios.append(f"Nombre: {old_name} → {nombre_completo}")
            
            if correo is not None:
                # Verificar que el correo no esté en uso
                existing_user = self.db.query(Usuario).filter(
                    Usuario.correo == correo,
                    Usuario.id_usuario != user_id
                ).first()
                
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El correo ya está en uso por otro usuario"
                    )
                
                old_email = usuario.correo
                usuario.correo = correo
                cambios.append(f"Correo: {old_email} → {correo}")
            
            if id_rol is not None:
                # Verificar que el rol existe
                rol = self.db.query(Rol).filter(Rol.id_rol == id_rol).first()
                if not rol:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El rol especificado no existe"
                    )
                
                old_role = usuario.rol.nombre_rol if usuario.rol else "Sin rol"
                usuario.id_rol = id_rol
                cambios.append(f"Rol: {old_role} → {rol.nombre_rol}")
            
            if cambios and updated_by:
                self.audit_service.registrar_accion(
                    id_usuario=updated_by,
                    accion=f"Actualizó usuario {usuario.correo}: {', '.join(cambios)}",
                    tabla_afectada="usuario",
                    id_registro_afectado=user_id
                )
            
            self.db.commit()
            self.db.refresh(usuario)
            
            return {
                "id_usuario": usuario.id_usuario,
                "nombre_completo": usuario.nombre_completo,
                "correo": usuario.correo,
                "id_rol": usuario.id_rol,
                "estado": usuario.estado,
                "rol_nombre": usuario.rol.nombre_rol if usuario.rol else None
            }
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar usuario: {str(e)}"
            )
    
    def cambiar_estado_usuario(
        self,
        user_id: int,
        nuevo_estado: bool,
        changed_by: int
    ) -> Dict[str, Any]:
        """
        Cambia el estado activo/inactivo de un usuario
        
        Args:
            user_id: ID del usuario
            nuevo_estado: True para activar, False para desactivar
            changed_by: ID del usuario que realiza el cambio
            
        Returns:
            Dict con información del usuario actualizado
        """
        try:
            usuario = self.db.query(Usuario).filter(
                Usuario.id_usuario == user_id
            ).first()
            
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            estado_anterior = usuario.estado
            usuario.estado = nuevo_estado
            
            # Registrar cambio en auditoría
            accion = f"{'Activó' if nuevo_estado else 'Desactivó'} usuario {usuario.correo}"
            self.audit_service.registrar_accion(
                id_usuario=changed_by,
                accion=accion,
                tabla_afectada="usuario",
                id_registro_afectado=user_id
            )
            
            self.db.commit()
            
            return {
                "id_usuario": usuario.id_usuario,
                "correo": usuario.correo,
                "estado_anterior": estado_anterior,
                "estado_nuevo": nuevo_estado,
                "mensaje": f"Usuario {'activado' if nuevo_estado else 'desactivado'} exitosamente"
            }
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cambiar estado del usuario: {str(e)}"
            )
    
    def cambiar_contraseña(
        self,
        user_id: int,
        nueva_contraseña: str,
        changed_by: int
    ) -> Dict[str, str]:
        """
        Cambia la contraseña de un usuario
        
        Args:
            user_id: ID del usuario
            nueva_contraseña: Nueva contraseña en texto plano
            changed_by: ID del usuario que realiza el cambio
            
        Returns:
            Dict con mensaje de confirmación
        """
        try:
            usuario = self.db.query(Usuario).filter(
                Usuario.id_usuario == user_id
            ).first()
            
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            usuario.contraseña = get_password_hash(nueva_contraseña)
            
            # Registrar cambio en auditoría
            self.audit_service.registrar_accion(
                id_usuario=changed_by,
                accion=f"Cambió contraseña del usuario {usuario.correo}",
                tabla_afectada="usuario",
                id_registro_afectado=user_id
            )
            
            self.db.commit()
            
            return {"mensaje": "Contraseña actualizada exitosamente"}
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cambiar contraseña: {str(e)}"
            )
