#!/usr/bin/env python3
"""
BDC Projesi AI Orchestrator Geliştirme Stratejisi
Bu script BDC projesini AI Orchestrator ile geliştirir
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any

# AI Orchestrator'ı import et
ai_orchestrator_path = Path("/Users/mikail/Desktop/ai_orchestrator_complete/ai_orchestrator")
sys.path.append(str(ai_orchestrator_path))

from src.orchestrator.engine import OrchestratorEngine
from src.models.task import Task, TaskType, Priority
from src.models.ai_model import AIModel, ModelType, Capability
from src.connectors.openai_connector import OpenAIConnector
from src.utils.config import Config


class BDCDevelopmentStrategy:
    """BDC Projesi Geliştirme Stratejisi"""
    
    def __init__(self):
        self.engine = None
        self.bdc_root = Path("/Users/mikail/Desktop/BDC/Beneficiary Development Center")
        self.backend_path = self.bdc_root / "backend"
        self.frontend_path = self.bdc_root / "frontend"
        
    async def initialize(self):
        """AI Orchestrator'ı başlat"""
        print("🚀 BDC Geliştirme Stratejisi başlatılıyor...")
        
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
                capabilities=[
                    Capability.CODE_GENERATION,
                    Capability.ANALYSIS,
                    Capability.TEXT_GENERATION,
                    Capability.CREATIVE_WRITING
                ],
                priority=1,
                description="GPT-4 - BDC geliştirme için"
            )
            
            openai_connector = OpenAIConnector("gpt-4", openai_config)
            self.engine.register_model(openai_model)
            self.engine.register_connector("gpt-4", openai_connector)
            print("✅ OpenAI GPT-4 modeli yapılandırıldı")
        
        await self.engine.start()
        print("✅ AI Orchestrator başarıyla başlatıldı")
    
    async def analyze_current_status(self):
        """Mevcut durumu analiz et"""
        print("🔍 BDC Projesi Mevcut Durum Analizi...")
        
        # Mevcut raporları oku
        reports = []
        for report_file in self.bdc_root.glob("*.md"):
            if "REPORT" in report_file.name or "STATUS" in report_file.name:
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        reports.append(f"## {report_file.name}\n{content[:1000]}...")
                except Exception as e:
                    print(f"   ⚠️  {report_file} okunamadı: {e}")
        
        prompt = f"""
        BDC projesinin mevcut durumunu analiz et:
        
        Mevcut raporlar:
        {chr(10).join(reports)}
        
        Şu konuları değerlendir:
        1. Proje tamamlanma oranı
        2. Mevcut sorunlar
        3. Eksik özellikler
        4. Test durumu
        5. Deployment hazırlığı
        6. Kritik iyileştirmeler
        7. Teslim için gerekli adımlar
        
        Kısa ve öz bir durum analizi oluştur.
        """
        
        task = Task(
            id="current_status_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Durum analizi tamamlandı (Model: {result.model_info['model_name']})")
        return result.content
    
    async def identify_critical_issues(self):
        """Kritik sorunları belirle"""
        print("🚨 Kritik Sorunlar Belirleniyor...")
        
        # Backend dosyalarını kontrol et
        backend_files = list(self.backend_path.rglob("*.py"))
        critical_files = []
        
        for file in backend_files:
            if any(keyword in file.name.lower() for keyword in ['main', 'app', 'api', 'config', 'database']):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        critical_files.append(f"File: {file.name}\n{content[:500]}...")
                except Exception as e:
                    print(f"   ⚠️  {file} okunamadı: {e}")
        
        prompt = f"""
        BDC projesindeki kritik sorunları belirle:
        
        Kritik dosyalar:
        {chr(10).join(critical_files[:5])}
        
        Şu kritik sorunları ara:
        1. Güvenlik açıkları
        2. Performans sorunları
        3. Kod kalitesi sorunları
        4. Eksik error handling
        5. Database sorunları
        6. API sorunları
        7. Test eksiklikleri
        8. Deployment sorunları
        
        Kritik sorunları öncelik sırasına göre listele.
        """
        
        task = Task(
            id="critical_issues_identification",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Kritik sorunlar belirlendi (Model: {result.model_info['model_name']})")
        return result.content
    
    async def generate_fix_plan(self, status_analysis, critical_issues):
        """Düzeltme planı oluştur"""
        print("📋 Düzeltme Planı Oluşturuluyor...")
        
        prompt = f"""
        BDC projesi için kapsamlı bir düzeltme planı oluştur:
        
        Mevcut Durum:
        {status_analysis}
        
        Kritik Sorunlar:
        {critical_issues}
        
        Şu formatta bir düzeltme planı oluştur:
        
        # BDC Projesi Düzeltme ve Teslim Planı
        
        ## 🚨 Acil Düzeltmeler (Bugün)
        - [ ] Sorun 1: Çözüm
        - [ ] Sorun 2: Çözüm
        
        ## ⚡ Hızlı İyileştirmeler (Yarın)
        - [ ] İyileştirme 1: Detay
        - [ ] İyileştirme 2: Detay
        
        ## 🔧 Orta Vadeli Düzeltmeler (Bu Hafta)
        - [ ] Düzeltme 1: Detay
        - [ ] Düzeltme 2: Detay
        
        ## 🎯 Teslim Hazırlığı (Gelecek Hafta)
        - [ ] Test tamamlama
        - [ ] Documentation
        - [ ] Deployment hazırlığı
        
        Her madde için:
        - Açıklama
        - Tahmini süre
        - Gerekli kaynaklar
        - Beklenen sonuç
        """
        
        task = Task(
            id="fix_plan_generation",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Düzeltme planı oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def create_automated_fixes(self, fix_plan):
        """Otomatik düzeltmeler oluştur"""
        print("🔧 Otomatik Düzeltmeler Oluşturuluyor...")
        
        prompt = f"""
        BDC projesi için otomatik düzeltme scriptleri oluştur:
        
        Düzeltme Planı:
        {fix_plan}
        
        Şu otomatik düzeltme scriptlerini oluştur:
        
        1. **Dependency Güncelleme Scripti**
        - requirements.txt güncelleme
        - Güvenlik açıklarını düzeltme
        - Version conflicts çözme
        
        2. **Kod Kalitesi Düzeltme Scripti**
        - PEP 8 uyumu
        - Import düzenleme
        - Error handling ekleme
        
        3. **Test Scripti**
        - Eksik testleri oluşturma
        - Test coverage artırma
        - Integration testleri
        
        4. **Deployment Scripti**
        - Docker yapılandırması
        - Environment setup
        - CI/CD pipeline
        
        Her script için tam kod örneği ver.
        """
        
        task = Task(
            id="automated_fixes_creation",
            type=TaskType.CODE_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Otomatik düzeltmeler oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def generate_final_delivery_plan(self, all_results):
        """Final teslim planı oluştur"""
        print("🎯 Final Teslim Planı Oluşturuluyor...")
        
        prompt = f"""
        BDC projesi için final teslim planı oluştur:
        
        Tüm Analizler:
        {json.dumps(all_results, indent=2, ensure_ascii=False)}
        
        Şu formatta profesyonel bir teslim planı oluştur:
        
        # BDC Projesi Final Teslim Planı
        
        ## 📊 Proje Durumu
        - Tamamlanma oranı
        - Kalite seviyesi
        - Test coverage
        
        ## 🎯 Teslim Kriterleri
        - Fonksiyonel gereksinimler
        - Performans kriterleri
        - Güvenlik standartları
        - Kullanılabilirlik kriterleri
        
        ## 📅 Teslim Takvimi
        - Aşama 1: Hazırlık (X gün)
        - Aşama 2: Test (X gün)
        - Aşama 3: Deployment (X gün)
        - Aşama 4: Teslim (X gün)
        
        ## 🔍 Kalite Kontrol
        - Test stratejisi
        - Code review süreci
        - Performance testing
        - Security audit
        
        ## 📋 Teslim Dokümanları
        - User manual
        - Technical documentation
        - API documentation
        - Deployment guide
        
        ## ⚠️ Risk Analizi
        - Potansiyel riskler
        - Risk azaltma stratejileri
        - Contingency planları
        """
        
        task = Task(
            id="final_delivery_plan_generation",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        print(f"   ✅ Final teslim planı oluşturuldu (Model: {result.model_info['model_name']})")
        return result.content
    
    async def save_comprehensive_report(self, all_results):
        """Kapsamlı raporu kaydet"""
        print("💾 Kapsamlı Rapor Kaydediliyor...")
        
        report_content = f"""# BDC Projesi AI Orchestrator Geliştirme Raporu

## 📊 Mevcut Durum Analizi

{all_results.get('status_analysis', 'Analiz bulunamadı')}

## 🚨 Kritik Sorunlar

{all_results.get('critical_issues', 'Sorun bulunamadı')}

## 📋 Düzeltme Planı

{all_results.get('fix_plan', 'Plan bulunamadı')}

## 🔧 Otomatik Düzeltmeler

{all_results.get('automated_fixes', 'Düzeltme bulunamadı')}

## 🎯 Final Teslim Planı

{all_results.get('delivery_plan', 'Plan bulunamadı')}

---

## 🚀 Sonraki Adımlar

1. **Acil Düzeltmeleri Uygula**
   - Kritik sorunları çöz
   - Güvenlik açıklarını kapat
   - Performans sorunlarını düzelt

2. **Test Sürecini Başlat**
   - Unit testleri tamamla
   - Integration testleri yap
   - Performance testleri uygula

3. **Deployment Hazırlığı**
   - Docker yapılandırmasını kontrol et
   - Environment variables'ları ayarla
   - CI/CD pipeline'ını test et

4. **Documentation Tamamla**
   - API documentation güncelle
   - User manual oluştur
   - Technical documentation tamamla

5. **Final Teslim**
   - Son testleri yap
   - Production deployment
   - Client teslimi

---

*Bu rapor AI Orchestrator kullanılarak otomatik olarak oluşturulmuştur.*
*Oluşturulma Tarihi: {asyncio.get_event_loop().time()}*
"""
        
        report_file = self.backend_path / "BDC_AI_ORCHESTRATOR_DEVELOPMENT_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Kapsamlı rapor kaydedildi: {report_file}")
    
    async def shutdown(self):
        """AI Orchestrator'ı kapat"""
        if self.engine:
            await self.engine.stop()
            print("🛑 AI Orchestrator kapatıldı")


async def main():
    """Ana fonksiyon"""
    print("🚀 BDC Projesi AI Orchestrator Geliştirme Stratejisi")
    print("=" * 60)
    
    strategy = BDCDevelopmentStrategy()
    all_results = {}
    
    try:
        # AI Orchestrator'ı başlat
        await strategy.initialize()
        
        # Mevcut durumu analiz et
        all_results['status_analysis'] = await strategy.analyze_current_status()
        
        # Kritik sorunları belirle
        all_results['critical_issues'] = await strategy.identify_critical_issues()
        
        # Düzeltme planı oluştur
        all_results['fix_plan'] = await strategy.generate_fix_plan(
            all_results['status_analysis'],
            all_results['critical_issues']
        )
        
        # Otomatik düzeltmeler oluştur
        all_results['automated_fixes'] = await strategy.create_automated_fixes(
            all_results['fix_plan']
        )
        
        # Final teslim planı oluştur
        all_results['delivery_plan'] = await strategy.generate_final_delivery_plan(all_results)
        
        # Kapsamlı raporu kaydet
        await strategy.save_comprehensive_report(all_results)
        
        print("\n🎉 BDC projesi AI Orchestrator geliştirme stratejisi tamamlandı!")
        print("📄 Rapor: BDC_AI_ORCHESTRATOR_DEVELOPMENT_REPORT.md")
        print("\n🚀 Şimdi bu rapora göre BDC projesini geliştirebilirsiniz!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await strategy.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 