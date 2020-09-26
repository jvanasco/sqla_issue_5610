from pprint import pprint

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine("sqlite:///:memory:")
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))

    def __repr__(self):
        return f"<User(id={self.id}, user_name='{self.user_name}')>"


class ActionLog(Base):
    __tablename__ = "action_log"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(32), nullable=False)
    entity_id = Column(Integer, nullable=False)

    __mapper_args__ = {
        "polymorphic_on": entity_type,
    }

    def __repr__(self):
        return (
            f"<ActionLog(id={self.id}, entity_type='{self.entity_type}'"
            f", entity_id={self.entity_id})>"
        )


class ActionUserLog(ActionLog):
    user = relationship(
        User,
        primaryjoin="User.id==ActionLog.entity_id",
        foreign_keys=ActionLog.entity_id,
    )

    __mapper_args__ = {"polymorphic_identity": "user"}

    def __repr__(self):
        return (
            f"<ActionUserLog(id={self.id}, entity_type='{self.entity_type}'"
            f", entity_id={self.entity_id}, user={self.user})>"
        )


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

gord_user = User(user_name="Gord")
jonathan_user = User(user_name="Jonathan")
gord_log = ActionUserLog(user=gord_user)
jonathan_log = ActionUserLog(user=jonathan_user)

session.add_all([gord_user, jonathan_user, jonathan_log, gord_log])
session.commit()

result = session.query(ActionUserLog).all()
pprint(result)
"""console output:
[<ActionUserLog(id=1, entity_type='user', entity_id=2, user=<User(id=2, user_name='Jonathan')>)>,
 <ActionUserLog(id=2, entity_type='user', entity_id=1, user=<User(id=1, user_name='Gord')>)>]
"""
