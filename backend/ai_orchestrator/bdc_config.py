# BDC AI Orchestrator Configuration
import os
from pathlib import Path

# BDC proje yolu
BDC_ROOT = Path(__file__).parent.parent

# AI Orchestrator konfigürasyonu
AI_ORCHESTRATOR_CONFIG = {
    'models': {
        'openai': {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model_name': 'gpt-4',
            'rate_limit_rpm': 500,
            'rate_limit_tpm': 150000
        },
        'gemini': {
            'api_key': os.getenv('GOOGLE_API_KEY'),
            'model_name': 'gemini-1.5-flash',
            'rate_limit_rpm': 300,
            'rate_limit_tpm': 100000
        }
    },
    'ollama': {
        'auto_discover': True,
        'api_base': 'http://localhost:11434'
    },
    'task_types': {
        'content_generation': ['gpt-4', 'gemini-1.5-flash'],
        'code_generation': ['ollama-codellama:34b', 'ollama-deepseek-coder:33b'],
        'analysis': ['gpt-4', 'gemini-1.5-flash'],
        'translation': ['gpt-4', 'gemini-1.5-flash'],
        'summarization': ['gpt-4', 'gemini-1.5-flash']
    },
    'validation': {
        'enable_cross_validation': True,
        'consensus_threshold': 0.8
    }
}

# BDC özel prompt'ları
BDC_PROMPTS = {
    'learning_path': {
        'system': "Sen BDC (Beneficiary Development Center) için öğrenme yolu oluşturan bir AI asistanısın.",
        'user_template': "Kullanıcı profili: {profile}. Hedef: {goal}. Bu kullanıcı için öğrenme yolu oluştur."
    },
    'assessment': {
        'system': "Sen BDC için değerlendirme soruları oluşturan bir AI asistanısın.",
        'user_template': "Konu: {topic}. Seviye: {level}. {count} adet değerlendirme sorusu oluştur."
    },
    'content': {
        'system': "Sen BDC için eğitim içeriği oluşturan bir AI asistanısın.",
        'user_template': "Konu: {topic}. Format: {format}. İçerik oluştur."
    }
}
