import enum
from sqlalchemy import Column, Integer, String, Enum, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class OrderStatusEnum(str, enum.Enum):
    PENDING = "pending"
    HANDED_OVER = "handed_over"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    status = Column(Enum(OrderStatusEnum, values_callable=lambda x: [e.value for e in x]), default=OrderStatusEnum.PENDING)

# Test
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Create order
order = Order(status=OrderStatusEnum.HANDED_OVER)
session.add(order)
session.commit()

# Load order
loaded_order = session.query(Order).first()
print(f"Loaded Status Type: {type(loaded_order.status)}")
print(f"Loaded Status Value: {loaded_order.status}")

try:
    print(f"Accessing .value: {loaded_order.status.value}")
except AttributeError as e:
    print(f"AttributeError: {e}")
