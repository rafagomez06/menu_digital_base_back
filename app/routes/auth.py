from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models.usuario import UsuarioAdmin
from app.utils.response import api_response
from app.utils.RaiseException import MissingValueError, UnauthorizedError, UnexpectedError
from app.utils.Logger import logger
from app.utils.Messages import (
            STATUS_CODE_201,STATUS_CODE_400,USER_CORTO,ADMIN_CREADO_EXITOSAMENTE,
            ADMIN_EXISTENTE,PASSWORD_CORTO,CAMPOS_REQUERIDOS,SUCCESS,ERROR)
from app.main import db, bcrypt

LOG      = logger()
auth_bp  = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data or not data.get("nombre_usuario") or not data.get("password"):
        raise MissingValueError("nombre_usuario y password son requeridos")

    nombre_usuario = data["nombre_usuario"].strip()
    password = data["password"]

    usuario = UsuarioAdmin.query.filter_by(nombre=nombre_usuario).first()

    if not usuario or not usuario.check_password(password):
        LOG.warning(f"Intento de login fallido para usuario: {nombre_usuario}")
        raise UnauthorizedError("Credenciales incorrectas")

    token = create_access_token(identity=str(usuario.id))
    LOG.info(f"Login exitoso: {nombre_usuario}")

    return api_response(200, {
        "token":    token,
        "usuario":  usuario.to_dict(),
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    GET /api/auth/me
    Requiere JWT. Retorna los datos del administrador autenticado.
    """
    usuario_id = get_jwt_identity()
    usuario    = UsuarioAdmin.query.get(usuario_id)

    if not usuario:
        raise UnauthorizedError("Usuario no encontrado")

    return api_response(200, usuario.to_dict())


@auth_bp.route("/registrar", methods=["POST"])
def registrar_admin():
    data = request.get_json()
    
    # Validar datos requeridos
    if not data or not data.get("nombre_usuario") or not data.get("password"):
        return api_response(STATUS_CODE_400, "",ERROR,CAMPOS_REQUERIDOS)
    
    nombre_usuario = data["nombre_usuario"].strip()
    password = data["password"]
    
    # Validar que no exista el admin
    usuario_existente = UsuarioAdmin.query.filter_by(nombre=nombre_usuario).first()
    if usuario_existente:
        return api_response(STATUS_CODE_400,None,ERROR,ADMIN_EXISTENTE)
    
    # Validar longitud de usuario y contraseña
    if (len(nombre_usuario) <=3):
        return api_response(STATUS_CODE_400,None,ERROR,USER_CORTO)    
    if (len(password) < 6):
        return api_response(STATUS_CODE_400,None,ERROR,PASSWORD_CORTO)
    
    # Crear nuevo admin
    nuevo_admin = UsuarioAdmin(nombre=nombre_usuario)
    nuevo_admin.set_password(password) 
    db.session.add(nuevo_admin)
    db.session.commit()
    
    LOG.info(f"# Nuevo admin creado: {nombre_usuario}")
    
    return api_response(STATUS_CODE_201,{},SUCCESS,ADMIN_CREADO_EXITOSAMENTE)
