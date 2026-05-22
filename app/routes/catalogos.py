from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
import traceback
from app.main import db
from app.models.catalogo import (CatCategoriasPlatillos)
from app.utils.response import api_response
from app.utils.RaiseException import (
    DatabaseError, MissingValueError, NotFoundError, UnexpectedError
)
from app.utils.Messages import (
            STATUS_CODE_200,STATUS_CODE_404,ERROR_EMPTY,
            SUCCESS,ERROR)
from app.utils.Logger import logger

LOG           = logger()
catalogos_bp  = Blueprint("catalogos", __name__)


# #####################################
# RUTAS PÚBLICAS (sin JWT)
# #####################################

@catalogos_bp.route("/categorias-platillos", methods=["GET"])
def listar_categorias():
    try:
        id_categoria           = request.args.get("id_categoria")
        descripcion           = request.args.get("descripcion")

        query = CatCategoriasPlatillos.query.filter(CatCategoriasPlatillos.activo == 1)

        if id_categoria:
            query = query.filter(CatCategoriasPlatillos.id_categoria == id_categoria)
        
        if descripcion:
            query = query.filter(CatCategoriasPlatillos.descripcion.ilike(f"%{descripcion}%"))

        categorias = query.order_by(CatCategoriasPlatillos.id_categoria.asc()).all()
        
        if not categorias:
            LOG.warning(f"GET /categorias-platillos")
            return api_response(STATUS_CODE_404, None,ERROR,ERROR_EMPTY)

        LOG.info(f"GET /categorias-platillos — {len(categorias)} resultados")
        
        categorias_json = [c.to_dict() for c in categorias]
        
        return api_response(STATUS_CODE_200, categorias_json,SUCCESS)
    
    except SQLAlchemyError as e: 
        LOG.error(f"DB error en listar_categorias: {str(e)}")
        raise DatabaseError("Error al consultar la base de datos")
    except ValueError as e: 
        LOG.warning(f"Parámetro inválido: {str(e)}")
        raise UnexpectedError("Parámetros de búsqueda inválidos")
    except Exception as e:  
        error_trace = traceback.format_exc()
        LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
        raise UnexpectedError("Ocurrió un error inesperado")
    

# @catalogos_bp.route("/almacenamientos", methods=["GET"])
# def listar_almacenamientos():
#     try:
#         id_almacenamiento = request.args.get("id_almacenamiento")

#         query = CatAlmacenamientoCelulares.query.filter(CatAlmacenamientoCelulares.activo == 1)

#         if id_almacenamiento:
#             query = query.filter(CatAlmacenamientoCelulares.id == id_almacenamiento)

#         almacenamientos = query.order_by(CatAlmacenamientoCelulares.id.asc()).all()

#         if not almacenamientos:
#             LOG.warning(f"GET /almacenamientos - Sin resultados.")
#             return api_response(STATUS_CODE_404, None, ERROR,ERROR_EMPTY)

#         LOG.info(f"GET /almacenamientos - {len(almacenamientos)} resultados")
        
#         almacenamientos_json = [c.to_dict() for c in almacenamientos]
        
#         return api_response(STATUS_CODE_200, almacenamientos_json,SUCCESS)
    
#     except Exception as e:
#         error_trace = traceback.format_exc()
#         LOG.info(f"Ocurrio un error inesperado: [{e}] [{error_trace}]")
#         raise UnexpectedError("Ocurrio un error inesperado")   
#     except SQLAlchemyError as e:
#         LOG.error(f"DB error en listar_almacenamientos: {str(e)}")
#         raise DatabaseError("Error al obtener los almacenamientos")
    
# @catalogos_bp.route("/estados-celular", methods=["GET"])
# def listar_estados_celular():
#     try:
#         id_estado_celular = request.args.get("id_estado_celular")

#         query = CatEstadosCelulares.query.filter(CatEstadosCelulares.activo == 1)

#         if id_estado_celular:
#             query = query.filter(CatEstadosCelulares.id == id_estado_celular)

#         estados_celular = query.order_by(CatEstadosCelulares.id.asc()).all()

#         if not estados_celular:
#             LOG.warning(f"GET /estados-celular - Sin resultados.")
#             return api_response(STATUS_CODE_404, None, ERROR,ERROR_EMPTY)

#         LOG.info(f"GET /estados-celular - {len(estados_celular)} resultados")
        
#         estados_celular_json = [c.to_dict() for c in estados_celular]
        
#         return api_response(STATUS_CODE_200, estados_celular_json,SUCCESS)
    
#     except Exception as e:
#         error_trace = traceback.format_exc()
#         LOG.info(f"Ocurrio un error inesperado: [{e}] [{error_trace}]")
#         raise UnexpectedError("Ocurrio un error inesperado")   
#     except SQLAlchemyError as e:
#         LOG.error(f"DB error en listar_almacenamientos: {str(e)}")
#         raise DatabaseError("Error al obtener los almacenamientos")

# @catalogos_bp.route("/companias-celular", methods=["GET"])
# def listar_companias_celular():
#     try:
#         id_compania = request.args.get("id_compania")

#         query = CatCompaniasCelulares.query.filter(CatCompaniasCelulares.activo == 1)

#         if id_compania:
#             query = query.filter(CatCompaniasCelulares.id == id_compania)

#         companias_celular = query.order_by(CatCompaniasCelulares.id.asc()).all()

#         if not companias_celular:
#             LOG.warning(f"GET /companias-celular - Sin resultados.")
#             return api_response(STATUS_CODE_404, None, ERROR,ERROR_EMPTY)

#         LOG.info(f"GET /companias-celular - {len(companias_celular)} resultados")
        
#         companias_celular_json = [c.to_dict() for c in companias_celular]
        
#         return api_response(STATUS_CODE_200, companias_celular_json,SUCCESS)
    
#     except Exception as e:
#         error_trace = traceback.format_exc()
#         LOG.info(f"Ocurrio un error inesperado: [{e}] [{error_trace}]")
#         raise UnexpectedError("Ocurrio un error inesperado")   
#     except SQLAlchemyError as e:
#         LOG.error(f"DB error en listar_companias_celular: {str(e)}")
#         raise DatabaseError("Error al obtener las companias")

# @catalogos_bp.route("/colores-celular", methods=["GET"])
# def listar_colores_celular():
#     try:
#         id_color = request.args.get("id_color")

#         query = CatColoresCelulares.query.filter(CatColoresCelulares.activo == 1)

#         if id_color:
#             query = query.filter(CatColoresCelulares.id == id_color)

#         colores_celular = query.order_by(CatColoresCelulares.id.asc()).all()

#         if not colores_celular:
#             LOG.warning(f"GET /colores-celular - Sin resultados.")
#             return api_response(STATUS_CODE_404, None, ERROR,ERROR_EMPTY)

#         LOG.info(f"GET /colores-celular - {len(colores_celular)} resultados")
        
#         colores_celular_json = [c.to_dict() for c in colores_celular]
        
#         return api_response(STATUS_CODE_200, colores_celular_json,SUCCESS)
    
#     except Exception as e:
#         error_trace = traceback.format_exc()
#         LOG.info(f"Ocurrio un error inesperado: [{e}] [{error_trace}]")
#         raise UnexpectedError("Ocurrio un error inesperado")   
#     except SQLAlchemyError as e:
#         LOG.error(f"DB error en listar_colores_celular: {str(e)}")
#         raise DatabaseError("Error al obtener los colores")




# # ─────────────────────────────────────────────────────────────────────────────
# # RUTAS DE ADMINISTRADOR (requieren JWT)
# # ─────────────────────────────────────────────────────────────────────────────

# @celulares_bp.route("/admin/celulares", methods=["GET"])
# @jwt_required()
# def admin_listar_celulares():
#     """
#     GET /api/admin/celulares
#     Lista TODOS los equipos (activos e inactivos) para la tabla del panel admin.
#     """
#     try:
#         celulares = Celular.query.order_by(Celular.created_at.desc()).all()
#         return api_response(200, [c.to_dict() for c in celulares])
#     except SQLAlchemyError as e:
#         LOG.error(f"DB error en admin_listar_celulares: {str(e)}")
#         raise DatabaseError("Error al obtener los equipos")


# @celulares_bp.route("/admin/celulares", methods=["POST"])
# @jwt_required()
# def admin_crear_celular():
#     """
#     POST /api/admin/celulares
#     Crea un nuevo equipo celular. Las imágenes se suben por separado.
#     Body JSON requerido:
#     {
#         "marca": "Samsung",
#         "nombre": "Galaxy S24",
#         "almacenamiento_gb": 256,
#         "precio": 12999.00,
#         "bateria_porcentaje": 90,
#         "estado_id": 1
#     }
#     """
#     try:
#         data = request.get_json()

#         campos_requeridos = ["marca", "nombre", "almacenamiento_gb", "precio", "bateria_porcentaje", "estado_id"]
#         faltantes = [c for c in campos_requeridos if not data.get(c)]
#         if faltantes:
#             raise MissingValueError(f"Campos requeridos faltantes: {', '.join(faltantes)}")

#         # Validar que el estado exista
#         estado = EstadoEquipo.query.get(data["estado_id"])
#         if not estado:
#             raise NotFoundError(f"Estado con id {data['estado_id']} no existe")

#         # Validar rango de batería
#         bateria = int(data["bateria_porcentaje"])
#         if not (0 <= bateria <= 100):
#             raise MissingValueError("bateria_porcentaje debe ser un valor entre 0 y 100")

#         nuevo = Celular(
#             marca              = data["marca"].strip(),
#             nombre             = data["nombre"].strip(),
#             almacenamiento_gb  = int(data["almacenamiento_gb"]),
#             precio             = float(data["precio"]),
#             bateria_porcentaje = bateria,
#             estado_id          = data["estado_id"],
#             activo             = data.get("activo", True),
#         )

#         db.session.add(nuevo)
#         db.session.commit()

#         LOG.info(f"Celular creado: {nuevo.marca} {nuevo.nombre} (id={nuevo.id})")
#         return api_response(201, nuevo.to_dict())

#     except (MissingValueError, NotFoundError):
#         raise
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         LOG.error(f"DB error en admin_crear_celular: {str(e)}")
#         raise DatabaseError("Error al crear el equipo")


# @celulares_bp.route("/admin/celulares/<int:celular_id>", methods=["PUT"])
# @jwt_required()
# def admin_editar_celular(celular_id):
#     """
#     PUT /api/admin/celulares/<id>
#     Actualiza los datos de un equipo existente.
#     """
#     try:
#         celular = Celular.query.get(celular_id)
#         if not celular:
#             raise NotFoundError(f"Equipo con id {celular_id} no encontrado")

#         data = request.get_json()

#         # Actualiza solo los campos que vengan en el body
#         if "marca"              in data: celular.marca              = data["marca"].strip()
#         if "nombre"             in data: celular.nombre             = data["nombre"].strip()
#         if "almacenamiento_gb"  in data: celular.almacenamiento_gb  = int(data["almacenamiento_gb"])
#         if "precio"             in data: celular.precio             = float(data["precio"])
#         if "activo"             in data: celular.activo             = bool(data["activo"])

#         if "bateria_porcentaje" in data:
#             bateria = int(data["bateria_porcentaje"])
#             if not (0 <= bateria <= 100):
#                 raise MissingValueError("bateria_porcentaje debe ser un valor entre 0 y 100")
#             celular.bateria_porcentaje = bateria

#         if "estado_id" in data:
#             estado = EstadoEquipo.query.get(data["estado_id"])
#             if not estado:
#                 raise NotFoundError(f"Estado con id {data['estado_id']} no existe")
#             celular.estado_id = data["estado_id"]

#         db.session.commit()
#         LOG.info(f"Celular actualizado id={celular_id}")
#         return api_response(200, celular.to_dict())

#     except (MissingValueError, NotFoundError):
#         raise
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         LOG.error(f"DB error en admin_editar_celular: {str(e)}")
#         raise DatabaseError("Error al actualizar el equipo")


# @celulares_bp.route("/admin/celulares/<int:celular_id>", methods=["DELETE"])
# @jwt_required()
# def admin_eliminar_celular(celular_id):
#     """
#     DELETE /api/admin/celulares/<id>
#     Elimina un equipo y todas sus imágenes asociadas.
#     """
#     try:
#         celular = Celular.query.get(celular_id)
#         if not celular:
#             raise NotFoundError(f"Equipo con id {celular_id} no encontrado")

#         db.session.delete(celular)   # cascade elimina también las imágenes
#         db.session.commit()

#         LOG.info(f"Celular eliminado id={celular_id}")
#         return api_response(200, {"mensaje": f"Equipo {celular_id} eliminado correctamente"})

#     except NotFoundError:
#         raise
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         LOG.error(f"DB error en admin_eliminar_celular: {str(e)}")
#         raise DatabaseError("Error al eliminar el equipo")
