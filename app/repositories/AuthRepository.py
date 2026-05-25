from app.main import db
from app.models.UsuarioModel import UsuarioAdmin
from sqlalchemy.exc import SQLAlchemyError
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.FileTools import FileTools  
from app.utils.Messages import *
from app.main import db
from app.utils.Logger import logger
LOG = logger()

class AuthRepository:

    @staticmethod
    def obtener_usuario_por_nombre_activo(nombre_usuario):
        try:
            # valida que exista el usuario y este activo
            usuario_id = UsuarioAdmin.query.filter_by(
                        nombre=nombre_usuario,
                        activo=1
                        ).first()
            return usuario_id
        except SQLAlchemyError as e:
            LOG.error(f"DB error en obtener_usuario_por_nombre_activo: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")   
    
    @staticmethod
    def crear_administrador(nuevo_admin):
            try:
                db.session.add(nuevo_admin)
                db.session.commit()
                return nuevo_admin
            except SQLAlchemyError as e:
                LOG.error(f"DB error en crear_administrador: {str(e)}")
                raise DatabaseError("Error al consultar la base de datos")   
                












