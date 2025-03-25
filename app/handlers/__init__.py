from handlers.users import router as users_router
from handlers.auth import router as auth_router
from handlers.links import router as links_router

routers = [users_router, auth_router, links_router]
