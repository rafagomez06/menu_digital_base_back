from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from app.models.UsuarioModel import UsuarioAdmin
from app.repositories.AuthRepository import AuthRepository
from app.utils.response import api_response
from app.utils.RaiseException import UnexpectedError
from app.utils.Logger import logger
import traceback
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.Messages import *
from app.main import db

LOG = logger()

class AuthServices:
    @staticmethod
    def login_admin(data):
        try:
            # validamos que exista el usuario
            nombre_usuario = data["nombre_usuario"].strip() 
            usuario_activo = AuthRepository.obtener_usuario_por_nombre_activo(nombre_usuario)

            if not usuario_activo:
                return api_response(STATUS_CODE_404, "",ERROR,ADMIN_NO_EXISTE)

            # Validamos y controlamos entrada de datos
            if not data or not data.get("nombre_usuario") or not data.get("password"):
                return api_response(STATUS_CODE_401, "",ERROR,CAMPOS_REQUERIDOS)                
            if not data:
                return api_response(STATUS_CODE_401, "",ERROR,DATA_EMPTY)                

            nombre_usuario = data["nombre_usuario"].strip()
            password = data["password"]

            if not usuario_activo or not usuario_activo.check_password(password):
                LOG.warning(f"Intento de login fallido para usuario: {nombre_usuario}")
                return api_response(STATUS_CODE_401, "",ERROR,CREDENCIALES_FALLIDAS)                

            token = create_access_token(identity=str(usuario_activo.id))
            LOG.info(f"Login exitoso: {nombre_usuario}")
            
            return api_response(STATUS_CODE_200, {
                    "token": token,
                    "usuario": usuario_activo.to_dict()},SUCCESS,LOGIN_SUCCESS)
        except ValueError as e: 
            LOG.warning(f"Parámetro inválido: {str(e)}")
            raise UnexpectedError("Parámetros de búsqueda inválidos")
        except Exception as e:  
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")        

    @staticmethod
    def registrar_admin(data):
        try:  
            # Obtenemos valores 
            nombre_usuario = data["nombre_usuario"].strip()
            password = data["password"]

            # Validamos y controladmos entrada de datos
            if not data or not data.get("nombre_usuario") or not data.get("password"):
                return api_response(STATUS_CODE_401, "",ERROR,CAMPOS_REQUERIDOS)                
            if not data:
                return api_response(STATUS_CODE_401, "",ERROR,DATA_EMPTY)    
            # Validar longitud de usuario y contraseña
            if (len(nombre_usuario) <=3):
                return api_response(STATUS_CODE_400,{},ERROR,USER_CORTO)    
            if (len(password) < 6):
                return api_response(STATUS_CODE_400,{},ERROR,PASSWORD_CORTO)            
            # Obtenemos valores
            nombre_usuario = data["nombre_usuario"].strip()
            password = data["password"]
            
            # Validar que no exista el admin
            usuario_existente = AuthRepository.obtener_usuario_por_nombre_activo(nombre_usuario)

            if usuario_existente:
                return api_response(STATUS_CODE_400,{},ERROR,ADMIN_EXISTENTE)

            # Creamos nuevo admin
            nuevo_admin = UsuarioAdmin(nombre=nombre_usuario)
            nuevo_admin.set_password(password) 

            administrador_creado = AuthRepository.crear_administrador(nuevo_admin)
            
            LOG.info(f"# Nuevo admin creado: {nombre_usuario}")
            

            return api_response(STATUS_CODE_201,administrador_creado.to_dict(),SUCCESS,ADMIN_CREADO_EXITOSAMENTE)                
        except ValueError as e: 
            LOG.warning(f"Parámetro inválido: {str(e)}")
            raise UnexpectedError("Parámetros de búsqueda inválidos")
        except Exception as e:  
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")