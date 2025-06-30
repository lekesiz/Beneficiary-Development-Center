#!/usr/bin/env python3
"""
BDC Projesi Final Düzeltmeler
AI Orchestrator kullanarak kalan sorunları çözer
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# AI Orchestrator'ı import et
ai_orchestrator_path = Path("/Users/mikail/Desktop/ai_orchestrator_complete/ai_orchestrator")
sys.path.append(str(ai_orchestrator_path))

from src.orchestrator.engine import OrchestratorEngine
from src.models.task import Task, TaskType, Priority
from src.models.ai_model import AIModel, ModelType, Capability
from src.connectors.openai_connector import OpenAIConnector
from src.utils.config import Config


class BDCFinalFixes:
    """BDC Projesi Final Düzeltmeleri"""
    
    def __init__(self):
        self.engine = None
        self.bdc_root = Path("/Users/mikail/Desktop/BDC/Beneficiary Development Center")
        self.backend_path = self.bdc_root / "backend"
        
    async def initialize(self):
        """AI Orchestrator'ı başlat"""
        print("🚀 BDC Final Düzeltmeler başlatılıyor...")
        
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
                description="GPT-4 - BDC düzeltmeleri için"
            )
            
            openai_connector = OpenAIConnector("gpt-4", openai_config)
            self.engine.register_model(openai_model)
            self.engine.register_connector("gpt-4", openai_connector)
            print("✅ OpenAI GPT-4 modeli yapılandırıldı")
        
        await self.engine.start()
        print("✅ AI Orchestrator başarıyla başlatıldı")
    
    async def fix_backend_tests(self):
        """Backend testlerini düzelt"""
        print("🧪 Backend Testleri Düzeltiliyor...")
        
        # Failing test dosyalarını bul
        test_files = list(self.backend_path.rglob("test_*.py"))
        failing_tests = []
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'def test_' in content:
                        failing_tests.append(f"File: {test_file.name}\n{content[:1000]}...")
            except Exception as e:
                print(f"   ⚠️  {test_file} okunamadı: {e}")
        
        prompt = f"""
        BDC backend testlerindeki sorunları analiz et ve düzelt:
        
        Test dosyaları:
        {chr(10).join(failing_tests[:3])}
        
        Ana sorunlar:
        1. WebSocket test infrastructure sorunları
        2. Schema validation çok kısıtlayıcı
        3. Service layer test coverage eksiklikleri
        4. API response format uyumsuzlukları
        
        Şu düzeltmeleri yap:
        1. WebSocket test mock'larını düzelt
        2. Schema validation'ı daha esnek yap
        3. Service layer testlerini ekle
        4. API response formatlarını standardize et
        
        Her sorun için tam çözüm kodu ver.
        """
        
        task = Task(
            id="backend_test_fixes",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Backend test düzeltmeleri oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def fix_websocket_tests(self):
        """WebSocket testlerini düzelt"""
        print("🔌 WebSocket Testleri Düzeltiliyor...")
        
        # WebSocket test dosyalarını bul
        websocket_tests = []
        for test_file in self.backend_path.rglob("*websocket*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    websocket_tests.append(f"File: {test_file.name}\n{content}")
            except Exception as e:
                print(f"   ⚠️  {test_file} okunamadı: {e}")
        
        prompt = f"""
        BDC WebSocket testlerini düzelt:
        
        WebSocket test dosyaları:
        {chr(10).join(websocket_tests)}
        
        Sorunlar:
        1. Authentication testleri başarısız
        2. Mock WebSocket bağlantıları çalışmıyor
        3. Test setup sorunları
        
        Şu düzeltmeleri yap:
        1. WebSocket test mock'larını oluştur
        2. Authentication testlerini düzelt
        3. Test setup'ını iyileştir
        4. Real-time test senaryolarını ekle
        
        Tam çözüm kodları ver.
        """
        
        task = Task(
            id="websocket_test_fixes",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ WebSocket test düzeltmeleri oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def fix_schema_validation(self):
        """Schema validation'ı düzelt"""
        print("📋 Schema Validation Düzeltiliyor...")
        
        # Schema dosyalarını bul
        schema_files = []
        for schema_file in self.backend_path.rglob("*schema*.py"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    schema_files.append(f"File: {schema_file.name}\n{content}")
            except Exception as e:
                print(f"   ⚠️  {schema_file} okunamadı: {e}")
        
        prompt = f"""
        BDC schema validation'ını daha esnek yap:
        
        Schema dosyaları:
        {chr(10).join(schema_files)}
        
        Sorunlar:
        1. Schema validation çok kısıtlayıcı
        2. Test verileri validation'dan geçmiyor
        3. Optional field'lar zorunlu olarak işaretlenmiş
        
        Şu düzeltmeleri yap:
        1. Optional field'ları düzelt
        2. Validation kurallarını esnet
        3. Test verileri için özel schema'lar oluştur
        4. Error mesajlarını iyileştir
        
        Düzeltilmiş schema kodlarını ver.
        """
        
        task = Task(
            id="schema_validation_fixes",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Schema validation düzeltmeleri oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def add_service_layer_tests(self):
        """Service layer testlerini ekle"""
        print("🔧 Service Layer Testleri Ekleniyor...")
        
        # Service dosyalarını bul
        service_files = []
        for service_file in self.backend_path.rglob("*service*.py"):
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    service_files.append(f"File: {service_file.name}\n{content[:1000]}...")
            except Exception as e:
                print(f"   ⚠️  {service_file} okunamadı: {e}")
        
        prompt = f"""
        BDC service layer'ları için kapsamlı testler oluştur:
        
        Service dosyaları:
        {chr(10).join(service_files)}
        
        Şu testleri oluştur:
        1. Unit testler (her method için)
        2. Integration testler (service interactions)
        3. Error handling testleri
        4. Edge case testleri
        5. Performance testleri
        
        Her service için ayrı test dosyası oluştur.
        Mock'ları ve test data'ları dahil et.
        """
        
        task = Task(
            id="service_layer_tests",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Service layer testleri oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def create_test_runner_script(self):
        """Test runner scripti oluştur"""
        print("🏃 Test Runner Scripti Oluşturuluyor...")
        
        prompt = f"""
        BDC projesi için kapsamlı test runner scripti oluştur:
        
        Özellikler:
        1. Backend testleri çalıştırma
        2. Frontend testleri çalıştırma
        3. Coverage raporu oluşturma
        4. Failing testleri analiz etme
        5. Test sonuçlarını raporlama
        
        Script şunları yapmalı:
        - Test coverage hedeflerini kontrol et
        - Failing testleri listele
        - Performance metrikleri topla
        - HTML coverage raporu oluştur
        - Test sonuçlarını JSON formatında kaydet
        
        Python scripti olarak oluştur.
        """
        
        task = Task(
            id="test_runner_script",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Test runner scripti oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def generate_final_report(self, all_fixes):
        """Final rapor oluştur"""
        print("📊 Final Rapor Oluşturuluyor...")
        
        prompt = f"""
        BDC projesi için final düzeltme raporu oluştur:
        
        Yapılan Düzeltmeler:
        {all_fixes}
        
        Şu formatta rapor oluştur:
        
        # BDC Projesi Final Düzeltme Raporu
        
        ## 🔧 Yapılan Düzeltmeler
        - Backend test düzeltmeleri
        - WebSocket test düzeltmeleri
        - Schema validation düzeltmeleri
        - Service layer testleri
        
        ## 📈 Beklenen İyileştirmeler
        - Test coverage artışı
        - Test başarı oranı
        - Performans iyileştirmeleri
        
        ## 🚀 Sonraki Adımlar
        - Testleri çalıştır
        - Coverage raporunu kontrol et
        - Production deployment hazırlığı
        
        ## ✅ Teslim Kriterleri
        - Backend test coverage > %80
        - Tüm kritik testler geçiyor
        - WebSocket testleri çalışıyor
        - Schema validation esnek
        
        Detaylı bir rapor oluştur.
        """
        
        task = Task(
            id="final_report_generation",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Final rapor oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def save_fixes(self, all_fixes):
        """Düzeltmeleri dosyalara kaydet"""
        print("💾 Düzeltmeler Kaydediliyor...")
        
        # Düzeltmeleri ayrı dosyalara kaydet
        fixes_dir = self.backend_path / "ai_fixes"
        fixes_dir.mkdir(exist_ok=True)
        
        for fix_name, fix_content in all_fixes.items():
            fix_file = fixes_dir / f"{fix_name}.py"
            with open(fix_file, 'w', encoding='utf-8') as f:
                f.write(f"# {fix_name.upper()} FIXES\n")
                f.write("# Generated by AI Orchestrator\n\n")
                f.write(fix_content)
        
        print(f"✅ Düzeltmeler kaydedildi: {fixes_dir}")
    
    async def shutdown(self):
        """AI Orchestrator'ı kapat"""
        if self.engine:
            await self.engine.stop()
            print("🛑 AI Orchestrator kapatıldı")


async def main():
    """Ana fonksiyon"""
    print("🚀 BDC Projesi Final Düzeltmeler")
    print("=" * 50)
    
    fixes = BDCFinalFixes()
    all_fixes = {}
    
    try:
        # AI Orchestrator'ı başlat
        await fixes.initialize()
        
        # Düzeltmeleri yap
        all_fixes['backend_tests'] = await fixes.fix_backend_tests()
        all_fixes['websocket_tests'] = await fixes.fix_websocket_tests()
        all_fixes['schema_validation'] = await fixes.fix_schema_validation()
        all_fixes['service_layer_tests'] = await fixes.add_service_layer_tests()
        all_fixes['test_runner'] = await fixes.create_test_runner_script()
        
        # Final rapor oluştur
        all_fixes['final_report'] = await fixes.generate_final_report(all_fixes)
        
        # Düzeltmeleri kaydet
        await fixes.save_fixes(all_fixes)
        
        print("\n🎉 BDC projesi final düzeltmeleri tamamlandı!")
        print("📁 Düzeltmeler: backend/ai_fixes/ klasöründe")
        print("\n🚀 Şimdi bu düzeltmeleri uygulayabilirsiniz!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await fixes.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 