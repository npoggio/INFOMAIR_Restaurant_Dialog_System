import os
import secrets
import threading
from dataclasses import dataclass
from typing import Dict

from flask import Flask, jsonify, render_template, request, session

from src import MODEL_NAMES_DIALOG
from src.dialog_manager import (
    ALLOWED_PRINT_STYLES,
    INTO_SENTENCE,
    TASKS,
    WebDialogSession,
    create_web_dialog_session,
    process_web_message,
)
from src.enums.match_type import MatchType
from src.utils.logger import Logger

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

_conversation_lock = threading.RLock()


@dataclass
class WebConversation:
    dialog: WebDialogSession
    model_name: str
    match_type: MatchType
    config: str
    participant_code: str | None = None
    logger: Logger | None = None


_conversations: Dict[str, WebConversation] = {}
_config_options = {}
for _style_index, _style in enumerate(ALLOWED_PRINT_STYLES, start=1):
    for _task_index, _task in enumerate(TASKS):
        _config = f"{_style_index}{chr(ord('a') + _task_index)}"
        _config_options[_config] = {
            "value": _config,
            "label": _config,
            "print_style": _style,
            "task_index": _task_index,
            "task_value": _task,
        }


def _new_conversation(
    model_name: str = "rb",
    match_type: MatchType = MatchType.LEVENSHTEIN,
    config: str = "1a",
    participant_code: str | None = None,
    logger: Logger | None = None,
) -> str:
    conversation_id = secrets.token_urlsafe(32)
    _conversations[conversation_id] = WebConversation(
        dialog=create_web_dialog_session(),
        model_name=model_name,
        match_type=match_type,
        config=config,
        participant_code=participant_code,
        logger=logger,
    )
    session["conversation_id"] = conversation_id
    return conversation_id


def _current_conversation() -> tuple[str, WebConversation]:
    conversation_id = session.get("conversation_id")
    if conversation_id not in _conversations:
        conversation_id = _new_conversation()
    return conversation_id, _conversations[conversation_id]


def _write_parameters(conversation: WebConversation) -> None:
    if conversation.logger is None:
        return
    config_option = _config_options[conversation.config]
    conversation.logger.write_parameters(
        f"participant_code={conversation.participant_code}; "
        f"model={conversation.model_name}; "
        f"match_type={conversation.match_type.value}; "
        f"config={conversation.config}; "
        f"printstyle={config_option['print_style']}; "
        f"task={config_option['task_index']}"
    )


@app.get("/")
def index():
    with _conversation_lock:
        _, conversation = _current_conversation()
        config_option = _config_options[conversation.config]
    return render_template(
        "index.html",
        greeting=INTO_SENTENCE,
        models=list(MODEL_NAMES_DIALOG),
        match_types=list(MatchType),
        configs=list(_config_options.values()),
        selected_model=conversation.model_name,
        selected_match_type=conversation.match_type,
        selected_config=conversation.config,
        task_value=config_option["task_value"],
        participant_code=conversation.participant_code or "",
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
        _, conversation = _current_conversation()
        if conversation.participant_code is None:
            return jsonify(error="Save a participant code before starting the conversation."), 400
        if conversation.logger is not None:
            conversation.logger.write_user_msg(utterance.strip())
        response = process_web_message(
            conversation.dialog,
            conversation.model_name,
            conversation.match_type,
            utterance.strip(),
        )
        if conversation.logger is not None:
            conversation.logger.write_sys_msg(response)
        return jsonify(
            response=response,
            state=conversation.dialog.state.value,
            print_style=_config_options[conversation.config]["print_style"],
        )


@app.post("/api/settings")
def update_settings():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object containing model and match_type."), 400

    model_name = data.get("model")
    match_type_name = data.get("match_type")
    config = data.get("config")
    if not isinstance(model_name, str) or model_name not in MODEL_NAMES_DIALOG:
        return jsonify(error="Select a supported dialog model."), 400
    try:
        match_type = MatchType(match_type_name)
    except (TypeError, ValueError):
        return jsonify(error="Select a supported matching method."), 400
    if not isinstance(config, str) or config not in _config_options:
        return jsonify(error="Select a supported dialog configuration."), 400

    with _conversation_lock:
        _, conversation = _current_conversation()
        task_changed = (
            _config_options[conversation.config]["task_index"]
            != _config_options[config]["task_index"]
        )
        conversation.model_name = model_name
        conversation.match_type = match_type
        conversation.config = config
        _write_parameters(conversation)
    config_option = _config_options[config]
    return jsonify(
        model=model_name,
        match_type=match_type.value,
        config=config,
        print_style=config_option["print_style"],
        task_value=config_option["task_value"] if task_changed else None,
    )


@app.post("/api/participant")
def save_participant_code():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object containing participant_code."), 400

    participant_code = data.get("participant_code")
    if not isinstance(participant_code, str):
        return jsonify(error="Enter a valid participant code."), 400
    participant_code = participant_code.strip()
    if not participant_code or len(participant_code) > 100 or not participant_code.isprintable():
        return jsonify(error="Participant code must be printable and 1–100 characters long."), 400

    with _conversation_lock:
        conversation_id, conversation = _current_conversation()
        if conversation.participant_code is not None:
            if participant_code != conversation.participant_code:
                return jsonify(error="This conversation already has a saved participant code."), 409
            return jsonify(participant_code=conversation.participant_code)

        os.makedirs("logs", exist_ok=True)
        conversation.participant_code = participant_code
        conversation.logger = Logger(log_file=f"logs/web_{conversation_id}.log")
        _write_parameters(conversation)
    return jsonify(participant_code=participant_code)


@app.post("/api/reset")
def reset_conversation():
    with _conversation_lock:
        _, conversation = _current_conversation()
        _new_conversation(
            conversation.model_name,
            conversation.match_type,
            conversation.config,
            conversation.participant_code,
            conversation.logger,
        )
        if conversation.logger is not None:
            conversation.logger.write_sys_msg("New conversation started.")
    config_option = _config_options[conversation.config]
    return jsonify(greeting=INTO_SENTENCE, task_value=config_option["task_value"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "1738")))
