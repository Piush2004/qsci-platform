import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    tier = Column(String, default="standard")
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="tenant")
    scenarios = relationship("Scenario", back_populates="tenant")
    users = relationship("User", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="viewer")  # Admin, Manager, Planner, Viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="users")

class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    status = Column(String, default="pending")
    priority = Column(Float, default=1.0)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="orders")
    shipments = relationship("Shipment", back_populates="order")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    supplier_id = Column(String, nullable=False)  # Usually maps to Neo4j/Supplier table
    moq = Column(Integer, default=1)
    lead_time_days = Column(Integer, default=7)
    status = Column(String, default="open")

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    carrier = Column(String)
    status = Column(String, default="in_transit")
    eta = Column(DateTime)
    
    order = relationship("Order", back_populates="shipments")

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    parameters = Column(JSON, default={})
    projected_outcomes = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="scenarios")

class Forecast(Base):
    """
    Time-Series data, primarily stored in TimescaleDB in production.
    Represented here for local SQLite testing.
    """
    __tablename__ = "forecasts"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    sku_id = Column(String, nullable=False)
    location_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    predicted_demand = Column(Float, nullable=False)
    p10 = Column(Float)
    p50 = Column(Float)
    p90 = Column(Float)
    metadata_json = Column(JSON, default={})
    
    recommendations = relationship("Recommendation", back_populates="forecast")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    forecast_id = Column(String, ForeignKey("forecasts.id"), nullable=False)
    action_type = Column(String, nullable=False)
    confidence_decomposition = Column(JSON, default={})  # Uncerainty, Data Quality, Agreement, Accuracy
    status = Column(String, default="pending")  # pending, approved, overridden
    created_at = Column(DateTime, default=datetime.utcnow)

    forecast = relationship("Forecast", back_populates="recommendations")
    approvals = relationship("Approval", back_populates="recommendation")

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    recommendation_id = Column(String, ForeignKey("recommendations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    decision = Column(String, nullable=False)  # approved, overridden, rejected
    reasoning = Column(String)
    is_override = Column(Boolean, default=False)
    decided_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="approvals")
    user = relationship("User")
