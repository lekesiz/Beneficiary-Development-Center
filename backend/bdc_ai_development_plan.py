#!/usr/bin/env python3
"""
BDC Projesi AI Orchestrator ile Geliştirme Planı
Bu script BDC projesini A'dan Z'ye analiz edip geliştirir
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
from src.connectors.gemini_connector import GeminiConnector
from src.utils.config import Config
from src.utils.ollama_discovery import OllamaDiscoveryService


class BDCDevelopmentOrchestrator:
    """BDC Projesi Geliştirme Orkestratörü"""
    
    def __init__(self):
        self.engine = None
        self.bdc_root = Path("/Users/mikail/Desktop/BDC/Beneficiary Development Center")
        self.backend_path = self.bdc_root / "backend"
        self.frontend_path = self.bdc_root / "frontend"
        self.analysis_results = {}
        self.improvement_plan = []
        
    async def initialize(self):
        """AI Orchestrator'ı başlat"""
        print("🚀 BDC Geliştirme Orkestratörü başlatılıyor...")
        
        # Config oluştur
        config = Config()
        
        # Engine oluştur
        self.engine = OrchestratorEngine(config)
        
        # Modelleri yapılandır
        await self._setup_models()
        
        # Engine'i başlat
        await self.engine.start()
        
        print("✅ AI Orchestrator başarıyla başlatıldı")
    
    async def _setup_models(self):
        """AI modellerini yapılandır"""
        
        # OpenAI GPT-4 (Kod analizi ve geliştirme için)
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
                description="GPT-4 - Kod analizi ve geliştirme için ana model"
            )
            
            openai_connector = OpenAIConnector("gpt-4", openai_config)
            self.engine.register_model(openai_model)
            self.engine.register_connector("gpt-4", openai_connector)
            print("✅ OpenAI GPT-4 modeli yapılandırıldı")
        
        # Google Gemini (Alternatif analiz için)
        gemini_config = {
            'api_key': os.getenv('GOOGLE_API_KEY'),
            'model_name': 'gemini-1.5-flash',
            'rate_limit_rpm': 300,
            'rate_limit_tpm': 100000
        }
        
        if gemini_config['api_key']:
            gemini_model = AIModel(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                type=ModelType.GEMINI,
                capabilities=[
                    Capability.CODE_GENERATION,
                    Capability.ANALYSIS,
                    Capability.TEXT_GENERATION,
                    Capability.MATH_REASONING
                ],
                priority=2,
                description="Gemini - Alternatif analiz ve geliştirme"
            )
            
            gemini_connector = GeminiConnector("gemini-1.5-flash", gemini_config)
            self.engine.register_model(gemini_model)
            self.engine.register_connector("gemini-1.5-flash", gemini_connector)
            print("✅ Google Gemini modeli yapılandırıldı")
    
    async def analyze_bdc_project(self):
        """BDC projesini kapsamlı analiz et"""
        print("\n🔍 BDC Projesi Kapsamlı Analizi")
        print("=" * 60)
        
        # 1. Proje yapısı analizi
        await self._analyze_project_structure()
        
        # 2. Kod kalitesi analizi
        await self._analyze_code_quality()
        
        # 3. Güvenlik analizi
        await self._analyze_security()
        
        # 4. Performans analizi
        await self._analyze_performance()
        
        # 5. Test coverage analizi
        await self._analyze_test_coverage()
        
        # 6. Dependency analizi
        await self._analyze_dependencies()
        
        # 7. API analizi
        await self._analyze_api_endpoints()
        
        # 8. Database analizi
        await self._analyze_database()
        
        # 9. Frontend analizi
        await self._analyze_frontend()
        
        # 10. Deployment analizi
        await self._analyze_deployment()
        
        print("✅ BDC projesi analizi tamamlandı")
    
    async def _analyze_project_structure(self):
        """Proje yapısını analiz et"""
        print("📁 Proje Yapısı Analizi...")
        
        prompt = f"""
        BDC projesinin yapısını analiz et ve raporla:
        
        Proje yolu: {self.bdc_root}
        
        Şu konuları değerlendir:
        1. Dosya organizasyonu
        2. Klasör yapısı
        3. Modüler yapı
        4. Best practices uyumu
        5. Öneriler
        
        Detaylı bir analiz raporu oluştur.
        """
        
        task = Task(
            id="project_structure_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['project_structure'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_code_quality(self):
        """Kod kalitesini analiz et"""
        print("🔍 Kod Kalitesi Analizi...")
        
        # Backend kodlarını tara
        backend_files = list(self.backend_path.rglob("*.py"))
        sample_files = backend_files[:10]  # İlk 10 dosyayı analiz et
        
        file_contents = []
        for file in sample_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_contents.append(f"File: {file.name}\n{content[:1000]}...")
            except Exception as e:
                print(f"   ⚠️  {file} okunamadı: {e}")
        
        prompt = f"""
        BDC backend kodlarının kalitesini analiz et:
        
        {chr(10).join(file_contents)}
        
        Şu kriterleri değerlendir:
        1. PEP 8 uyumu
        2. Kod okunabilirliği
        3. Fonksiyon uzunlukları
        4. Değişken isimlendirme
        5. Error handling
        6. Documentation
        7. Code smells
        8. Refactoring önerileri
        
        Detaylı bir kod kalitesi raporu oluştur.
        """
        
        task = Task(
            id="code_quality_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['code_quality'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_security(self):
        """Güvenlik analizi"""
        print("🔒 Güvenlik Analizi...")
        
        # Requirements dosyasını kontrol et
        requirements_file = self.backend_path / "requirements.txt"
        requirements_content = ""
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                requirements_content = f.read()
        
        prompt = f"""
        BDC projesinin güvenlik durumunu analiz et:
        
        Requirements:
        {requirements_content}
        
        Şu güvenlik konularını değerlendir:
        1. Dependency vulnerabilities
        2. Authentication/Authorization
        3. Input validation
        4. SQL injection risks
        5. XSS vulnerabilities
        6. CSRF protection
        7. Environment variables
        8. API security
        9. Data encryption
        10. Security headers
        
        Güvenlik açıklarını ve önerileri listele.
        """
        
        task = Task(
            id="security_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['security'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_performance(self):
        """Performans analizi"""
        print("⚡ Performans Analizi...")
        
        prompt = f"""
        BDC projesinin performans durumunu analiz et:
        
        Proje yolu: {self.bdc_root}
        
        Şu performans konularını değerlendir:
        1. Database query optimization
        2. Caching strategies
        3. API response times
        4. Memory usage
        5. CPU utilization
        6. Database indexing
        7. Connection pooling
        8. Async/await usage
        9. Background tasks
        10. Load balancing
        
        Performans iyileştirme önerileri sun.
        """
        
        task = Task(
            id="performance_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['performance'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_test_coverage(self):
        """Test coverage analizi"""
        print("🧪 Test Coverage Analizi...")
        
        # Test dosyalarını bul
        test_files = list(self.backend_path.rglob("test_*.py"))
        test_content = []
        
        for test_file in test_files[:5]:  # İlk 5 test dosyası
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    test_content.append(f"Test File: {test_file.name}\n{content[:500]}...")
            except Exception as e:
                print(f"   ⚠️  {test_file} okunamadı: {e}")
        
        prompt = f"""
        BDC projesinin test coverage durumunu analiz et:
        
        Test dosyaları:
        {chr(10).join(test_content)}
        
        Şu test konularını değerlendir:
        1. Unit test coverage
        2. Integration test coverage
        3. Test quality
        4. Missing test cases
        5. Test organization
        6. Mock/stub usage
        7. Test data management
        8. CI/CD integration
        9. Test performance
        10. Test documentation
        
        Test iyileştirme önerileri sun.
        """
        
        task = Task(
            id="test_coverage_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['test_coverage'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_dependencies(self):
        """Dependency analizi"""
        print("📦 Dependency Analizi...")
        
        requirements_file = self.backend_path / "requirements.txt"
        requirements_content = ""
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                requirements_content = f.read()
        
        prompt = f"""
        BDC projesinin dependency durumunu analiz et:
        
        Requirements:
        {requirements_content}
        
        Şu dependency konularını değerlendir:
        1. Outdated packages
        2. Security vulnerabilities
        3. Unused dependencies
        4. Version conflicts
        5. Heavy dependencies
        6. Alternative packages
        7. Dependency tree
        8. Update recommendations
        9. Minimal requirements
        10. Production vs development
        
        Dependency iyileştirme önerileri sun.
        """
        
        task = Task(
            id="dependency_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['dependencies'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_api_endpoints(self):
        """API endpoint analizi"""
        print("🌐 API Endpoint Analizi...")
        
        # API dosyalarını bul
        api_files = list(self.backend_path.rglob("api/*.py"))
        api_content = []
        
        for api_file in api_files[:5]:
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    api_content.append(f"API File: {api_file.name}\n{content[:500]}...")
            except Exception as e:
                print(f"   ⚠️  {api_file} okunamadı: {e}")
        
        prompt = f"""
        BDC projesinin API endpoint'lerini analiz et:
        
        API dosyaları:
        {chr(10).join(api_content)}
        
        Şu API konularını değerlendir:
        1. RESTful design
        2. HTTP methods usage
        3. Status codes
        4. Error handling
        5. Request/Response validation
        6. Authentication/Authorization
        7. Rate limiting
        8. API documentation
        9. Versioning strategy
        10. API testing
        
        API iyileştirme önerileri sun.
        """
        
        task = Task(
            id="api_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['api_endpoints'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_database(self):
        """Database analizi"""
        print("🗄️ Database Analizi...")
        
        # Database dosyalarını bul
        db_files = list(self.backend_path.rglob("*.db"))
        migration_files = list(self.backend_path.rglob("migrations/*.py"))
        
        prompt = f"""
        BDC projesinin database durumunu analiz et:
        
        Database dosyaları: {[f.name for f in db_files]}
        Migration dosyaları: {[f.name for f in migration_files]}
        
        Şu database konularını değerlendir:
        1. Schema design
        2. Indexing strategy
        3. Query optimization
        4. Data relationships
        5. Migration management
        6. Backup strategy
        7. Data validation
        8. Connection management
        9. ORM usage
        10. Database security
        
        Database iyileştirme önerileri sun.
        """
        
        task = Task(
            id="database_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['database'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_frontend(self):
        """Frontend analizi"""
        print("🎨 Frontend Analizi...")
        
        if self.frontend_path.exists():
            frontend_files = list(self.frontend_path.rglob("*.js")) + list(self.frontend_path.rglob("*.jsx"))
            frontend_content = []
            
            for file in frontend_files[:5]:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        frontend_content.append(f"Frontend File: {file.name}\n{content[:500]}...")
                except Exception as e:
                    print(f"   ⚠️  {file} okunamadı: {e}")
        else:
            frontend_content = ["Frontend klasörü bulunamadı"]
        
        prompt = f"""
        BDC projesinin frontend durumunu analiz et:
        
        Frontend dosyaları:
        {chr(10).join(frontend_content)}
        
        Şu frontend konularını değerlendir:
        1. Component architecture
        2. State management
        3. UI/UX design
        4. Responsive design
        5. Performance optimization
        6. Code splitting
        7. Error handling
        8. Accessibility
        9. Testing strategy
        10. Build optimization
        
        Frontend iyileştirme önerileri sun.
        """
        
        task = Task(
            id="frontend_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.MEDIUM
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['frontend'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def _analyze_deployment(self):
        """Deployment analizi"""
        print("🚀 Deployment Analizi...")
        
        # Deployment dosyalarını bul
        docker_files = list(self.bdc_root.rglob("Dockerfile"))
        docker_compose_files = list(self.bdc_root.rglob("docker-compose*.yml"))
        
        prompt = f"""
        BDC projesinin deployment durumunu analiz et:
        
        Docker dosyaları: {[f.name for f in docker_files]}
        Docker Compose dosyaları: {[f.name for f in docker_compose_files]}
        
        Şu deployment konularını değerlendir:
        1. Containerization strategy
        2. Environment management
        3. CI/CD pipeline
        4. Monitoring/logging
        5. Scaling strategy
        6. Backup/recovery
        7. Security hardening
        8. Performance tuning
        9. Resource management
        10. Disaster recovery
        
        Deployment iyileştirme önerileri sun.
        """
        
        task = Task(
            id="deployment_analysis",
            type=TaskType.ANALYSIS,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.analysis_results['deployment'] = result.content
        
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def generate_improvement_plan(self):
        """İyileştirme planı oluştur"""
        print("\n📋 İyileştirme Planı Oluşturuluyor...")
        print("=" * 60)
        
        # Tüm analiz sonuçlarını birleştir
        all_analysis = "\n\n".join([
            f"## {key.replace('_', ' ').title()}\n{value}"
            for key, value in self.analysis_results.items()
        ])
        
        prompt = f"""
        BDC projesi analiz sonuçlarına göre kapsamlı bir iyileştirme planı oluştur:
        
        {all_analysis}
        
        Şu formatta bir iyileştirme planı oluştur:
        
        # BDC Projesi İyileştirme Planı
        
        ## 1. Kritik Öncelikli İyileştirmeler
        - [ ] İyileştirme 1 (Açıklama)
        - [ ] İyileştirme 2 (Açıklama)
        
        ## 2. Yüksek Öncelikli İyileştirmeler
        - [ ] İyileştirme 1 (Açıklama)
        - [ ] İyileştirme 2 (Açıklama)
        
        ## 3. Orta Öncelikli İyileştirmeler
        - [ ] İyileştirme 1 (Açıklama)
        - [ ] İyileştirme 2 (Açıklama)
        
        ## 4. Düşük Öncelikli İyileştirmeler
        - [ ] İyileştirme 1 (Açıklama)
        - [ ] İyileştirme 2 (Açıklama)
        
        Her iyileştirme için:
        - Açıklama
        - Tahmini süre
        - Gerekli kaynaklar
        - Beklenen fayda
        
        Son olarak genel bir teslim planı oluştur.
        """
        
        task = Task(
            id="improvement_plan_generation",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        self.improvement_plan = result.content
        
        print("✅ İyileştirme planı oluşturuldu")
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def generate_final_report(self):
        """Final rapor oluştur"""
        print("\n📊 Final Rapor Oluşturuluyor...")
        print("=" * 60)
        
        prompt = f"""
        BDC projesi için kapsamlı bir final rapor oluştur:
        
        Analiz Sonuçları:
        {json.dumps(self.analysis_results, indent=2, ensure_ascii=False)}
        
        İyileştirme Planı:
        {self.improvement_plan}
        
        Şu bölümleri içeren profesyonel bir rapor oluştur:
        
        # BDC Projesi Kapsamlı Analiz ve Geliştirme Raporu
        
        ## Özet
        - Proje durumu
        - Ana bulgular
        - Kritik iyileştirmeler
        
        ## Detaylı Analiz
        - Her analiz bölümü için detaylar
        - Bulgular ve öneriler
        
        ## İyileştirme Planı
        - Öncelikli iyileştirmeler
        - Zaman çizelgesi
        - Kaynak gereksinimleri
        
        ## Teslim Stratejisi
        - Aşamalı teslim planı
        - Kalite kontrol süreçleri
        - Test stratejisi
        
        ## Risk Analizi
        - Potansiyel riskler
        - Risk azaltma stratejileri
        
        ## Sonuç ve Öneriler
        - Genel değerlendirme
        - Sonraki adımlar
        
        Raporu markdown formatında oluştur.
        """
        
        task = Task(
            id="final_report_generation",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH
        )
        
        result = await self.engine.process_task(task)
        
        # Raporu dosyaya kaydet
        report_file = self.backend_path / "BDC_COMPREHENSIVE_DEVELOPMENT_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(result.content)
        
        print(f"✅ Final rapor oluşturuldu: {report_file}")
        print(f"   Model: {result.model_info['model_name']}")
        print(f"   Güven: {result.confidence:.2f}")
    
    async def shutdown(self):
        """AI Orchestrator'ı kapat"""
        if self.engine:
            await self.engine.stop()
            print("🛑 AI Orchestrator kapatıldı")


async def main():
    """Ana fonksiyon"""
    print("🚀 BDC Projesi AI Orchestrator ile Geliştirme")
    print("=" * 60)
    
    orchestrator = BDCDevelopmentOrchestrator()
    
    try:
        # AI Orchestrator'ı başlat
        await orchestrator.initialize()
        
        # BDC projesini analiz et
        await orchestrator.analyze_bdc_project()
        
        # İyileştirme planı oluştur
        await orchestrator.generate_improvement_plan()
        
        # Final rapor oluştur
        await orchestrator.generate_final_report()
        
        print("\n🎉 BDC projesi analizi ve geliştirme planı tamamlandı!")
        print("📄 Final rapor: BDC_COMPREHENSIVE_DEVELOPMENT_REPORT.md")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 