"""API blueprints. Every route is authenticated by the request hook in security.py
and authorised again inside the route (role permission + patient scope)."""


def register_blueprints(app):
    from . import (admin, ai, auth, beds, deliverables, documents, monitoring, orders, patients, portal, reports, scheduling, verify, workspaces)
    for mod in (auth, patients, scheduling, beds, orders, monitoring, documents, deliverables, portal, ai, workspaces, reports, admin, verify):
        app.register_blueprint(mod.bp)
