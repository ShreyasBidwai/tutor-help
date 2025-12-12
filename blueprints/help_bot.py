"""Help Bot API Blueprint with RAG system"""
from flask import Blueprint, request, jsonify, session
from utils import require_login
from utils.rag_system import get_rag_system
import os

help_bot_bp = Blueprint('help_bot', __name__, url_prefix='')

@help_bot_bp.route('/api/help-bot/query', methods=['POST'])
@require_login
def help_bot_query():
    """Handle help bot queries using RAG system"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        context = data.get('context', '')
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Get user role
        user_role = session.get('role', 'tutor')
        
        # Get RAG system
        rag = get_rag_system()
        
        # Ensure index is loaded
        if rag.index is None or len(rag.qa_pairs) == 0:
            # Try to load existing index
            if os.path.exists(rag.faiss_index_path) and os.path.exists(rag.qa_data_path):
                import json as json_lib
                with open(rag.qa_data_path, 'r', encoding='utf-8') as f:
                    rag.qa_pairs = json_lib.load(f)
                import faiss
                rag.index = faiss.read_index(rag.faiss_index_path)
                if os.path.exists(rag.embeddings_path):
                    with open(rag.embeddings_path, 'rb') as f:
                        import pickle
                        rag.embeddings = pickle.load(f)
            else:
                return jsonify({
                    'success': False,
                    'error': 'RAG index not initialized. Please run build_rag_index.py first.',
                    'response': "I'm setting up my knowledge base. Please try again in a moment! 😊"
                }), 500
        
        # Get RAG response
        response_data = rag.get_rag_response(
            user_query=user_query,
            user_role=user_role,
            context=context
        )
        
        return jsonify({
            'success': True,
            'response': response_data['response'],
            'used_rag': response_data.get('used_rag', False),
            'similarity_scores': response_data.get('similarity_scores', []),
            'rag_context': response_data.get('rag_context', [])
        })
        
    except Exception as e:
        import traceback
        print(f"Error in help_bot_query: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your query',
            'response': "I'm here to help! Could you please rephrase your question? 😊"
        }), 500
