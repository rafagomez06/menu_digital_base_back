from app.main import db
from app.models.MenuModel import CtlPlatillos
from sqlalchemy.exc import SQLAlchemyError
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.FileTools import FileTools  
from app.utils.Messages import *
from app.main import db
from app.utils.Logger import logger
LOG = logger()

class MenuRepository:
    
    @staticmethod
    def obtener_platillos(id_platillo=None):
        try:
            # Obtenemos platillos activos
            query = CtlPlatillos.query.filter(CtlPlatillos.activo == 1)
            
            if id_platillo:
                query = query.filter(CtlPlatillos.id_platillo == id_platillo)
                
            return query.order_by(CtlPlatillos.fecha_creacion.desc()).all()
        except SQLAlchemyError as e:
                LOG.error(f"DB error en obtener_platillos: {str(e)}")
                raise DatabaseError("Error al consultar la base de datos")
        
    @staticmethod
    def crear_platillo(nuevo_platillo: CtlPlatillos):
        try:
            db.session.add(nuevo_platillo)
            db.session.commit()
            return nuevo_platillo
        except SQLAlchemyError as e:
                db.session.rollback()
                LOG.error(f"DB error en crear_platillo: {str(e)}")
                raise DatabaseError("Error al consultar la base de datos")

    @staticmethod
    def obtener_platillo_activo(id_platillo):
        try:
            # Buscamos si existe el platillo y que este activo antes de editar
            return db.session.query(CtlPlatillos).filter_by(
                            id_platillo=id_platillo, activo=1
                            ).first()    
        except SQLAlchemyError as e:
            LOG.error(f"DB error en obtener_platillo_activo: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")     

    @staticmethod
    def editar_platillo():
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOG.error(f"DB error en editar_platillo: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")        
    
    @staticmethod
    def eliminar_platillo():
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOG.error(f"DB error en eliminar_platillo: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")        