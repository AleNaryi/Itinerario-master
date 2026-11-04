from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.model.chat_model import ChatModel
from app.helpers.chat_knowledge import ChatKnowledge

bp = Blueprint('chat', __name__, url_prefix='/asistente')


@bp.route('/', methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        return jsonify({'error': 'No autenticado'}), 401

    if request.method == 'GET':
        historial = ChatModel().historial(current_user.id, limite=20)
        return jsonify({
            'nombre': ChatKnowledge.NOMBRE,
            'historial': historial,
        })

    mensaje = request.form.get('mensaje', '').strip()
    if not mensaje:
        return jsonify({'error': 'Escribe un mensaje'}), 400

    resultado = ChatKnowledge.procesar(mensaje, current_user)

    ChatModel().guardar(
        usuario_id=current_user.id,
        mensaje=mensaje,
        respuesta=resultado['respuesta'],
        contexto={'intencion': resultado['intencion'], 'confianza': resultado['confianza']},
    )

    return jsonify({
        'respuesta': resultado['respuesta'],
        'timestamp': None,
    })
