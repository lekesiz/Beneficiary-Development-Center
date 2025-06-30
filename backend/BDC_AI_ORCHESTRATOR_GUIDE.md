# 🚀 BDC AI Orchestrator Kullanım Rehberi

## 📋 Genel Bakış

BDC projeniz artık **AI Orchestrator** ile güçlendirildi! Bu sistem sayesinde:

- ✅ **15 farklı AI modeli** kullanabilirsiniz
- ✅ **Akıllı model seçimi** ile optimal performans
- ✅ **Maliyet optimizasyonu** ile bütçe kontrolü
- ✅ **Validation croisée** ile güvenilir sonuçlar
- ✅ **Otomatik fallback** ile kesintisiz hizmet

## 🔧 Kurulum ve Konfigürasyon

### 1. API Anahtarlarını Ayarlama

```bash
# Terminal'de API anahtarlarını ayarlayın
export OPENAI_API_KEY="your-openai-api-key-here"
export GOOGLE_API_KEY="your-google-api-key-here"

# Kalıcı olması için .env dosyasına ekleyin
echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env
echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" >> .env
```

### 2. Ollama Kurulumu (Opsiyonel)

```bash
# Ollama'yı kurun (macOS)
brew install ollama

# Modelleri indirin
ollama pull qwen2.5:72b
ollama pull codellama:34b
ollama pull deepseek-coder:33b
```

## 🎯 Kullanım Örnekleri

### 1. Öğrenme Yolu Oluşturma

```python
from app.services.enhanced_ai_service import bdc_ai_service

# Kullanıcı profili
user_profile = {
    'id': 'user_123',
    'name': 'Ahmet Yılmaz',
    'age': 28,
    'education_level': 'university',
    'interests': ['programming', 'web_development'],
    'learning_style': 'practical',
    'available_time': '15_hours_per_week'
}

# Hedef
goal = "Full-stack web geliştirici olmak ve React, Node.js öğrenmek"

# Öğrenme yolu oluştur
result = await bdc_ai_service.generate_learning_path(user_profile, goal)

print(f"Model: {result['model_used']}")
print(f"Güven: {result['confidence']:.2f}")
print(f"Maliyet: ${result['cost']:.4f}")
print(f"Öğrenme Yolu: {result['learning_path']}")
```

### 2. Değerlendirme Soruları Oluşturma

```python
# Değerlendirme soruları oluştur
questions = await bdc_ai_service.generate_assessment_questions(
    topic="JavaScript Fundamentals",
    level="intermediate",
    count=10
)

for i, question in enumerate(questions, 1):
    print(f"{i}. {question['question']}")
    if 'options' in question:
        for j, option in enumerate(question['options'], 1):
            print(f"   {j}. {option}")
```

### 3. Eğitim İçeriği Oluşturma

```python
# Eğitim içeriği oluştur
content = await bdc_ai_service.generate_content(
    topic="Python Data Structures",
    format_type="lesson_plan"
)

print(f"İçerik: {content['content']}")
print(f"Model: {content['model_used']}")
print(f"Maliyet: ${content['cost']:.4f}")
```

## 🔄 BDC API Entegrasyonu

### Mevcut AI Service'i Güncelleme

```python
# app/services/ai_service.py dosyasında

from app.services.enhanced_ai_service import bdc_ai_service

class AIService:
    def __init__(self):
        self.orchestrator = bdc_ai_service
    
    async def generate_learning_path(self, user_profile, goal):
        """Öğrenme yolu oluştur - AI Orchestrator ile"""
        return await self.orchestrator.generate_learning_path(user_profile, goal)
    
    async def generate_assessment(self, topic, level, count):
        """Değerlendirme oluştur - AI Orchestrator ile"""
        return await self.orchestrator.generate_assessment_questions(topic, level, count)
    
    async def generate_content(self, topic, format_type):
        """İçerik oluştur - AI Orchestrator ile"""
        return await self.orchestrator.generate_content(topic, format_type)
```

### API Endpoint'leri

```python
# app/api/ai_routes.py

from flask import Blueprint, request, jsonify
from app.services.enhanced_ai_service import bdc_ai_service

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/learning-path', methods=['POST'])
async def create_learning_path():
    """Öğrenme yolu oluştur"""
    data = request.get_json()
    
    result = await bdc_ai_service.generate_learning_path(
        user_profile=data['user_profile'],
        goal=data['goal']
    )
    
    return jsonify({
        'success': True,
        'data': result,
        'message': 'Öğrenme yolu başarıyla oluşturuldu'
    })

@ai_bp.route('/assessment', methods=['POST'])
async def create_assessment():
    """Değerlendirme oluştur"""
    data = request.get_json()
    
    questions = await bdc_ai_service.generate_assessment_questions(
        topic=data['topic'],
        level=data['level'],
        count=data.get('count', 10)
    )
    
    return jsonify({
        'success': True,
        'data': questions,
        'message': 'Değerlendirme soruları oluşturuldu'
    })

@ai_bp.route('/content', methods=['POST'])
async def create_content():
    """İçerik oluştur"""
    data = request.get_json()
    
    content = await bdc_ai_service.generate_content(
        topic=data['topic'],
        format_type=data['format']
    )
    
    return jsonify({
        'success': True,
        'data': content,
        'message': 'İçerik oluşturuldu'
    })
```

## 🧪 Test Etme

### Manuel Test

```bash
# Manuel test çalıştır
cd backend
python tests/test_ai_orchestrator.py
```

### Otomatik Test

```bash
# Pytest ile test et
pytest tests/test_ai_orchestrator.py -v
```

### API Test

```bash
# API endpoint'lerini test et
curl -X POST http://localhost:5000/api/ai/learning-path \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "id": "test_user",
      "name": "Test User",
      "age": 25,
      "education_level": "university",
      "interests": ["programming"]
    },
    "goal": "Web development öğrenmek"
  }'
```

## 📊 Performans İzleme

### Model Kullanım İstatistikleri

```python
# Model kullanım istatistiklerini al
stats = bdc_ai_service.engine.get_usage_statistics()

print("Model Kullanım İstatistikleri:")
for model_id, usage in stats.items():
    print(f"  {model_id}:")
    print(f"    Kullanım: {usage['requests']} istek")
    print(f"    Token: {usage['tokens']}")
    print(f"    Maliyet: ${usage['cost']:.4f}")
```

### Maliyet Takibi

```python
# Toplam maliyeti hesapla
total_cost = bdc_ai_service.engine.get_total_cost()
print(f"Toplam Maliyet: ${total_cost:.4f}")
```

## 🔧 Konfigürasyon Özelleştirme

### Model Önceliklerini Ayarlama

```python
# ai_orchestrator/bdc_config.py dosyasında

AI_ORCHESTRATOR_CONFIG = {
    'models': {
        'openai': {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model_name': 'gpt-4',
            'priority': 1,  # En yüksek öncelik
            'rate_limit_rpm': 500,
            'rate_limit_tpm': 150000
        },
        'gemini': {
            'api_key': os.getenv('GOOGLE_API_KEY'),
            'model_name': 'gemini-1.5-flash',
            'priority': 2,  # Orta öncelik
            'rate_limit_rpm': 300,
            'rate_limit_tpm': 100000
        }
    },
    'task_types': {
        'content_generation': ['gpt-4', 'gemini-1.5-flash'],
        'code_generation': ['ollama-codellama:34b', 'ollama-deepseek-coder:33b'],
        'analysis': ['gpt-4', 'gemini-1.5-flash'],
        'translation': ['gpt-4', 'gemini-1.5-flash']
    }
}
```

### Özel Prompt'lar Ekleme

```python
# BDC_PROMPTS'e yeni prompt'lar ekle

BDC_PROMPTS = {
    'learning_path': {
        'system': "Sen BDC için öğrenme yolu oluşturan bir AI asistanısın.",
        'user_template': "Kullanıcı profili: {profile}. Hedef: {goal}. Bu kullanıcı için öğrenme yolu oluştur."
    },
    'assessment': {
        'system': "Sen BDC için değerlendirme soruları oluşturan bir AI asistanısın.",
        'user_template': "Konu: {topic}. Seviye: {level}. {count} adet değerlendirme sorusu oluştur."
    },
    'content': {
        'system': "Sen BDC için eğitim içeriği oluşturan bir AI asistanısın.",
        'user_template': "Konu: {topic}. Format: {format}. İçerik oluştur."
    },
    # Yeni prompt ekle
    'career_advice': {
        'system': "Sen BDC için kariyer danışmanlığı yapan bir AI asistanısın.",
        'user_template': "Kullanıcı: {user_info}. Kariyer hedefi: {career_goal}. Kariyer tavsiyesi ver."
    }
}
```

## 🚨 Sorun Giderme

### Yaygın Sorunlar

#### 1. API Anahtarı Hatası
```bash
# API anahtarlarını kontrol et
echo $OPENAI_API_KEY
echo $GOOGLE_API_KEY

# Yeniden ayarla
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
```

#### 2. Ollama Bağlantı Hatası
```bash
# Ollama'nın çalıştığını kontrol et
curl http://localhost:11434/api/tags

# Ollama'yı yeniden başlat
ollama serve
```

#### 3. Model Bulunamadı Hatası
```python
# Mevcut modelleri kontrol et
models = bdc_ai_service.engine.get_registered_models()
for model in models:
    print(f"- {model.name} ({model.id})")
```

### Log Dosyaları

```bash
# Log dosyalarını kontrol et
tail -f logs/bdc_ai_orchestrator.log
```

## 📈 Performans Optimizasyonu

### 1. Model Seçimi Stratejisi

```python
# Task tipine göre model seçimi
TASK_MODEL_MAPPING = {
    'content_generation': ['gpt-4', 'gemini-1.5-flash'],
    'code_generation': ['ollama-codellama:34b', 'ollama-deepseek-coder:33b'],
    'analysis': ['gpt-4', 'gemini-1.5-flash'],
    'translation': ['gpt-4', 'gemini-1.5-flash']
}
```

### 2. Maliyet Optimizasyonu

```python
# Maliyet sınırları
COST_LIMITS = {
    'per_request': 0.10,  # İstek başına maksimum $0.10
    'daily': 10.0,        # Günlük maksimum $10
    'monthly': 100.0      # Aylık maksimum $100
}
```

### 3. Caching Stratejisi

```python
# Sonuçları cache'le
from functools import lru_cache

@lru_cache(maxsize=1000)
async def cached_generate_learning_path(user_profile_hash, goal):
    return await bdc_ai_service.generate_learning_path(user_profile, goal)
```

## 🎉 Sonuç

AI Orchestrator ile BDC projeniz artık:

- ✅ **15 farklı AI modeli** kullanabilir
- ✅ **Akıllı model seçimi** yapabilir
- ✅ **Maliyet optimizasyonu** sağlar
- ✅ **Yüksek güvenilirlik** sunar
- ✅ **Ölçeklenebilir** yapıya sahip

**Başarılı kullanımlar! 🚀** 