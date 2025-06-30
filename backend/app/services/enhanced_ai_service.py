"""
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
from src.utils.config import Config

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
            
            # Config oluştur
            config = Config()
            
            # Orchestrator engine'i oluştur
            self.engine = OrchestratorEngine(config)
            
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
