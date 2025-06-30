#!/usr/bin/env python3
"""
BDC AI Orchestrator Test Suite
"""

import pytest
import asyncio
import sys
from pathlib import Path

# BDC backend path'ini ekle
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from app.services.enhanced_ai_service import bdc_ai_service


class TestBDCAIOrchestrator:
    """BDC AI Orchestrator test sınıfı"""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Test öncesi ve sonrası işlemler"""
        # Test öncesi
        await bdc_ai_service.initialize()
        yield
        # Test sonrası
        await bdc_ai_service.shutdown()
    
    @pytest.mark.asyncio
    async def test_learning_path_generation(self):
        """Öğrenme yolu oluşturma testi"""
        user_profile = {
            'id': 'test_user_1',
            'name': 'Test User',
            'age': 25,
            'education_level': 'high_school',
            'interests': ['programming', 'technology'],
            'learning_style': 'visual'
        }
        
        goal = "Web geliştirme öğrenmek ve kariyer değişikliği yapmak"
        
        result = await bdc_ai_service.generate_learning_path(user_profile, goal)
        
        # Sonuçları kontrol et
        assert result is not None
        assert 'learning_path' in result
        assert 'confidence' in result
        assert 'model_used' in result
        assert 'cost' in result
        assert 'tokens_used' in result
        
        print(f"✅ Öğrenme yolu oluşturuldu:")
        print(f"   Model: {result['model_used']}")
        print(f"   Güven: {result['confidence']:.2f}")
        print(f"   Maliyet: ${result['cost']:.4f}")
        print(f"   Token: {result['tokens_used']}")
        print(f"   İçerik: {result['learning_path'][:200]}...")
    
    @pytest.mark.asyncio
    async def test_assessment_questions_generation(self):
        """Değerlendirme soruları oluşturma testi"""
        topic = "Python Programming"
        level = "beginner"
        count = 5
        
        result = await bdc_ai_service.generate_assessment_questions(topic, level, count)
        
        # Sonuçları kontrol et
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        
        print(f"✅ Değerlendirme soruları oluşturuldu:")
        print(f"   Konu: {topic}")
        print(f"   Seviye: {level}")
        print(f"   Soru sayısı: {len(result)}")
        
        for i, question in enumerate(result[:3], 1):
            print(f"   Soru {i}: {question.get('question', str(question))[:100]}...")
    
    @pytest.mark.asyncio
    async def test_content_generation(self):
        """Eğitim içeriği oluşturma testi"""
        topic = "JavaScript Fundamentals"
        format_type = "lesson_plan"
        
        result = await bdc_ai_service.generate_content(topic, format_type)
        
        # Sonuçları kontrol et
        assert result is not None
        assert 'content' in result
        assert 'confidence' in result
        assert 'model_used' in result
        assert 'cost' in result
        assert 'tokens_used' in result
        
        print(f"✅ Eğitim içeriği oluşturuldu:")
        print(f"   Konu: {topic}")
        print(f"   Format: {format_type}")
        print(f"   Model: {result['model_used']}")
        print(f"   Güven: {result['confidence']:.2f}")
        print(f"   Maliyet: ${result['cost']:.4f}")
        print(f"   İçerik: {result['content'][:200]}...")
    
    @pytest.mark.asyncio
    async def test_multiple_models_availability(self):
        """Çoklu model kullanılabilirliği testi"""
        # Engine'in durumunu kontrol et
        assert bdc_ai_service.engine is not None
        assert bdc_ai_service.is_initialized is True
        
        # Kayıtlı modelleri kontrol et
        registered_models = bdc_ai_service.engine.get_registered_models()
        assert len(registered_models) > 0
        
        print(f"✅ {len(registered_models)} model kayıtlı:")
        for model in registered_models:
            print(f"   - {model.name} ({model.id}) - Öncelik: {model.priority}")
    
    @pytest.mark.asyncio
    async def test_cost_optimization(self):
        """Maliyet optimizasyonu testi"""
        # Basit bir görev için maliyet kontrolü
        user_profile = {'id': 'test_cost', 'name': 'Cost Test User'}
        goal = "Test goal"
        
        result = await bdc_ai_service.generate_learning_path(user_profile, goal)
        
        # Maliyet kontrolü
        assert result['cost'] >= 0
        assert result['cost'] < 1.0  # Makul maliyet sınırı
        
        print(f"✅ Maliyet optimizasyonu çalışıyor:")
        print(f"   Toplam maliyet: ${result['cost']:.4f}")
        print(f"   Token kullanımı: {result['tokens_used']}")


# Manuel test fonksiyonları
async def manual_test_learning_path():
    """Manuel öğrenme yolu testi"""
    print("🎯 Manuel Öğrenme Yolu Testi")
    print("=" * 50)
    
    await bdc_ai_service.initialize()
    
    user_profile = {
        'id': 'manual_test_user',
        'name': 'Manuel Test Kullanıcısı',
        'age': 30,
        'education_level': 'university',
        'interests': ['data_science', 'machine_learning'],
        'learning_style': 'practical',
        'available_time': '10_hours_per_week'
    }
    
    goal = "Veri bilimi alanında kariyer yapmak ve Python, SQL, Machine Learning öğrenmek"
    
    try:
        result = await bdc_ai_service.generate_learning_path(user_profile, goal)
        
        print("📊 Sonuçlar:")
        print(f"Model: {result['model_used']}")
        print(f"Güven: {result['confidence']:.2f}")
        print(f"Maliyet: ${result['cost']:.4f}")
        print(f"Token: {result['tokens_used']}")
        print("\n📚 Öğrenme Yolu:")
        print(result['learning_path'])
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        await bdc_ai_service.shutdown()


async def manual_test_assessment():
    """Manuel değerlendirme testi"""
    print("🎯 Manuel Değerlendirme Testi")
    print("=" * 50)
    
    await bdc_ai_service.initialize()
    
    try:
        result = await bdc_ai_service.generate_assessment_questions(
            topic="Machine Learning Basics",
            level="intermediate",
            count=3
        )
        
        print("📊 Sonuçlar:")
        print(f"Soru sayısı: {len(result)}")
        print("\n❓ Sorular:")
        
        for i, question in enumerate(result, 1):
            print(f"\n{i}. {question.get('question', str(question))}")
            if 'options' in question:
                for j, option in enumerate(question['options'], 1):
                    print(f"   {j}. {option}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        await bdc_ai_service.shutdown()


if __name__ == "__main__":
    # Manuel testleri çalıştır
    print("🚀 BDC AI Orchestrator Manuel Testleri")
    print("=" * 60)
    
    # Öğrenme yolu testi
    asyncio.run(manual_test_learning_path())
    
    print("\n" + "=" * 60 + "\n")
    
    # Değerlendirme testi
    asyncio.run(manual_test_assessment()) 