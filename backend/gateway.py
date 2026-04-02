from flask import Blueprint


gateway = Blueprint("gateway", __name__)


@gateway.post("/api/chatlogs/parse")
def parse_chatlogs():
    pass


@gateway.post("/api/souls/distill")
def distill_soul():
    pass


@gateway.post("/api/souls/save")
def save_soul():
    pass


@gateway.get("/api/souls")
def list_souls():
    pass


@gateway.get("/api/souls/<string:bro_name>")
def get_soul(bro_name: str):
    pass


@gateway.get("/api/souls/<string:bro_name>/export")
def export_soul(bro_name: str):
    pass


@gateway.delete("/api/souls/<string:bro_name>")
def delete_soul(bro_name: str):
    pass


@gateway.post("/api/sessions")
def create_session():
    pass


@gateway.get("/api/sessions")
def list_sessions():
    pass


@gateway.get("/api/sessions/<string:session_id>")
def get_session(session_id: str):
    pass


@gateway.post("/api/sessions/<string:session_id>/messages")
def create_session_message(session_id: str):
    pass


@gateway.delete("/api/sessions/<string:session_id>")
def delete_session(session_id: str):
    pass
