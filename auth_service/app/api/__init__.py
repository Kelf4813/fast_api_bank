from app.api.auth import router


def include_router(app):
    app.include_router(router)
