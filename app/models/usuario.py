from datetime import datetime
from app.main import db, bcrypt


class UsuarioAdmin(db.Model):
    __tablename__ = "ctl_usuarios_sistema_menu"

    id            = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_creacion = db.Column(db.String(100), nullable=True) 

    def set_password(self, password: str):
        resultado = self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        return resultado

    def check_password(self, password_plano: str) -> bool:
        resultado = bcrypt.check_password_hash(self.password_hash, password_plano)
        return resultado

    def to_dict(self):
        return {
            "id":         self.id,
            "nombre":   self.nombre,
            "fecha_creacion": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_creacion else None,
        }

    def __repr__(self):
        return f"<UsuarioAdmin {self.nombre}>"
