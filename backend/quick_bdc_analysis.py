#!/usr/bin/env python3
"""
BDC Projesi Hızlı Analiz Scripti
AI Orchestrator kullanarak BDC projesini analiz eder
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


class QuickBDCAnalyzer:
    """BDC Projesi Hızlı Analizör"""
    
    def __init__(self):
        self.engine = None
        self.bdc_root = Path("/Users/mikail/Desktop/BDC/Beneficiary Development Center")
        self.backend_path = self.bdc_root / "backend"
        self.results = {}
        
    async def initialize(self):
        """AI Orchestrator'ı başlat"""
        print("🚀 BDC Hızlı Analizör başlatılıyor...")
        
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
                capabilities=[Capability.ANALYSIS, Capability.CODE_GENERATION],
                priority=1,
                description="GPT-4 - Analiz için"
            )
            
            openai_connector = OpenAIConnector("gpt-4", openai_config)
            self.engine.register_model(openai_model)
            self.engine.register_connector("gpt-4", openai_connector)
            print("✅ OpenAI GPT-4 modeli yapılandırıldı")
        
        await self.engine.start()
        print("✅ AI Orchestrator başarıyla başlatıldı")
    
    async def analyze_project_structure(self):
        """Proje yapısını analiz et"""
        print("📁 Proje Yapısı Analizi...")
        
        # Proje dosyalarını listele
        files = []
        for root, dirs, filenames in os.walk(self.bdc_root):
            for filename in filenames:
                if filename.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yml', '.yaml')):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.bdc_root)
                    files.append(rel_path)
        
        file_structure = "\n".join(files[:50])  # İlk 50 dosya
        
        prompt = f"""
        BDC projesinin yapısını analiz et:
        
        Dosya yapısı:
        {file_structure}
        
        Şu konuları değerlendir:
        1. Proje organizasyonu
        2. Teknoloji stack'i
        3. Dosya organizasyonu
        4. Eksik dosyalar
        5. İyileştirme önerileri
        
        Kısa ve öz bir analiz raporu oluştur.
        """
        
        task = Task(
            id="project_structure_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.results['project_structure'] = result.content
        
        print(f"   ✅ Tamamlandı (Model: {result.model_info['model_name']})")
    
    async def analyze_code_quality(self):
        """Kod kalitesini analiz et"""
        print("🔍 Kod Kalitesi Analizi...")
        
        # Python dosyalarını oku
        python_files = list(self.backend_path.rglob("*.py"))
        sample_content = ""
        
        for file in python_files[:3]:  # İlk 3 dosya
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    sample_content += f"\n--- {file.name} ---\n{content[:500]}...\n"
            except Exception as e:
                print(f"   ⚠️  {file} okunamadı: {e}")
        
        prompt = f"""
        BDC backend kodlarının kalitesini analiz et:
        
        {sample_content}
        
        Şu kriterleri değerlendir:
        1. Kod okunabilirliği
        2. PEP 8 uyumu
        3. Fonksiyon yapısı
        4. Error handling
        5. Documentation
        6. Ana sorunlar
        7. İyileştirme önerileri
        
        Kısa ve öz bir kod kalitesi raporu oluştur.
        """
        
        task = Task(
            id="code_quality_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.results['code_quality'] = result.content
        
        print(f"   ✅ Tamamlandı (Model: {result.model_info['model_name']})")
    
    async def analyze_dependencies(self):
        """Dependency analizi"""
        print("📦 Dependency Analizi...")
        
        requirements_file = self.backend_path / "requirements.txt"
        requirements_content = ""
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                requirements_content = f.read()
        
        package_json_file = self.bdc_root / "package.json"
        package_content = ""
        if package_json_file.exists():
            with open(package_json_file, 'r') as f:
                package_content = f.read()
        
        prompt = f"""
        BDC projesinin dependency durumunu analiz et:
        
        Python Requirements:
        {requirements_content}
        
        Node.js Package.json:
        {package_content}
        
        Şu konuları değerlendir:
        1. Güncel olmayan paketler
        2. Güvenlik açıkları
        3. Kullanılmayan dependencies
        4. Version conflicts
        5. Ağır dependencies
        6. İyileştirme önerileri
        
        Kısa bir dependency analiz raporu oluştur.
        """
        
        task = Task(
            id="dependency_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        self.results['dependencies'] = result.content
        
        print(f"   ✅ Tamamlandı (Model: {result.model_info['model_name']})")
    
    async def generate_improvement_plan(self):
        """İyileştirme planı oluştur"""
        print("📋 İyileştirme Planı Oluşturuluyor...")
        
        all_analysis = "\n\n".join([
            f"## {key.replace('_', ' ').title()}\n{value}"
            for key, value in self.results.items()
        ])
        
        prompt = f"""
        BDC projesi analiz sonuçlarına göre pratik bir iyileştirme planı oluştur:
        
        {all_analysis}
        
        Şu formatta bir plan oluştur:
        
        # BDC Projesi İyileştirme Planı
        
        ## 🚨 Kritik İyileştirmeler (1-2 gün)
        - [ ] İyileştirme 1
        - [ ] İyileştirme 2
        
        ## ⚡ Hızlı İyileştirmeler (3-5 gün)
        - [ ] İyileştirme 1
        - [ ] İyileştirme 2
        
        ## 📈 Orta Vadeli İyileştirmeler (1-2 hafta)
        - [ ] İyileştirme 1
        - [ ] İyileştirme 2
        
        ## 🎯 Teslim Stratejisi
        - Aşamalı teslim planı
        - Test stratejisi
        - Kalite kontrol
        
        Her iyileştirme için kısa açıklama ve tahmini süre ekle.
        """
        
        task = Task(
            id="improvement_plan_generation",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.results['improvement_plan'] = result.content
        
        print(f"   ✅ Tamamlandı (Model: {result.model_info['model_name']})")
    
    async def save_report(self):
        """Raporu kaydet"""
        print("💾 Rapor Kaydediliyor...")
        
        report_content = f"""# BDC Projesi Hızlı Analiz Raporu

## 📊 Analiz Özeti

{self.results.get('project_structure', 'Analiz bulunamadı')}

## 🔍 Kod Kalitesi

{self.results.get('code_quality', 'Analiz bulunamadı')}

## 📦 Dependencies

{self.results.get('dependencies', 'Analiz bulunamadı')}

## 📋 İyileştirme Planı

{self.results.get('improvement_plan', 'Plan bulunamadı')}

---
*Bu rapor AI Orchestrator kullanılarak otomatik olarak oluşturulmuştur.*
"""
        
        report_file = self.backend_path / "BDC_QUICK_ANALYSIS_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Rapor kaydedildi: {report_file}")
    
    async def shutdown(self):
        """AI Orchestrator'ı kapat"""
        if self.engine:
            await self.engine.stop()
            print("🛑 AI Orchestrator kapatıldı")


async def main():
    """Ana fonksiyon"""
    print("🚀 BDC Projesi Hızlı Analiz")
    print("=" * 50)
    
    analyzer = QuickBDCAnalyzer()
    
    try:
        # AI Orchestrator'ı başlat
        await analyzer.initialize()
        
        # Analizleri yap
        await analyzer.analyze_project_structure()
        await analyzer.analyze_code_quality()
        await analyzer.analyze_dependencies()
        
        # İyileştirme planı oluştur
        await analyzer.generate_improvement_plan()
        
        # Raporu kaydet
        await analyzer.save_report()
        
        print("\n🎉 BDC projesi hızlı analizi tamamlandı!")
        print("📄 Rapor: BDC_QUICK_ANALYSIS_REPORT.md")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await analyzer.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 