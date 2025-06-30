#!/usr/bin/env python3
"""
BDC Evaluation Tests Fix
AI Orchestrator kullanarak evaluation testlerini düzeltir
"""

import os
import sys
import asyncio
from pathlib import Path

# AI Orchestrator'ı import et
ai_orchestrator_path = Path("/Users/mikail/Desktop/ai_orchestrator_complete/ai_orchestrator")
sys.path.append(str(ai_orchestrator_path))

from src.orchestrator.engine import OrchestratorEngine
from src.models.task import Task, TaskType, Priority
from src.models.ai_model import AIModel, ModelType, Capability
from src.connectors.openai_connector import OpenAIConnector
from src.utils.config import Config


class EvaluationTestFixer:
    """Evaluation Test Düzeltme Sınıfı"""
    
    def __init__(self):
        self.engine = None
        self.test_file = Path("/Users/mikail/Desktop/BDC/Beneficiary Development Center/backend/tests/test_evaluation_service.py")
        
    async def initialize(self):
        """AI Orchestrator'ı başlat"""
        print("🚀 Evaluation Test Düzeltme başlatılıyor...")
        
        config = Config()
        self.engine = OrchestratorEngine(config)
        
        # OpenAI modelini yapılandır
        openai_config = {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model_name': 'gpt-4',
            'rate_limit_rpm': 500,
            'rate_limit_tpm': 150000
        }
        
        if openai_config['api_key']:
            openai_model = AIModel(
                id="gpt-4",
                name="GPT-4",
                type=ModelType.OPENAI_GPT,
                capabilities=[Capability.CODE_GENERATION, Capability.ANALYSIS],
                priority=1,
                description="GPT-4 - Test düzeltmeleri için"
            )
            
            openai_connector = OpenAIConnector("gpt-4", openai_config)
            self.engine.register_model(openai_model)
            self.engine.register_connector("gpt-4", openai_connector)
            print("✅ OpenAI GPT-4 modeli yapılandırıldı")
        
        await self.engine.start()
        print("✅ AI Orchestrator başarıyla başlatıldı")
    
    async def analyze_test_file(self):
        """Test dosyasını analiz et"""
        print("🔍 Test Dosyası Analiz Ediliyor...")
        
        # Test dosyasını oku
        with open(self.test_file, 'r', encoding='utf-8') as f:
            test_content = f.read()
        
        prompt = f"""
        BDC evaluation test dosyasını analiz et ve sorunları belirle:
        
        Test dosyası:
        {test_content}
        
        Şu sorunları ara:
        1. Mock setup sorunları
        2. Database session sorunları
        3. Import sorunları
        4. Assertion sorunları
        5. Test isolation sorunları
        6. Missing test cases
        
        Her sorun için:
        - Sorunun açıklaması
        - Çözüm önerisi
        - Düzeltilmiş kod örneği
        
        Detaylı bir analiz raporu oluştur.
        """
        
        task = Task(
            id="test_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Test analizi tamamlandı (Model: {result.model_info['model_name']})")
        return result.content
    
    async def generate_fixed_tests(self, analysis):
        """Düzeltilmiş testleri oluştur"""
        print("🔧 Düzeltilmiş Testler Oluşturuluyor...")
        
        prompt = f"""
        BDC evaluation testlerini düzelt:
        
        Analiz Sonuçları:
        {analysis}
        
        Şu düzeltmeleri yap:
        1. Mock setup'larını iyileştir
        2. Database session yönetimini düzelt
        3. Import'ları düzenle
        4. Assertion'ları güçlendir
        5. Test isolation'ı sağla
        6. Eksik test case'leri ekle
        
        Düzeltilmiş test dosyasının tam kodunu ver.
        """
        
        task = Task(
            id="test_fixes",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Düzeltilmiş testler oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def create_test_helpers(self):
        """Test helper fonksiyonları oluştur"""
        print("🛠️ Test Helper Fonksiyonları Oluşturuluyor...")
        
        prompt = f"""
        BDC evaluation testleri için helper fonksiyonları oluştur:
        
        Şu helper'ları oluştur:
        1. Mock user factory
        2. Mock evaluation factory
        3. Mock question factory
        4. Database session mock
        5. Test data generators
        6. Assertion helpers
        
        Her helper için:
        - Fonksiyon açıklaması
        - Parametreler
        - Return değeri
        - Kullanım örneği
        
        Python kodu olarak oluştur.
        """
        
        task = Task(
            id="test_helpers",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Test helper'ları oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def save_fixes(self, analysis, fixed_tests, helpers):
        """Düzeltmeleri kaydet"""
        print("💾 Düzeltmeler Kaydediliyor...")
        
        # Analiz raporunu kaydet
        analysis_file = self.test_file.parent / "evaluation_test_analysis.md"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(f"# Evaluation Test Analizi\n\n{analysis}")
        
        # Düzeltilmiş testleri kaydet
        fixed_file = self.test_file.parent / "test_evaluation_service_fixed.py"
        with open(fixed_file, 'w', encoding='utf-8') as f:
            f.write(fixed_tests)
        
        # Helper'ları kaydet
        helpers_file = self.test_file.parent / "test_helpers.py"
        with open(helpers_file, 'w', encoding='utf-8') as f:
            f.write(helpers)
        
        print(f"✅ Düzeltmeler kaydedildi:")
        print(f"   - Analiz: {analysis_file}")
        print(f"   - Düzeltilmiş testler: {fixed_file}")
        print(f"   - Helper'lar: {helpers_file}")
    
    async def shutdown(self):
        """AI Orchestrator'ı kapat"""
        if self.engine:
            await self.engine.stop()
            print("🛑 AI Orchestrator kapatıldı")


async def main():
    """Ana fonksiyon"""
    print("🚀 BDC Evaluation Test Düzeltme")
    print("=" * 50)
    
    fixer = EvaluationTestFixer()
    
    try:
        # AI Orchestrator'ı başlat
        await fixer.initialize()
        
        # Test dosyasını analiz et
        analysis = await fixer.analyze_test_file()
        
        # Düzeltilmiş testleri oluştur
        fixed_tests = await fixer.generate_fixed_tests(analysis)
        
        # Test helper'larını oluştur
        helpers = await fixer.create_test_helpers()
        
        # Düzeltmeleri kaydet
        await fixer.save_fixes(analysis, fixed_tests, helpers)
        
        print("\n🎉 Evaluation test düzeltmeleri tamamlandı!")
        print("📁 Düzeltmeler tests/ klasöründe")
        print("\n🚀 Şimdi bu düzeltmeleri uygulayabilirsiniz!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await fixer.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 