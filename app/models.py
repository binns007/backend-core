from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Enum as SQLAlchemyEnum,DECIMAL,DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class RoleEnum(enum.Enum):
    admin = "admin"
    dealer = "dealer"
    sales_executive = "sales_executive"
    finance = "finance" 
    rto = "rto"
    customer = "customer"
    
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

    vehicles = relationship("Vehicle", back_populates="dealership")
    roles = relationship("DealershipRole", back_populates="dealership")
    # payments = relationship("Payment", back_populates="dealership")
    branches = relationship("Branch", back_populates="dealership")
    users = relationship("User", back_populates="dealership",foreign_keys="[User.dealership_id]")
    customers = relationship("Customer", back_populates="dealership")
    creator = relationship("User", back_populates="created_dealership",foreign_keys="[Dealership.creator_id]")
    form_templates = relationship("FormTemplate", back_populates="dealership")  


class DealershipRole(Base):
    __tablename__ = "dealership_roles"
    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id"), nullable=False)
    role = Column(SQLAlchemyEnum(RoleEnum, name='role_enum', create_type=False), nullable=False)
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



# class Payment(Base):
#     __tablename__ = "payments"
    
#     id = Column(Integer, primary_key=True, index=True)
#     dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"))  # Add this foreign key

#     status = Column(String, default="Pending")  # Payment status: Pending, Completed, etc.
#     amount = Column(DECIMAL(10, 2))  # Amount paid
#     payment_date = Column(TIMESTAMP, nullable=True)  # Date of payment
#     transaction_id = Column(String, nullable=True)  # Optional transaction ID

#     dealership = relationship("Dealership", back_populates="payments")

    

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
    form_instance_id = Column(Integer, ForeignKey("form_instances.id"), nullable=False)
    total_price = Column(Float, nullable=False)  # Calculated total amount
    amount_paid = Column(Float, default=0, nullable=False)
    balance_amount = Column(Float, default=0, nullable=False)


    dealership_id = Column(Integer, ForeignKey("dealerships.id", ondelete="CASCADE"))
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default="now()")
    
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    vehicle = relationship("Vehicle", back_populates="customers")
    form_instance = relationship("FormInstance", back_populates="customer")
    # payments = relationship("CustomerPayment", back_populates="customer")


    dealership = relationship("Dealership", back_populates="customers")
    branch = relationship("Branch", back_populates="customers")
    user = relationship("User")




class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    dealership_id = Column(Integer, ForeignKey("dealerships.id"), nullable=False)
    name = Column(String, nullable=False)
    first_service_time = Column(String, nullable=True)
    service_kms = Column(Integer, nullable=True)
    total_price = Column(Float, nullable=False)

    dealership = relationship("Dealership", back_populates="vehicles")
    customers = relationship("Customer", back_populates="vehicle")



class FilledByEnum(str, enum.Enum):
    sales_executive = "sales_executive"
    customer = "customer"

class FieldTypeEnum(str, enum.Enum):
    text = "text"
    number = "number"
    image = "image"
    date = "date"
    amount = "amount"
    vehicle = "vehicle"

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
    field_type = Column(SQLAlchemyEnum(FieldTypeEnum, name='field_type_enum'), nullable=False)
    is_required = Column(Boolean, default=True)
    filled_by = Column(SQLAlchemyEnum(FilledByEnum, name='filled_by_enum'), nullable=False)
    order = Column(Integer, nullable=False)

    template = relationship("FormTemplate", back_populates="fields")


class FormInstance(Base):
    __tablename__ = "form_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("form_templates.id"), nullable=False)
    generated_by = Column(Integer, nullable=False)  # Sales executive ID
    customer_name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    customer_submitted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    customer_submitted = Column(Boolean,default=False, nullable=True)
    sales_verified = Column(Boolean,default=False, nullable=True)
    accounts_verified = Column(Boolean, default=False, nullable=True)
    
    customer = relationship("Customer", back_populates="form_instance", uselist=False)

    template = relationship("FormTemplate", back_populates="instances")
    responses = relationship("FormResponse", back_populates="form_instance")
    chat_session = relationship("ChatSession", back_populates="form_instance", uselist=False)


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
    notification_type = Column(String, nullable=False)  
    
    user = relationship("User", foreign_keys=[user_id])
    sender = relationship("User", foreign_keys=[sender_id])


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    form_instance_id = Column(Integer, ForeignKey("form_instances.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="active")  # active, closed
    created_at = Column(TIMESTAMP, server_default="now()")
    closed_at = Column(TIMESTAMP, nullable=True)
    
    form_instance = relationship("FormInstance", back_populates="chat_session")
    messages = relationship("ChatMessage", back_populates="session")
    employee = relationship("User", foreign_keys=[employee_id])

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender_type = Column(String, nullable=False)  # "customer" or "employee"
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for customer
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default="now()")
    
    session = relationship("ChatSession", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])