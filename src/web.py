import os
import secrets
import threading
from typing import Dict, Tuple

from flask import Flask, jsonify, render_template, request, session

from src import MODEL_NAMES_DIALOG
from src.dialog_manager import (
    INTO_SENTENCE,
    WebDialogSession,
    create_web_dialog_session,
    process_web_message,
)
from src.enums.match_type import MatchType

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

_conversation_lock = threading.RLock()
_conversations: Dict[str, Tuple[WebDialogSession, str, MatchType]] = {}


def _new_conversation(model_name: str = "rb", match_type: MatchType = MatchType.LEVENSHTEIN) -> str:
    conversation_id = secrets.token_urlsafe(32)
    _conversations[conversation_id] = (create_web_dialog_session(), model_name, match_type)
    session["conversation_id"] = conversation_id
    return conversation_id


def _current_conversation() -> Tuple[str, WebDialogSession, str, MatchType]:
    conversation_id = session.get("conversation_id")
    if conversation_id not in _conversations:
        conversation_id = _new_conversation()
    conversation, model_name, match_type = _conversations[conversation_id]
    return conversation_id, conversation, model_name, match_type


@app.get("/")
def index():
    with _conversation_lock:
        _, _, model_name, match_type = _current_conversation()
    return render_template(
        "index.html",
        greeting=INTO_SENTENCE,
        models=list(MODEL_NAMES_DIALOG),
        match_types=list(MatchType),
        selected_model=model_name,
        selected_match_type=match_type,
    )


@app.post("/api/message")
def send_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object containing a message."), 400

    utterance = data.get("message")
    if not isinstance(utterance, str) or not utterance.strip():
        return jsonify(error="Message must not be empty."), 400
    if len(utterance) > 1000:
        return jsonify(error="Message must be 1000 characters or fewer."), 400

    with _conversation_lock:
        _, conversation, model_name, match_type = _current_conversation()
        response = process_web_message(
            conversation,
            model_name,
            match_type,
            utterance.strip(),
        )
        return jsonify(response=response, state=conversation.state.value)


@app.post("/api/settings")
def update_settings():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object containing model and match_type."), 400

    model_name = data.get("model")
    match_type_name = data.get("match_type")
    if not isinstance(model_name, str) or model_name not in MODEL_NAMES_DIALOG:
        return jsonify(error="Select a supported dialog model."), 400
    try:
        match_type = MatchType(match_type_name)
    except (TypeError, ValueError):
        return jsonify(error="Select a supported matching method."), 400

    with _conversation_lock:
        conversation_id, conversation, _, _ = _current_conversation()
        _conversations[conversation_id] = (conversation, model_name, match_type)
    return jsonify(model=model_name, match_type=match_type.value)


@app.post("/api/reset")
def reset_conversation():
    with _conversation_lock:
        _, _, model_name, match_type = _current_conversation()
        _new_conversation(model_name, match_type)
    return jsonify(greeting=INTO_SENTENCE)


if __name__ == "__main__":
    app.run()
