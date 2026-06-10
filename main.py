from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.database.connection import Base, engine
from api.routes import exposure_router
from api.routes.mercadolibre_oauth import router as meli_oauth_router
from api.routes.publications import router as publications_router
from api.routes.descriptions import router as descriptions_router
from api.routes.publication_relations import router as publication_relations_router
from api.routes.publications import router as publications_router
from api.routes.costs import router as costs_router
from api.routes.shipping import router as shipping_router
from api.routes.base_costs import router as base_costs_router
from api.routes.profitability import router as profitability_router
from api.routes.kit_costs import router as kit_costs_router
from api.routes.publication_groups import router as publication_groups_router
from api.routes.sales import router as sales_router
from api.routes.advertising_targets import advertising_targets_router
from api.routes.falabella_migration import falabella_migration_router
app = FastAPI()
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(descriptions_router)
app.include_router(exposure_router)
app.include_router(meli_oauth_router)
app.include_router(costs_router)
app.include_router(publications_router)
app.include_router(publication_relations_router)
app.include_router(shipping_router)
app.include_router(base_costs_router)
app.include_router(profitability_router)
app.include_router(kit_costs_router)
app.include_router(publication_groups_router)
app.include_router(sales_router)
app.include_router(advertising_targets_router)
app.include_router(falabella_migration_router)