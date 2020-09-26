from pprint import pprint

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine("sqlite:///:memory:")
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))
    log_entries = relationship("ActionUserLog")

    def __repr__(self):
        return f"<User(id={self.id}, user_name='{self.user_name}')>"


class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True)
    equipment_name = Column(String(100))
    log_entries = relationship("ActionEquipmentLog")

    def __repr__(self):
        return (
            f"<Equipment(id={self.id}"
            f", equipment_name='{self.equipment_name}')>"
        )


class ActionLog(Base):
    __tablename__ = "action_log"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(32), nullable=False)
    activity = Column(String(255), nullable=False)
    user_id = Column(ForeignKey("user.id"), nullable=True)
    equipment_id = Column(ForeignKey("equipment.id"), nullable=True)

    __mapper_args__ = {
        "polymorphic_on": entity_type,
    }

    def __repr__(self):
        return (
            f"<ActionLog(id={self.id}, entity_type='{self.entity_type}'"
            f", user_id={self.user_id})>"
        )


class ActionUserLog(ActionLog):
    user = relationship("User", back_populates="log_entries")

    __mapper_args__ = {"polymorphic_identity": "user"}

    def __repr__(self):
        return (
            f"<ActionUserLog(id={self.id}, entity_type='{self.entity_type}'"
            f", user_id={self.user_id}, user={self.user}"
            f", activity='{self.activity}')>"
        )


class ActionEquipmentLog(ActionLog):
    equipment = relationship("Equipment", back_populates="log_entries")

    __mapper_args__ = {"polymorphic_identity": "equipment"}

    def __repr__(self):
        return (
            f"<ActionEquipmentLog(id={self.id}"
            f", entity_type='{self.entity_type}'"
            f", equipment_id={self.equipment_id}, equipment={self.equipment}"
            f", activity='{self.activity}')>"
        )


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

gord_user = User(user_name="Gord")
jonathan_user = User(user_name="Jonathan")
gord_log = ActionUserLog(user=gord_user, activity="ate cookie")
jonathan_log = ActionUserLog(user=jonathan_user, activity="walked dog(s)")
gord_log2 = ActionUserLog(user=gord_user, activity="took nap")
osc_over = Equipment(equipment_name="Oscillation Overthruster")
osc_over_log = ActionEquipmentLog(equipment=osc_over, activity="recalibrate")

session.add_all(
    [
        gord_user,
        jonathan_user,
        jonathan_log,
        gord_log,
        gord_log2,
        osc_over,
        osc_over_log,
    ]
)
session.commit()

result = session.query(ActionUserLog).all()
pprint(result)
"""console output:
[<ActionUserLog(id=1, entity_type='user', user_id=1, user=<User(id=1, user_name='Gord')>, activity='ate cookie')>,
 <ActionUserLog(id=2, entity_type='user', user_id=1, user=<User(id=1, user_name='Gord')>, activity='took nap')>,
 <ActionUserLog(id=3, entity_type='user', user_id=2, user=<User(id=2, user_name='Jonathan')>, activity='walked dog(s)')>]
"""

result = session.query(ActionEquipmentLog).all()
pprint(result)
"""console output:
[<ActionEquipmentLog(id=4, entity_type='equipment', equipment_id=1, equipment=<Equipment(id=1, equipment_name='Oscillation Overthruster')>, activity='recalibrate')>]
"""

pprint(gord_user.log_entries)
"""console output:
[<ActionUserLog(id=1, entity_type='user', user_id=1, user=<User(id=1, user_name='Gord')>, activity='ate cookie')>,
 <ActionUserLog(id=2, entity_type='user', user_id=1, user=<User(id=1, user_name='Gord')>, activity='took nap')>]
"""
