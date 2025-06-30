#!/usr/bin/env python3
"""
BDC - AI Orchestrator Integration Script
Bu script AI Orchestrator'ı BDC projesine entegre eder
"""

import os
import sys
import shutil
from pathlib import Path

def integrate_ai_orchestrator():
    """AI Orchestrator'ı BDC projesine entegre et"""
    
    # Yolları tanımla
    bdc_backend = Path(__file__).parent
    ai_orchestrator_src = Path("/Users/mikail/Desktop/ai_orchestrator_complete/ai_orchestrator")
    
    print("🔧 AI Orchestrator BDC Entegrasyonu")
    print("=" * 50)
    
    # AI Orchestrator kaynak dizininin varlığını kontrol et
    if not ai_orchestrator_src.exists():
        print(f"❌ AI Orchestrator kaynak dizini bulunamadı: {ai_orchestrator_src}")
        print("📝 Lütfen AI Orchestrator'ın doğru konumda olduğundan emin olun")
        return
    
    # 1. AI Orchestrator'ı kopyala
    target_dir = bdc_backend / "ai_orchestrator"
    
    if target_dir.exists():
        print(f"⚠️  {target_dir} zaten mevcut, güncelleniyor...")
        shutil.rmtree(target_dir)
    
    print(f"📁 AI Orchestrator kopyalanıyor...")
    print(f"   Kaynak: {ai_orchestrator_src}")
    print(f"   Hedef: {target_dir}")
    
    shutil.copytree(ai_orchestrator_src, target_dir)
    
    # 2. Gereksiz dosyaları temizle
    files_to_remove = [
        "main.py",
        "test_ollama.py", 
        "test_api_keys.py",
        "setup_api_keys.sh"
    ]
    
    for file in files_to_remove:
        file_path = target_dir / file
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️  {file} silindi")
    
    # 3. BDC için özel konfigürasyon oluştur
    create_bdc_config(target_dir)
    
    # 4. BDC AI Service'i güncelle
    update_bdc_ai_service(bdc_backend)
    
    print("✅ AI Orchestrator başarıyla entegre edildi!")
    print("\n📝 Sonraki adımlar:")
    print("1. API anahtarlarını ayarlayın:")
    print("   export OPENAI_API_KEY='sk-...'")
    print("   export GOOGLE_API_KEY='AIza...'")
    print("2. BDC'yi yeniden başlatın:")
    print("   python app.py")
    print("3. Test edin:")
    print("   python -m pytest tests/test_ai_orchestrator.py")

def create_bdc_config(ai_orchestrator_dir):
    """BDC için özel konfigürasyon oluştur"""
    
    config_content = '''# BDC AI Orchestrator Configuration
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
'''
    
    config_file = ai_orchestrator_dir / "bdc_config.py"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"📝 BDC konfigürasyonu oluşturuldu: {config_file}")

def update_bdc_ai_service(bdc_backend):
    """BDC AI Service'ini AI Orchestrator ile güncelle"""
    
    # AI Orchestrator import'larını ekle
    ai_service_path = bdc_backend / "app" / "services" / "ai_service.py"
    
    if not ai_service_path.exists():
        print(f"⚠️  AI service dosyası bulunamadı: {ai_service_path}")
        return
    
    # Mevcut AI service'i yedekle
    backup_path = ai_service_path.with_suffix('.py.backup')
    shutil.copy2(ai_service_path, backup_path)
    print(f"💾 AI service yedeklendi: {backup_path}")
    
    # AI Orchestrator entegrasyonu için yeni service oluştur
    create_enhanced_ai_service(bdc_backend)

def create_enhanced_ai_service(bdc_backend):
    """AI Orchestrator ile geliştirilmiş AI service oluştur"""
    
    enhanced_service_content = '''"""
BDC Enhanced AI Service with AI Orchestrator
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger

# AI Orchestrator'ı import et
ai_orchestrator_path = Path(__file__).parent.parent.parent / "ai_orchestrator"
sys.path.append(str(ai_orchestrator_path))

from src.orchestrator.engine import OrchestratorEngine
from src.models.task import Task, TaskType, Priority
from src.models.ai_model import AIModel, ModelType, Capability
from src.connectors.openai_connector import OpenAIConnector
from src.connectors.gemini_connector import GeminiConnector
from src.utils.ollama_discovery import OllamaDiscoveryService
from bdc_config import AI_ORCHESTRATOR_CONFIG, BDC_PROMPTS

class BDCEnhancedAIService:
    """BDC için geliştirilmiş AI service"""
    
    def __init__(self):
        self.engine = None
        self.is_initialized = False
        
    async def initialize(self):
        """AI Orchestrator'ı başlat"""
        if self.is_initialized:
            return
            
        try:
            logger.info("🚀 BDC AI Orchestrator başlatılıyor...")
            
            # Orchestrator engine'i oluştur
            self.engine = OrchestratorEngine()
            
            # Modelleri yapılandır
            await self._setup_models()
            
            # Engine'i başlat
            await self.engine.start()
            
            self.is_initialized = True
            logger.info("✅ BDC AI Orchestrator başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"❌ AI Orchestrator başlatma hatası: {e}")
            raise
    
    async def _setup_models(self):
        """AI modellerini yapılandır"""
        
        config = AI_ORCHESTRATOR_CONFIG
        
        # OpenAI modeli
        if config['models']['openai']['api_key']:
            openai_model = AIModel(
                id="gpt-4",
                name="GPT-4",
                type=ModelType.OPENAI_GPT,
                capabilities=[
                    Capability.TEXT_GENERATION,
                    Capability.ANALYSIS,
                    Capability.CREATIVE_WRITING,
                    Capability.CODE_GENERATION,
                    Capability.QUESTION_ANSWERING,
                    Capability.SUMMARIZATION,
                    Capability.TRANSLATION
                ],
                priority=2,
                description="OpenAI GPT-4 - BDC için ana model"
            )
            
            openai_connector = OpenAIConnector("gpt-4", config['models']['openai'])
            
            self.engine.register_model(openai_model)
            self.engine.register_connector("gpt-4", openai_connector)
            
            logger.info("✅ OpenAI GPT-4 modeli yapılandırıldı")
        
        # Gemini modeli
        if config['models']['gemini']['api_key']:
            gemini_model = AIModel(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                type=ModelType.GEMINI,
                capabilities=[
                    Capability.TEXT_GENERATION,
                    Capability.ANALYSIS,
                    Capability.CREATIVE_WRITING,
                    Capability.CODE_GENERATION,
                    Capability.QUESTION_ANSWERING,
                    Capability.SUMMARIZATION,
                    Capability.TRANSLATION,
                    Capability.MATH_REASONING
                ],
                priority=3,
                description="Google Gemini - BDC için alternatif model"
            )
            
            gemini_connector = GeminiConnector("gemini-1.5-flash", config['models']['gemini'])
            
            self.engine.register_model(gemini_model)
            self.engine.register_connector("gemini-1.5-flash", gemini_connector)
            
            logger.info("✅ Google Gemini modeli yapılandırıldı")
        
        # Ollama modelleri (otomatik keşif)
        if config['ollama']['auto_discover']:
            try:
                discovery_service = OllamaDiscoveryService(config['ollama']['api_base'])
                registered_models = await discovery_service.auto_discover_and_register(self.engine)
                
                if registered_models:
                    logger.info(f"✅ {len(registered_models)} Ollama modeli keşfedildi")
                else:
                    logger.warning("⚠️  Ollama modelleri bulunamadı")
                    
            except Exception as e:
                logger.warning(f"⚠️  Ollama keşfi başarısız: {e}")
    
    async def generate_learning_path(self, user_profile: Dict, goal: str) -> Dict[str, Any]:
        """Öğrenme yolu oluştur"""
        await self.initialize()
        
        prompt = BDC_PROMPTS['learning_path']['user_template'].format(
            profile=str(user_profile),
            goal=goal
        )
        
        system_message = BDC_PROMPTS['learning_path']['system']
        
        task = Task(
            id=f"learning_path_{user_profile.get('id', 'unknown')}",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.HIGH,
            metadata={
                'user_profile': user_profile,
                'goal': goal,
                'system_message': system_message
            }
        )
        
        result = await self.engine.process_task(task)
        return self._process_learning_path_result(result)
    
    async def generate_assessment_questions(self, topic: str, level: str, count: int = 10) -> List[Dict]:
        """Değerlendirme soruları oluştur"""
        await self.initialize()
        
        prompt = BDC_PROMPTS['assessment']['user_template'].format(
            topic=topic,
            level=level,
            count=count
        )
        
        system_message = BDC_PROMPTS['assessment']['system']
        
        task = Task(
            id=f"assessment_{topic}_{level}",
            type=TaskType.QUESTION_GENERATION,
            prompt=prompt,
            priority=Priority.MEDIUM,
            metadata={
                'topic': topic,
                'level': level,
                'count': count,
                'system_message': system_message
            }
        )
        
        result = await self.engine.process_task(task)
        return self._process_assessment_result(result)
    
    async def generate_content(self, topic: str, format_type: str) -> Dict[str, Any]:
        """Eğitim içeriği oluştur"""
        await self.initialize()
        
        prompt = BDC_PROMPTS['content']['user_template'].format(
            topic=topic,
            format=format_type
        )
        
        system_message = BDC_PROMPTS['content']['system']
        
        task = Task(
            id=f"content_{topic}_{format_type}",
            type=TaskType.CONTENT_GENERATION,
            prompt=prompt,
            priority=Priority.MEDIUM,
            metadata={
                'topic': topic,
                'format': format_type,
                'system_message': system_message
            }
        )
        
        result = await self.engine.process_task(task)
        return self._process_content_result(result)
    
    def _process_learning_path_result(self, result) -> Dict[str, Any]:
        """Öğrenme yolu sonucunu işle"""
        return {
            'learning_path': result.content,
            'confidence': result.confidence,
            'model_used': result.model_info['model_name'],
            'cost': result.cost,
            'tokens_used': result.tokens_used
        }
    
    def _process_assessment_result(self, result) -> List[Dict]:
        """Değerlendirme sonucunu işle"""
        # JSON formatında soruları parse et
        try:
            import json
            questions = json.loads(result.content)
            return questions
        except:
            # Fallback: basit liste formatı
            return [{'question': result.content, 'type': 'text'}]
    
    def _process_content_result(self, result) -> Dict[str, Any]:
        """İçerik sonucunu işle"""
        return {
            'content': result.content,
            'confidence': result.confidence,
            'model_used': result.model_info['model_name'],
            'cost': result.cost,
            'tokens_used': result.tokens_used
        }
    
    async def shutdown(self):
        """AI Orchestrator'ı kapat"""
        if self.engine:
            await self.engine.stop()
            logger.info("🛑 BDC AI Orchestrator kapatıldı")

# Global instance
bdc_ai_service = BDCEnhancedAIService()
'''
    
    enhanced_service_path = bdc_backend / "app" / "services" / "enhanced_ai_service.py"
    with open(enhanced_service_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_service_content)
    
    print(f"📝 Geliştirilmiş AI service oluşturuldu: {enhanced_service_path}")

if __name__ == "__main__":
    integrate_ai_orchestrator() 