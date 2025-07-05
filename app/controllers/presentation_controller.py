from datetime import datetime

from flask import Blueprint, request, jsonify, send_file
from ..services.content_service import ContentService
from ..services.pptx_service import PPTXService
from ..models.presentation import Presentation
from ..utils.decorators import validate_json
from ..utils.exceptions import InvalidRequestError
import uuid
from app import limiter

bp = Blueprint('presentation', __name__, url_prefix='/api/v1/presentations')

presentations = {}  # In-memory storage for demo purposes

# Health check endpoint
@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'presentations_count': len(presentations)
    }), 200


@bp.route('', methods=['POST'])
@validate_json({
    'type': 'object',
    'properties': {
        'topic': {'type': 'string', 'minLength': 3},
        'num_slides': {'type': 'integer', 'minimum': 1, 'maximum': 20},
        'custom_content': {'type': 'string'},
        'theme': {
            'type': 'object',
            'properties': {
                'primary_color': {'type': 'string'},
                'secondary_color': {'type': 'string'},
                'font': {'type': 'string'}
            }
        }
    },
    'required': ['topic']
})
@limiter.limit("5 per minute")
def create_presentation():
    data = request.json
    presentation_id = str(uuid.uuid4())

    # Generate content
    content_service = ContentService()
    if 'custom_content' in data and data['custom_content']:
        content = data['custom_content']
    else:
        content = content_service.generate_content(
            topic=data['topic'],
            num_slides=data.get('num_slides', 5)
        )

    # Create presentation
    presentation = Presentation(
        id=presentation_id,
        topic=data['topic'],
        content=content,
        theme=data.get('theme', {})
    )
    presentations[presentation_id] = presentation

    return jsonify({
        'id': presentation_id,
        'topic': presentation.topic,
        'status': 'created'
    }), 201


@bp.route('/<string:presentation_id>', methods=['GET'])
def get_presentation(presentation_id):
    if presentation_id not in presentations:
        raise InvalidRequestError('Presentation not found', 404)

    presentation = presentations[presentation_id]
    return jsonify(presentation.to_dict())


@bp.route('/<string:presentation_id>/download', methods=['GET'])
def download_presentation(presentation_id):
    if presentation_id not in presentations:
        raise InvalidRequestError('Presentation not found', 404)

    presentation = presentations[presentation_id]
    pptx_service = PPTXService()
    file_path = pptx_service.generate_pptx(presentation)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{presentation.topic}.pptx",
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )


@bp.route('/<string:presentation_id>/configure', methods=['POST'])
@validate_json({
    'type': 'object',
    'properties': {
        'num_slides': {'type': 'integer', 'minimum': 1, 'maximum': 20},
        'theme': {
            'type': 'object',
            'properties': {
                'primary_color': {'type': 'string'},
                'secondary_color': {'type': 'string'},
                'font': {'type': 'string'}
            }
        },
        'layout_changes': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'slide_number': {'type': 'integer'},
                    'layout': {'type': 'string'}
                }
            }
        }
    }
})
def configure_presentation(presentation_id):
    if presentation_id not in presentations:
        raise InvalidRequestError('Presentation not found', 404)

    data = request.json
    presentation = presentations[presentation_id]

    if 'num_slides' in data:
        presentation.num_slides = data['num_slides']

    if 'theme' in data:
        presentation.theme.update(data['theme'])

    if 'layout_changes' in data:
        for change in data['layout_changes']:
            presentation.update_slide_layout(
                change['slide_number'],
                change['layout']
            )

    return jsonify(presentation.to_dict())