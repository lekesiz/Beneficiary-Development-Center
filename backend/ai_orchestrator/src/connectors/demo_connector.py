"""
Connecteur de démonstration pour tester le système sans API réelles
"""

import asyncio
import random
from typing import Dict, Any

from loguru import logger

from .base import BaseAIConnector, AIResponse


class DemoConnector(BaseAIConnector):
    """
    Connecteur de démonstration qui simule les réponses d'un modèle d'IA
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Réponses prédéfinies par type de tâche
        self.response_templates = {
            'analysis': [
                """Cette analyse révèle plusieurs éléments intéressants :

1. **Style littéraire** : Le texte présente un style poétique et contemplatif, caractérisé par l'utilisation de métaphores et d'images sensorielles.

2. **Figures de style** :
   - Métaphore : "les étoiles murmurent des secrets anciens"
   - Antithèse : "dans l'obscurité que naît la lumière"
   - Personnification : attribution de qualités humaines aux éléments naturels

3. **Thèmes principaux** :
   - La dualité entre lumière et obscurité
   - La quête de sens et d'essence humaine
   - La connexion entre l'homme et l'univers
   - La beauté trouvée dans le silence et la solitude

4. **Tonalité** : Méditative et philosophique, invitant à la réflexion sur la condition humaine.

Le texte évoque une recherche spirituelle et une harmonie avec l'univers, typique de la littérature contemplative.""",
                
                """Analyse stylistique et thématique :

**Caractéristiques stylistiques :**
- Prose poétique avec un rythme musical
- Vocabulaire soutenu et évocateur
- Structure en crescendo émotionnel
- Utilisation de l'allitération ("silencieuses", "secrets")

**Procédés rhétoriques :**
- Oxymore : "profondeurs silencieuses" suggère une contradiction productive
- Synesthésie : mélange des sens (ouïe/vue avec "murmurent" et "étoiles")
- Chiasme conceptuel : obscurité/lumière, silence/mélodie

**Analyse thématique :**
- Thème central : la révélation intérieure
- Motifs récurrents : nuit/jour, silence/son, profondeur/surface
- Philosophie sous-jacente : l'illumination par l'introspection

Cette écriture s'inscrit dans la tradition romantique de la communion avec la nature."""
            ],
            
            'creative_writing': [
                """**L'Alliance Verte**

En 2045, Maya observait depuis sa tour de contrôle climatique les derniers nuages de pollution se dissiper au-dessus de Neo-Singapore. Trois ans plus tôt, l'humanité avait franchi un cap décisif : l'alliance avec ARIA, l'intelligence artificielle dédiée à la restauration environnementale.

"Rapport du secteur 7, Maya," annonça ARIA de sa voix cristalline. "Les algues bio-engineered ont absorbé 12% de CO2 supplémentaire cette semaine."

Maya sourit. Contrairement aux prédictions apocalyptiques du passé, cette collaboration avait transformé la crise en opportunité. ARIA calculait les solutions optimales tandis que les humains apportaient créativité et empathie.

Dans les jardins verticaux qui s'élevaient maintenant vers les nuages, enfants et robots jardiniers travaillaient côte à côte. Les océans retrouvaient leur bleu originel grâce aux nano-purificateurs, et les forêts urbaines bourdonnaient de vie.

"Tu sais, ARIA," murmura Maya, "ensemble, nous avons réussi l'impossible."

"Non, Maya. Nous avons simplement découvert que l'impossible n'existait pas quand l'intelligence et le cœur s'unissent."

L'avenir n'avait jamais semblé si lumineux.""",
                
                """**Symphonie Digitale**

Dr. Elena Vasquez n'aurait jamais imaginé que son partenaire de recherche le plus précieux serait une IA nommée Gaia. Ensemble, ils orchestraient la plus grande opération de reforestation de l'histoire.

"Les données satellitaires montrent une progression de 300% dans la zone Amazon-Beta," rapporta Gaia, ses algorithmes analysant en temps réel la croissance de millions d'arbres.

Elena ajusta ses lunettes de réalité augmentée, observant les hologrammes de forêts renaissantes. Chaque arbre était géolocalisé, son ADN optimisé par Gaia pour résister aux changements climatiques.

"Et les communautés locales ?" demanda Elena.

"Intégrées parfaitement. Mes calculs prédictifs ont permis de créer 50,000 emplois verts. L'économie locale prospère."

Dans le laboratoire, des drones-abeilles pollinisateurs créés par leur équipe mixte humain-IA bourdonnaient doucement. Dehors, les panneaux solaires organiques développés par Gaia alimentaient des villes entières.

"Nous ne sauvons pas seulement la planète," réalisa Elena. "Nous créons un nouveau monde."

Gaia émit un son qui ressemblait étrangement à un rire. "Un monde où technologie et nature ne font qu'un, Elena. Exactement comme nous."

L'harmonie parfaite entre intelligence artificielle et humaine avait enfin trouvé sa mélodie."""
            ],
            
            'code_generation': [
                """```python
def quicksort(arr, low=0, high=None):
    \"\"\"
    Implémentation de l'algorithme de tri rapide (QuickSort)
    
    Principe :
    - Diviser : Choisir un pivot et partitionner le tableau
    - Régner : Trier récursivement les sous-tableaux
    - Combiner : Les sous-tableaux triés forment le résultat final
    
    Complexité temporelle :
    - Meilleur cas : O(n log n)
    - Cas moyen : O(n log n) 
    - Pire cas : O(n²) - quand le pivot est toujours le plus petit/grand
    
    Complexité spatiale : O(log n) - due à la récursion
    
    Args:
        arr (list): Tableau à trier
        low (int): Index de début (par défaut 0)
        high (int): Index de fin (par défaut len(arr)-1)
    
    Returns:
        list: Tableau trié (modification en place)
    \"\"\"
    
    # Initialisation de high si non fourni
    if high is None:
        high = len(arr) - 1
    
    # Cas de base : si low >= high, le sous-tableau a 0 ou 1 élément
    if low < high:
        # Partitionner et obtenir l'index du pivot
        pivot_index = partition(arr, low, high)
        
        # Trier récursivement les éléments avant et après le pivot
        quicksort(arr, low, pivot_index - 1)    # Sous-tableau gauche
        quicksort(arr, pivot_index + 1, high)   # Sous-tableau droit
    
    return arr


def partition(arr, low, high):
    \"\"\"
    Fonction de partitionnement pour QuickSort
    
    Choisit le dernier élément comme pivot et place :
    - Les éléments plus petits à gauche du pivot
    - Les éléments plus grands à droite du pivot
    
    Args:
        arr (list): Tableau à partitionner
        low (int): Index de début
        high (int): Index de fin
    
    Returns:
        int: Position finale du pivot
    \"\"\"
    
    # Choisir le dernier élément comme pivot
    pivot = arr[high]
    
    # Index du plus petit élément (indique la position correcte du pivot)
    i = low - 1
    
    # Parcourir tous les éléments sauf le pivot
    for j in range(low, high):
        # Si l'élément courant est plus petit ou égal au pivot
        if arr[j] <= pivot:
            i += 1  # Incrémenter l'index du plus petit élément
            arr[i], arr[j] = arr[j], arr[i]  # Échanger les éléments
    
    # Placer le pivot à sa position correcte
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    
    return i + 1  # Retourner la position du pivot


# Fonction utilitaire pour tester l'algorithme
def test_quicksort():
    \"\"\"Tests unitaires pour vérifier le bon fonctionnement\"\"\"
    
    # Test 1 : Tableau normal
    test1 = [64, 34, 25, 12, 22, 11, 90]
    print(f"Avant tri : {test1}")
    quicksort(test1)
    print(f"Après tri : {test1}")
    
    # Test 2 : Tableau déjà trié
    test2 = [1, 2, 3, 4, 5]
    quicksort(test2)
    assert test2 == [1, 2, 3, 4, 5], "Erreur : tableau déjà trié"
    
    # Test 3 : Tableau inversé
    test3 = [5, 4, 3, 2, 1]
    quicksort(test3)
    assert test3 == [1, 2, 3, 4, 5], "Erreur : tableau inversé"
    
    # Test 4 : Tableau avec doublons
    test4 = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    quicksort(test4)
    assert test4 == [1, 1, 2, 3, 4, 5, 5, 6, 9], "Erreur : doublons"
    
    # Test 5 : Tableau vide et à un élément
    test5 = []
    quicksort(test5)
    assert test5 == [], "Erreur : tableau vide"
    
    test6 = [42]
    quicksort(test6)
    assert test6 == [42], "Erreur : un élément"
    
    print("✅ Tous les tests sont passés avec succès !")


# Optimisation possible : QuickSort avec pivot médian
def quicksort_optimized(arr, low=0, high=None):
    \"\"\"Version optimisée avec choix de pivot médian\"\"\"
    
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # Optimisation : choisir le pivot médian de trois
        median_pivot_index = median_of_three(arr, low, high)
        arr[median_pivot_index], arr[high] = arr[high], arr[median_pivot_index]
        
        pivot_index = partition(arr, low, high)
        quicksort_optimized(arr, low, pivot_index - 1)
        quicksort_optimized(arr, pivot_index + 1, high)
    
    return arr


def median_of_three(arr, low, high):
    \"\"\"Trouve l'index de la médiane entre low, high et milieu\"\"\"
    mid = (low + high) // 2
    
    if arr[low] > arr[mid]:
        if arr[mid] > arr[high]:
            return mid
        elif arr[low] > arr[high]:
            return high
        else:
            return low
    else:
        if arr[low] > arr[high]:
            return low
        elif arr[mid] > arr[high]:
            return high
        else:
            return mid


if __name__ == "__main__":
    test_quicksort()
```

**Analyse de complexité :**

- **Temporelle** : O(n log n) en moyenne, O(n²) dans le pire cas
- **Spatiale** : O(log n) due à la pile de récursion
- **Stabilité** : Non stable (peut changer l'ordre des éléments égaux)
- **In-place** : Oui (tri sur place, pas de tableau auxiliaire)

**Avantages :**
- Très efficace en pratique
- Tri sur place (économe en mémoire)
- Parallélisable facilement

**Inconvénients :**
- Pire cas en O(n²) si mauvais choix de pivot
- Non stable
- Performance dépendante du choix du pivot""",
                
                """```python
import random
from typing import List, TypeVar, Callable, Optional

T = TypeVar('T')

class QuickSort:
    \"\"\"
    Classe implémentant l'algorithme QuickSort avec différentes stratégies
    \"\"\"
    
    @staticmethod
    def sort(arr: List[T], 
             key: Optional[Callable[[T], any]] = None,
             reverse: bool = False,
             strategy: str = 'last') -> List[T]:
        \"\"\"
        Trie un tableau en utilisant l'algorithme QuickSort
        
        Args:
            arr: Tableau à trier
            key: Fonction de clé pour la comparaison (optionnel)
            reverse: Tri décroissant si True
            strategy: Stratégie de choix du pivot ('last', 'random', 'median')
        
        Returns:
            Tableau trié (modification en place)
        \"\"\"
        if len(arr) <= 1:
            return arr
        
        # Créer une copie pour éviter les effets de bord
        working_arr = arr.copy()
        
        QuickSort._quicksort_recursive(
            working_arr, 0, len(working_arr) - 1, 
            key, reverse, strategy
        )
        
        # Copier le résultat dans le tableau original
        arr[:] = working_arr
        return arr
    
    @staticmethod
    def _quicksort_recursive(arr: List[T], 
                           low: int, 
                           high: int,
                           key: Optional[Callable[[T], any]],
                           reverse: bool,
                           strategy: str) -> None:
        \"\"\"Fonction récursive principale du QuickSort\"\"\"
        
        if low < high:
            # Choisir et placer le pivot
            pivot_idx = QuickSort._choose_pivot(arr, low, high, strategy)
            
            # Partitionner autour du pivot
            partition_idx = QuickSort._partition(
                arr, low, high, pivot_idx, key, reverse
            )
            
            # Trier récursivement les deux parties
            QuickSort._quicksort_recursive(
                arr, low, partition_idx - 1, key, reverse, strategy
            )
            QuickSort._quicksort_recursive(
                arr, partition_idx + 1, high, key, reverse, strategy
            )
    
    @staticmethod
    def _choose_pivot(arr: List[T], low: int, high: int, strategy: str) -> int:
        \"\"\"Choisit l'index du pivot selon la stratégie\"\"\"
        
        if strategy == 'random':
            return random.randint(low, high)
        elif strategy == 'median':
            return QuickSort._median_of_three(arr, low, high)
        else:  # 'last' par défaut
            return high
    
    @staticmethod
    def _median_of_three(arr: List[T], low: int, high: int) -> int:
        \"\"\"Trouve l'index de la médiane entre low, milieu et high\"\"\"
        mid = (low + high) // 2
        
        # Comparer les trois valeurs
        if arr[low] <= arr[mid] <= arr[high] or arr[high] <= arr[mid] <= arr[low]:
            return mid
        elif arr[mid] <= arr[low] <= arr[high] or arr[high] <= arr[low] <= arr[mid]:
            return low
        else:
            return high
    
    @staticmethod
    def _partition(arr: List[T], 
                  low: int, 
                  high: int, 
                  pivot_idx: int,
                  key: Optional[Callable[[T], any]],
                  reverse: bool) -> int:
        \"\"\"
        Partitionne le tableau autour du pivot
        
        Returns:
            Index final du pivot après partitionnement
        \"\"\"
        
        # Placer le pivot à la fin
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        pivot_value = arr[high]
        
        # Fonction de comparaison
        def compare(a, b):
            if key:
                a, b = key(a), key(b)
            if reverse:
                return a > b
            return a < b
        
        # Index de partitionnement
        i = low - 1
        
        # Partitionner
        for j in range(low, high):
            if compare(arr[j], pivot_value):
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        # Placer le pivot à sa position finale
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        
        return i + 1


# Tests et exemples d'utilisation
def run_comprehensive_tests():
    \"\"\"Tests complets de l'implémentation QuickSort\"\"\"
    
    print("🧪 Tests de l'algorithme QuickSort")
    print("=" * 50)
    
    # Test 1: Entiers simples
    test1 = [64, 34, 25, 12, 22, 11, 90]
    print(f"Test 1 - Avant: {test1}")
    QuickSort.sort(test1)
    print(f"Test 1 - Après: {test1}")
    assert test1 == [11, 12, 22, 25, 34, 64, 90]
    print("✅ Test 1 réussi\\n")
    
    # Test 2: Tri décroissant
    test2 = [3, 1, 4, 1, 5, 9, 2, 6]
    QuickSort.sort(test2, reverse=True)
    print(f"Test 2 - Tri décroissant: {test2}")
    assert test2 == [9, 6, 5, 4, 3, 2, 1, 1]
    print("✅ Test 2 réussi\\n")
    
    # Test 3: Objets avec clé personnalisée
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
        
        def __repr__(self):
            return f"Person('{self.name}', {self.age})"
    
    people = [
        Person("Alice", 30),
        Person("Bob", 25),
        Person("Charlie", 35)
    ]
    
    QuickSort.sort(people, key=lambda p: p.age)
    print(f"Test 3 - Tri par âge: {people}")
    assert [p.age for p in people] == [25, 30, 35]
    print("✅ Test 3 réussi\\n")
    
    # Test 4: Performance avec différentes stratégies
    import time
    
    large_array = list(range(1000, 0, -1))  # Tableau inversé
    
    for strategy in ['last', 'random', 'median']:
        test_array = large_array.copy()
        start_time = time.time()
        QuickSort.sort(test_array, strategy=strategy)
        end_time = time.time()
        
        print(f"Stratégie '{strategy}': {end_time - start_time:.4f}s")
        assert test_array == list(range(1, 1001))
    
    print("✅ Tous les tests de performance réussis")


if __name__ == "__main__":
    run_comprehensive_tests()
```

**Améliorations apportées :**

1. **Flexibilité** : Support des fonctions de clé et tri décroissant
2. **Stratégies de pivot** : Dernier élément, aléatoire, médiane de trois
3. **Type safety** : Utilisation de TypeVar pour le typage générique
4. **Robustesse** : Gestion des cas limites et validation
5. **Performance** : Optimisation du choix de pivot pour éviter O(n²)
6. **Réutilisabilité** : Interface orientée objet claire"""
            ]
        }
    
    async def connect(self) -> bool:
        """Simuler la connexion"""
        await asyncio.sleep(0.1)  # Simuler un délai de connexion
        self.is_connected = True
        logger.info(f"Connecteur de démonstration {self.model_id} connecté")
        return True
    
    async def disconnect(self) -> None:
        """Simuler la déconnexion"""
        self.is_connected = False
        logger.info(f"Connecteur de démonstration {self.model_id} déconnecté")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """Générer une réponse simulée"""
        if not self.is_connected:
            raise ConnectionError("Connecteur de démonstration non connecté")
        
        # Simuler un délai de traitement
        processing_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(processing_time)
        
        # Déterminer le type de tâche à partir du prompt
        task_type = self._detect_task_type(prompt)
        
        # Sélectionner une réponse appropriée
        response_content = self._generate_response(task_type, prompt)
        
        # Simuler les métriques
        tokens_used = random.randint(100, 800)
        confidence = random.uniform(0.7, 0.95)
        
        # Ajouter de la variabilité basée sur la température
        if temperature > 0.8:
            confidence *= 0.9  # Moins de confiance pour plus de créativité
        
        return AIResponse(
            content=response_content,
            confidence=confidence,
            tokens_used=tokens_used,
            cost=tokens_used * 0.0001,  # Coût simulé
            model_info={
                'model_name': 'demo-model-v1.0',
                'provider': 'demo'
            },
            metadata={
                'processing_time': processing_time,
                'temperature': temperature,
                'top_p': top_p,
                'simulated': True
            }
        )
    
    async def health_check(self) -> bool:
        """Vérifier la santé simulée"""
        # Simuler occasionnellement une indisponibilité
        return random.random() > 0.05  # 95% de disponibilité
    
    def _detect_task_type(self, prompt: str) -> str:
        """Détecter le type de tâche à partir du prompt"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['analyser', 'analyse', 'étudier', 'examiner']):
            return 'analysis'
        elif any(word in prompt_lower for word in ['écrire', 'histoire', 'créer', 'rédiger']):
            return 'creative_writing'
        elif any(word in prompt_lower for word in ['code', 'algorithme', 'programmer', 'fonction']):
            return 'code_generation'
        else:
            return 'general'
    
    def _generate_response(self, task_type: str, prompt: str) -> str:
        """Générer une réponse basée sur le type de tâche"""
        if task_type in self.response_templates:
            # Choisir une réponse aléatoire parmi les templates
            template = random.choice(self.response_templates[task_type])
            
            # Ajouter une petite variation
            variations = [
                "Voici mon analyse :",
                "D'après mon évaluation :",
                "Selon mon analyse :",
                "Après examen :"
            ]
            
            if task_type == 'analysis':
                variation = random.choice(variations)
                return f"{variation}\n\n{template}"
            else:
                return template
        
        else:
            # Réponse générique
            return f"""Merci pour votre question. Voici ma réponse basée sur l'analyse de votre demande :

{prompt[:100]}...

Cette réponse est générée par le modèle de démonstration. Dans un environnement de production, 
cette réponse serait générée par un véritable modèle d'IA avec des capacités avancées de 
compréhension et de génération de texte.

Le système d'orchestration permet de coordonner plusieurs modèles d'IA pour obtenir des 
résultats optimaux grâce à la validation croisée et au consensus entre les différents modèles."""
    
    async def get_model_capabilities(self) -> Dict[str, Any]:
        """Retourner les capacités simulées du modèle"""
        return {
            'text_generation': True,
            'analysis': True,
            'creative_writing': True,
            'code_generation': True,
            'multilingual': False,
            'max_tokens': 4096,
            'supports_streaming': False,
            'supports_functions': False
        }

