from fastapi import APIRouter

from cargoapi.api.v1.endpoints import auth, cargos, users

api_router_v1 = APIRouter()

_v1_routers = [
    users,
    auth,
    cargos,
]

for v1_route in _v1_routers:
    api_router_v1.include_router(
        v1_route.router,
        prefix='/api/v1',
    )
