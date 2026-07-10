from app.core.database import Base, engine
from app.models import User, Portfolio, Holding

Base.metadata.create_all(bind=engine)

print("Tables created successfully")