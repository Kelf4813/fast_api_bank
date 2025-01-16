from app.api.transactions import router



def include_router(app):
    app.include_router(router)
