from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Numeric,
    UniqueConstraint,
    Float,
    DateTime,
)

from sqlalchemy.sql import func
from sqlalchemy import Boolean, ForeignKey
from infrastructure.database.connection import Base
from sqlalchemy.orm import relationship
class PublicationRelationBaseEntity(Base):
    __tablename__ = "publication_relation_bases"
    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=True)
    price = Column(Numeric, nullable=True, default=0)
    permalink = Column(Text, nullable=True)
    is_kit = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PublicationRelationComponentEntity(Base):
    __tablename__ = "publication_relation_components"
    id = Column(Integer, primary_key=True, index=True)
    base_publication_id = Column(String(50), nullable=False, index=True)
    publication_id = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=True)
    price = Column(Numeric, nullable=True, default=0)
    permalink = Column(Text, nullable=True)
    is_kit = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PublicationRelationKitEntity(Base):
    __tablename__ = "publication_relation_kits"
    id = Column(Integer, primary_key=True, index=True)
    base_publication_id = Column(String(50), nullable=False, index=True)
    publication_id = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=True)
    price = Column(Numeric, nullable=True, default=0)
    permalink = Column(Text, nullable=True)
    is_kit = Column(Boolean, nullable=False, default=True)
    assigned_count = Column(Integer, nullable=True, default=0)
    required_assignments = Column(Integer, nullable=True, default=2)
    double_unit_same_product = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PublicationRelationUnassignedKitEntity(Base):
    __tablename__ = "publication_relation_unassigned_kits"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=True)
    price = Column(Numeric, nullable=True, default=0)
    permalink = Column(Text, nullable=True)
    is_kit = Column(Boolean, nullable=False, default=True)
    reason = Column(Text, nullable=True, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
class DescriptionVariantEntity(Base):
    __tablename__ = "description_variants"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String(50),
        nullable=False,
        index=True,
    )

    variant_type = Column(
        String(50),
        nullable=False,
    )

    text = Column(
        Text,
        nullable=False,
        default="",
    )

    status = Column(
        String(20),
        nullable=False,
        default="draft",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "publication_id",
            "variant_type",
            name="uq_description_variant_publication_type",
        ),
    )


class MeliPublicationEntity(Base):
    __tablename__ = "meli_publications"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(Text, nullable=False)

    thumbnail = Column(Text, nullable=True)
    permalink = Column(Text, nullable=True)

    price = Column(
        Numeric,
        nullable=True,
        default=0,
    )

    status = Column(String(50), nullable=True)

    category_id = Column(
        String(50),
        nullable=True,
    )

    listing_type_id = Column(
        String(50),
        nullable=True,
    )

    currency_id = Column(
        String(10),
        nullable=True,
        default="CLP",
    )

    current_description = Column(
        Text,
        nullable=True,
        default="",
    )

    active_description_type = Column(
        String(50),
        nullable=True,
    )

    last_synced_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    shipping_mode = Column(String(50), nullable=True)

    logistic_type = Column(String(50), nullable=True)

    free_shipping = Column(Boolean, nullable=False, default=False)
    
class ProductCostEntity(Base):
    __tablename__ = "product_costs"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String,
        ForeignKey("meli_publications.publication_id"),
        unique=True,
        nullable=False,
    )

    disassembly_stock = Column(Integer, default=0)
    disassembly_unit_cost = Column(Float, default=0)

    direct_stock = Column(Integer, default=0)
    direct_purchase_cost = Column(Float, default=0)
    direct_discount_percent = Column(Float, default=0)
    direct_shipping_cost = Column(Float, default=0)

    calculated_kit_product_cost = Column(Float, nullable=True, default=None)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    publication = relationship(
        "MeliPublicationEntity",
        backref="cost_data",
    )
class MarketplaceCostEntity(Base):
    __tablename__ = "marketplace_costs"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String,
        ForeignKey("meli_publications.publication_id"),
        unique=True,
        nullable=False,
        index=True,
    )

    sale_fee_amount = Column(Float, default=0)
    listing_fee_amount = Column(Float, default=0)
    total_meli_cost = Column(Float, default=0)

    percentage_fee = Column(Float, default=0)

    shipping_list_cost = Column(Float, default=0)
    shipping_seller_cost = Column(Float, default=0)
    billable_weight = Column(Float, default=0)

    total_marketplace_cost = Column(Float, default=0)

    currency_id = Column(String(10), default="CLP")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    publication = relationship(
        "MeliPublicationEntity",
        backref="marketplace_cost",
    )
class PublicationProfitabilityEntity(Base):
    __tablename__ = "publication_profitability"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String,
        ForeignKey("meli_publications.publication_id"),
        unique=True,
        nullable=False,
        index=True,
    )

    price = Column(Float, default=0)

    sale_fee_amount = Column(Float, default=0)
    shipping_seller_cost = Column(Float, default=0)
    total_marketplace_cost = Column(Float, default=0)

    disassembly_unit_cost = Column(Float, default=0)
    disassembly_total_cost = Column(Float, default=0)
    disassembly_profit = Column(Float, default=0)
    disassembly_margin_percent = Column(Float, default=0)

    direct_unit_cost = Column(Float, default=0)
    direct_total_cost = Column(Float, default=0)
    direct_profit = Column(Float, default=0)
    direct_margin_percent = Column(Float, default=0)

    # RENTABILIDAD KIT
    calculated_kit_product_cost = Column(Float, default=0)
    kit_total_cost = Column(Float, default=0)
    kit_profit = Column(Float, default=0)
    kit_margin_percent = Column(Float, default=0)

    recommended_cost_type = Column(String(30), default="none")
    recommended_profit = Column(Float, default=0)
    recommended_margin_percent = Column(Float, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
class PublicationSaleEntity(Base):
    __tablename__ = "publication_sales"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String,
        ForeignKey("meli_publications.publication_id"),
        nullable=False,
        index=True,
    )

    order_id = Column(String(50), nullable=False, unique=True, index=True)

    quantity = Column(Integer, nullable=False, default=0)

    unit_price = Column(Float, nullable=False, default=0)

    total_amount = Column(Float, nullable=False, default=0)

    sale_date = Column(DateTime(timezone=True), nullable=False)

    status = Column(String(50), nullable=True)

    currency_id = Column(String(10), nullable=True, default="CLP")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    publication = relationship(
        "MeliPublicationEntity",
        backref="sales",
    )
class PublicationAdvertisingTargetEntity(Base):
    __tablename__ = "publication_advertising_targets"

    id = Column(Integer, primary_key=True, index=True)

    publication_id = Column(
        String,
        ForeignKey("meli_publications.publication_id"),
        unique=True,
        nullable=False,
        index=True,
    )

    target_acos = Column(Float, nullable=True, default=None)

    notes = Column(Text, nullable=True, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    publication = relationship(
        "MeliPublicationEntity",
        backref="advertising_target",
    )