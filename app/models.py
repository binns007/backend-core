from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Enum as SQLAlchemyEnum,DECIMAL,DateTime, Boolean
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.ext.declarative import declarative_base

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
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Name of the template
    dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"))

    fields = relationship("FormField", back_populates="template", cascade="all, delete-orphan")

class FormField(Base):
    __tablename__ = "form_fields"
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("form_templates.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)           # Field name (e.g., "License Number")
    field_type = Column(SQLAlchemyEnum(FieldTypeEnum), nullable=False)  # Field type
    is_required = Column(Boolean, default=True)      # Is the field mandatory?
    filled_by = Column(SQLAlchemyEnum(FilledByEnum), nullable=False)  # Who fills this field
    order = Column(Integer, nullable=False)          # Order of the field in the form
    template = relationship("FormTemplate", back_populates="fields")