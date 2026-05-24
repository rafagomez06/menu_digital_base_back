from flask import request
from sqlalchemy.exc import SQLAlchemyError
from app.models.menu import CtlPlatillos
from app.utils.response import api_response
from app.utils.RaiseException import UnexpectedError
from app.utils.Logger import logger
import traceback
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.Messages import *
from app.main import db
from app.utils.FileTools import FileTools  

LOG = logger()

class MenuServices:
    @staticmethod
    def listar_platillos():
        try:
            id_platillo = request.args.get("id_platillo")

            query = CtlPlatillos.query.filter(CtlPlatillos.activo == 1)
            
            if id_platillo:
                query = query.filter(CtlPlatillos.id_platillo == id_platillo)

            platillos = query.order_by(CtlPlatillos.fecha_creacion.desc()).all()

            if not platillos:
                LOG.info(f"GET /menu - {ERROR_EMPTY}")            
                return api_response(STATUS_CODE_404, {},ERROR,ERROR_EMPTY)
            
            LOG.info(f"GET /menu - {len(platillos)} resultados")
            menu_json = [c.to_dict() for c in platillos]
            
            return api_response(STATUS_CODE_200, menu_json, SUCCESS)
        
        except SQLAlchemyError as e: 
            LOG.error(f"DB error en listar_platillos: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")
        except ValueError as e: 
            LOG.warning(f"Parámetro inválido: {str(e)}")
            raise UnexpectedError("Parámetros de búsqueda inválidos")
        except Exception as e:  
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")
    
    @staticmethod
    def crear_platillo(data, files):        
        try:
            # Validaciones
            campos_requeridos = ["nombre","precio","categoria_platillo_fk","descripcion"]
            campos_faltantes = [
                campo for campo in campos_requeridos 
                if campo not in data or not str(data[campo]).strip()
            ]

            if 'imagen' not in files:
                campos_faltantes.append('imagen')

            if campos_faltantes:
                return api_response(STATUS_CODE_400, {}, ERROR, CAMPOS_REQUERIDOS)

            foto = files['imagen']
            nombre_platillo = data.get("nombre")
            descripcion = data.get("descripcion")
            precio_raw = data.get("precio")

            try:
                precio = float(precio_raw) if precio_raw else 0.0
            except ValueError:
                return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_ERROR)

            if foto.filename == '':
                return api_response(STATUS_CODE_400, {}, ERROR, IMAGEN_EMPTY)

            # Validaciones de negocio
            if not nombre_platillo.strip():
                return api_response(STATUS_CODE_400, {}, ERROR, NOMBRE_PLATILLO_CORTO)
            if len(nombre_platillo) > 100:
                return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_LARGO)
            if len(descripcion) > 350:
                return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_LARGO)
            if not descripcion.strip():
                return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_CORTO)
            if precio <= 1:
                return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_MAX)

            # Guardar imagen
            nombre_archivo_guardado = FileTools.guardar_imagen(foto, UPLOAD_FOLDER)
            if not nombre_archivo_guardado:
                return api_response(STATUS_CODE_400, {}, ERROR, IMAGEN_ERROR)

            imagen_url_db = f"/uploads/platillos/{nombre_archivo_guardado}"

            nuevo_platillo = CtlPlatillos(
                nombre=nombre_platillo,
                precio=precio,
                categoria_platillo_fk=int(data["categoria_platillo_fk"]),
                descripcion=descripcion,
                imagen_url=imagen_url_db,
            )

            db.session.add(nuevo_platillo)
            db.session.commit()

            LOG.info(f"Platillo creado con éxito: {nuevo_platillo}")
            return api_response(STATUS_CODE_201, {}, SUCCESS, PLATILLO_SUCCESS)

        except SQLAlchemyError as e:
            db.session.rollback()
            if 'nombre_archivo_guardado' in locals() and nombre_archivo_guardado:
                FileTools.elimina_archivo(UPLOAD_FOLDER, nombre_archivo_guardado)
            LOG.error(f"DB error en crear_platillo: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")
        except Exception as e:
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")

    
    @staticmethod
    def editar_platillo(id_platillo, data):
        try:
            data = request.form
            # Buscamos si existe el platillo y que este activo antes de editar
            platillo = db.session.query(CtlPlatillos).filter_by(
                        id_platillo=id_platillo, activo=1
                        ).first()

            if not platillo:
                return api_response(STATUS_CODE_404, {}, ERROR, REGISTRO_NO_EXISTE)
            
            campos_requeridos = ["nombre", "precio", "categoria_platillo_fk", "descripcion"]
            
            campos_faltantes = [
                campo for campo in campos_requeridos 
                if campo not in data or data[campo] is None or str(data[campo]).strip() == ""
            ]

            if campos_faltantes:
                return api_response(STATUS_CODE_400, {}, ERROR, CAMPOS_REQUERIDOS)

            nombre_platillo = data.get("nombre")
            descripcion = data.get("descripcion")
            precio_raw = data.get("precio")

            # Validaciones 
            try:
                precio = float(precio_raw)
            except ValueError:
                return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_ERROR)

            if not nombre_platillo or not nombre_platillo.strip():
                return api_response(STATUS_CODE_400, {}, ERROR, NOMBRE_PLATILLO_CORTO)
            if len(nombre_platillo) > 100:
                return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_LARGO)        
            if len(descripcion) > 350:
                return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_LARGO)
            if not descripcion or not descripcion.strip():
                return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_CORTO)
            if not (precio > 1):
                return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_MAX)

            # validacion imagen
            imagen_url_db = platillo.imagen_url 
            archivo_viejo_a_eliminar = None

            if 'imagen' in request.files:
                foto = request.files['imagen']
                if foto and foto.filename != '':
                    # Guardamos la nueva imagen 
                    nombre_archivo_guardado = FileTools.guardar_imagen(foto, UPLOAD_FOLDER)
                    if not nombre_archivo_guardado:
                        return api_response(STATUS_CODE_400, {}, ERROR, IMAGEN_ERROR)
                    
                    # Guardamos la referencia de la foto vieja para borrarla del disco SOLO si la BD hace commit con éxito
                    if platillo.imagen_url:
                        archivo_viejo_a_eliminar = platillo.imagen_url.split('/')[-1]

                    # Nueva URL para la BD
                    imagen_url_db = f"/uploads/platillos/{nombre_archivo_guardado}"

            # Actualización de datos en el modelo
            platillo.nombre = nombre_platillo
            platillo.precio = precio
            platillo.categoria_platillo_fk = int(data["categoria_platillo_fk"])
            platillo.descripcion = descripcion
            platillo.imagen_url = imagen_url_db

            db.session.commit()

            # Limpieza del disco duro (solo si el commit fue exitoso)
            if archivo_viejo_a_eliminar:
                try:
                    FileTools.elimina_archivo(UPLOAD_FOLDER, archivo_viejo_a_eliminar)
                    LOG.info(f"Archivo viejo eliminado con éxito: {archivo_viejo_a_eliminar}")
                except Exception as file_err:
                    LOG.warning(f"No se pudo eliminar el archivo físico viejo {archivo_viejo_a_eliminar}: {str(file_err)}")

            LOG.info(f"# Platillo Editado con éxito ID {id_platillo}: {platillo}")
            return api_response(STATUS_CODE_200, {}, SUCCESS, PLATILLO_SUCCESS_UPDATED)
        
        except SQLAlchemyError as e: 
            db.session.rollback()        
            if 'nombre_archivo_guardado' in locals() and nombre_archivo_guardado:
                FileTools.elimina_archivo(UPLOAD_FOLDER, nombre_archivo_guardado)
                
            LOG.error(f"DB error en editar_platillo: {str(e)}")
            raise DatabaseError("Error al actualizar la base de datos")
        except Exception as e:  
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado en editar_platillo: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")
    
    @staticmethod
    def eliminar_platillo(id_platillo):
        try:
            platillo = db.session.get(CtlPlatillos, id_platillo)      
            
            if not platillo:
                LOG.info(f"DELETE /menu/{id_platillo} - {ERROR_EMPTY}")            
                return api_response(STATUS_CODE_404,None,ERROR,ERROR_EMPTY)

            platillo.activo = 0
            db.session.commit()
            LOG.info(f"DELETE /menu/{id_platillo} - Platillo marcado como inactivo")
            return api_response(STATUS_CODE_200, {},SUCCESS,PLATILLO_SUCCESS_DELETED)
        
        except SQLAlchemyError as e: 
            db.session.rollback()            
            LOG.error(f"DB error en eliminar_platillo: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")
        except ValueError as e: 
            LOG.warning(f"Parámetro inválido: {str(e)}")
            raise UnexpectedError("Parámetros de búsqueda inválidos")
        except Exception as e:  
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")        