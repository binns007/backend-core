from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Enum as SQLAlchemyEnum,DECIMAL,DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class RoleEnum(enum.Enum):
    ADMIN = "admin"
    DEALER = "dealer"
    SALES_EXECUTIVE = "sales_executive"
    FINANCE = "finance"
    RTO = "rto"
    CUSTOMER = "customer"
    
class Dealership(Base):
    __tablename__ = "dealerships"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, unique=True)
    created_at = Column(TIMESTAMP, server_default="now()")
    address = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    num_employees = Column(Integer, nullable=False)
    num_branches = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    roles = relationship("DealershipRole", back_populates="dealership")
    payments = relationship("Payment", back_populates="dealership")
    branches = relationship("Branch", back_populates="dealership")
    users = relationship("User", back_populates="dealership",foreign_keys="[User.dealership_id]")
    customers = relationship("Customer", back_populates="dealership")
    creator = relationship("User", back_populates="created_dealership",foreign_keys="[Dealership.creator_id]")
    form_templates = relationship("FormTemplate", back_populates="dealership")  


class DealershipRole(Base):
    __tablename__ = "dealership_roles"
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id"), nullable=False)
    role = Column(SQLAlchemyEnum(RoleEnum), nullable=False)
    enabled = Column(Boolean, default=True)
    
    dealership = relationship("Dealership", back_populates="roles")

class SuggestedRole(Base):
    __tablename__ = "suggested_roles"
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id"), nullable=False)
    role_name = Column(String, nullable=False)
    reason = Column(String)  # Optional description of why they need this role
class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(TIMESTAMP, server_default="now()")
    
    dealership = relationship("Dealership", back_populates="branches")
    users = relationship("User", back_populates="branch")
    customers = relationship("Customer", back_populates="branch")



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"),nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    role = Column(SQLAlchemyEnum(RoleEnum), nullable=False) 
    password = Column(String, nullable=False)
    phone_number = Column(String)
    is_activated = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default="now()")
    
    
    dealership = relationship("Dealership", back_populates="users",foreign_keys="[User.dealership_id]")
    branch = relationship("Branch", back_populates="users")
    created_dealership = relationship("Dealership", back_populates="creator",foreign_keys="[Dealership.creator_id]")



class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"))  # Add this foreign key

    status = Column(String, default="Pending")  # Payment status: Pending, Completed, etc.
    amount = Column(DECIMAL(10, 2))  # Amount paid
    payment_date = Column(TIMESTAMP, nullable=True)  # Date of payment
    transaction_id = Column(String, nullable=True)  # Optional transaction ID

    dealership = relationship("Dealership", back_populates="payments")

    

class OTP(Base):
    __tablename__ = 'otps'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)  # Store email instead of user_id
    otp_code = Column(String, nullable=False)
    expiration_time = Column(DateTime, nullable=False)
    verified = Column(Boolean)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"))
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    name = Column(String, nullable=False)
    phone_number = Column(String)
    email = Column(String, unique=True)
    created_at = Column(TIMESTAMP, server_default="now()")
    
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    vehicle = relationship("Vehicle", back_populates="customers")

    dealership = relationship("Dealership", back_populates="customers")
    branch = relationship("Branch", back_populates="customers")
    user = relationship("User")


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    variant = Column(String, nullable=False)
    color = Column(String, nullable=True)
    ex_showroom_price = Column(DECIMAL(10, 2))
    tax = Column(DECIMAL(10, 2))
    insurance = Column(DECIMAL(10, 2))
    tp_registration = Column(DECIMAL(10, 2))
    man_accessories = Column(DECIMAL(10, 2))
    optional_accessories = Column(DECIMAL(10, 2))
    
    # Relationships
    customers = relationship("Customer", back_populates="vehicle")


class FilledByEnum(str, enum.Enum):
    SALES_EXECUTIVE = "sales_executive"
    CUSTOMER = "customer"

# Enum to define the data type for each form field
class FieldTypeEnum(str, enum.Enum):
    TEXT = "text"  # "TEXT" is the member name, and "text" is the value
    NUMBER = "number"
    IMAGE = "image" 
    DATE = "date"
    

class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)  # Flag for active template
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_activated_at = Column(TIMESTAMP(timezone=True), nullable=True)  # New column

    fields = relationship("FormField", back_populates="template")
    instances = relationship("FormInstance", back_populates="template")

    dealership_id = Column(Integer, ForeignKey('dealerships.id'))  # Ensure this field exists

    dealership = relationship("Dealership", back_populates="form_templates")  # Relationship with Dealership



class FormField(Base):
    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("form_templates.id"), nullable=False)
    name = Column(String, nullable=False)
    field_type = Column(SQLAlchemyEnum(FieldTypeEnum), nullable=False)
    is_required = Column(Boolean, default=True)
    filled_by = Column(SQLAlchemyEnum(FilledByEnum), nullable=False)
    order = Column(Integer, nullable=False)

    template = relationship("FormTemplate", back_populates="fields")


class FormInstance(Base):
    __tablename__ = "form_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("form_templates.id"), nullable=False)
    generated_by = Column(Integer, nullable=False)  # Sales executive ID
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    template = relationship("FormTemplate", back_populates="instances")
    responses = relationship("FormResponse", back_populates="form_instance")


class FormResponse(Base):
    __tablename__ = "form_responses"

    id = Column(Integer, primary_key=True, index=True)
    form_instance_id = Column(Integer, ForeignKey("form_instances.id"), nullable=False)
    form_field_id = Column(Integer, ForeignKey("form_fields.id"), nullable=False)
    value = Column(String, nullable=True)  # Stores text, numbers, or S3 URLs

    form_instance = relationship("FormInstance", back_populates="responses")
    form_field = relationship("FormField")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text, nullable=False)
    title = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default="now()")
    notification_type = Column(String, nullable=False)  # e.g., 'system', 'task', 'message'
    
    user = relationship("User", foreign_keys=[user_id])
    sender = relationship("User", foreign_keys=[sender_id])