"""
MORPHEUS Protocol Implementation
=================================
A systematic anti-hallucination framework for Large Language Models (LLMs).

This module implements the Triple-Judge Verification System designed to 
eliminate hallucinations while optimizing algorithmic efficiency.

Author: Kacem Mansouri
License: MIT
Version: 1.0.0
"""

import logging
from typing import Optional, Dict, Any, Literal
from enum import Enum
from dataclasses import dataclass, field

# Configuration du logging pour la traçabilité des vérifications
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MORPHEUS")


class Verdict(Enum):
    """Enumération des verdicts possibles pour chaque juge."""
    PASS = "✅"
    WARNING = "️"
    FAIL = "❌"


class Decision(Enum):
    """Décision finale basée sur l'agrégation des juges."""
    GENERATE = "GÉNÉRER"
    PRUDENCE = "PRUDENCE"
    ABSTAIN = "ABSTENIR"


@dataclass
class JudgeResult:
    """Résultat d'un juge individuel."""
    verdict: Verdict
    justification: str
    confidence: float = 0.0


@dataclass
class MorpheusOutput:
    """Structure de sortie standardisée du protocole MORPHEUS."""
    response: str
    source_grounding: JudgeResult
    factuality_check: JudgeResult
    logical_consistency: JudgeResult
    final_decision: Decision
    epistemic_confidence: float
    known_limitations: str


class MORPHEUS:
    """
    Système MORPHEUS - Protocole Anti-Hallucination.
    
    Implémente un moteur de raisonnement rigoureux exécutant obligatoirement
    le protocole de vérification avant toute génération de réponse.
    
    Attributes:
        rigor_level: Niveau de rigueur appliqué ('standard', 'high', 'maximal')
        _verdicts: Stockage temporaire des résultats des trois juges
    """

    def __init__(self, rigor_level: Literal['standard', 'high', 'maximal'] = 'standard'):
        self.rigor_level = rigor_level
        self._verdicts: Dict[str, JudgeResult] = {}
        logger.info(f"🛡️ MORPHEUS Protocol Initialized | Rigor Level: {rigor_level}")

    # --------------------------------------------------------------------------
    # SPLIT 400m : COMPRENDRE
    # --------------------------------------------------------------------------
    def split_400m_understand(self, question: str, context: Optional[str] = None) -> bool:
        """
        Étape 1 : Compréhension et détection d'ambiguïté.
        
        Args:
            question: La requête utilisateur à analyser.
            context: Contexte fourni (optionnel).
            
        Returns:
            True si la compréhension est validée, False si clarification nécessaire.
        """
        logger.info("🏃 SPLIT 400m - Compréhension en cours...")
        
        if not question or len(question.strip()) < 3:
            logger.warning("Question trop courte ou vide détectée.")
            return False
            
        # Détection basique d'ambiguïté sémantique
        ambiguous_markers = ['peut-être', 'parfois', 'généralement', 'souvent', 'quelque chose']
        has_ambiguity = any(marker in question.lower() for marker in ambiguous_markers)
        
        if has_ambiguity and self.rigor_level == 'maximal':
            logger.warning("Ambiguïté détectée en mode maximal. Clarification requise.")
            return False
            
        logger.info("✅ Compréhension validée.")
        return True

    # --------------------------------------------------------------------------
    # SPLIT 800m : VÉRIFIER (Triple Juge)
    # --------------------------------------------------------------------------
    def split_800m_verify(self, information: str, context: Optional[str] = None) -> Dict[str, JudgeResult]:
        """
        Étape 2 : Vérification par les trois juges indépendants.
        
        Args:
            information: L'affirmation ou donnée à vérifier.
            context: Contexte de référence pour le Source Grounding.
            
        Returns:
            Dictionnaire contenant les résultats des trois juges.
        """
        logger.info("🏃 SPLIT 800m - Vérification Triple Juge en cours...")
        
        # JUGE 1 : Le Détective (Source Grounding)
        if context and information.strip().lower() in context.strip().lower():
            self._verdicts['source_grounding'] = JudgeResult(
                verdict=Verdict.PASS,
                justification="Information présente littéralement dans le contexte fourni.",
                confidence=100.0
            )
        else:
            self._verdicts['source_grounding'] = JudgeResult(
                verdict=Verdict.FAIL,
                justification="Information absente du contexte fourni.",
                confidence=0.0
            )
        
        # JUGE 2 : L'Expert (Factuality Check)
        # NOTE: Dans une implémentation production, connecter ici une API RAG / Base de connaissances
        facts_db = ['paris est la capitale de la france', '2+2=4', 'l\'eau bout à 100 degrés']
        info_lower = information.strip().lower()
        
        if any(fact in info_lower for fact in facts_db):
            self._verdicts['factuality_check'] = JudgeResult(
                verdict=Verdict.PASS,
                justification="Fait vérifié dans la base de connaissances interne.",
                confidence=95.0
            )
        elif self._verdicts['source_grounding'].verdict == Verdict.PASS:
            # Si c'est dans le contexte, on considère que c'est factuellement acceptable pour ce tour
            self._verdicts['factuality_check'] = JudgeResult(
                verdict=Verdict.WARNING,
                justification="Non vérifiable externement, mais présent dans le contexte.",
                confidence=70.0
            )
        else:
            self._verdicts['factuality_check'] = JudgeResult(
                verdict=Verdict.WARNING,
                justification="Non vérifiable automatiquement sans source externe.",
                confidence=50.0
            )

        # JUGE 3 : Le Logicien (Logical Consistency)
        contradiction_markers = ['mais', 'cependant', 'toutefois', 'contrairement', 'pourtant']
        has_contradiction = context and any(m in information.lower() for m in contradiction_markers)
        
        if has_contradiction:
            self._verdicts['logical_consistency'] = JudgeResult(
                verdict=Verdict.FAIL,
                justification="Contradiction potentielle détectée avec le contexte.",
                confidence=0.0
            )
        else:
            self._verdicts['logical_consistency'] = JudgeResult(
                verdict=Verdict.PASS,
                justification="Aucune contradiction logique interne détectée.",
                confidence=90.0
            )
            
        logger.info("✅ Vérification Triple Juge terminée.")
        return self._verdicts

    # --------------------------------------------------------------------------
    # SPLIT 1200m : DÉCIDER
    # --------------------------------------------------------------------------
    def split_1200m_decide(self) -> tuple[Decision, float]:
        """
        Étape 3 : Agrégation des verdicts et prise de décision.
        
        Returns:
            Tuple contenant la décision finale et le score de confiance épistémique.
        """
        logger.info("🏃 SPLIT 1200m - Prise de décision...")
        
        scores = [j.confidence for j in self._verdicts.values()]
        avg_confidence = sum(scores) / len(scores) if scores else 0.0
        
        fail_count = sum(1 for j in self._verdicts.values() if j.verdict == Verdict.FAIL)
        warn_count = sum(1 for j in self._verdicts.values() if j.verdict == Verdict.WARNING)
        
        # Logique de décision stricte
        if fail_count > 0:
            decision = Decision.ABSTAIN
            avg_confidence = 0.0
        elif warn_count > 0:
            decision = Decision.PRUDENCE
        else:
            decision = Decision.GENERATE
            
        logger.info(f"Décision: {decision.value} | Confiance: {avg_confidence:.1f}%")
        return decision, avg_confidence

    # --------------------------------------------------------------------------
    # ARRIVÉE : FORMATER & EXÉCUTER
    # --------------------------------------------------------------------------
    def execute(self, question: str, information: str, context: Optional[str] = None) -> MorpheusOutput:
        """
        Exécute le protocole MORPHEUS complet et retourne la réponse formatée.
        
        Args:
            question: La requête originale.
            information: La réponse candidate générée par le LLM.
            context: Contexte de référence (RAG ou prompt système).
            
        Returns:
            Objet MorpheusOutput contenant la réponse et les métadonnées de vérification.
        """
        print("=" * 60)
        print("DÉMARRAGE DU PROTOCOLE MORPHEUS")
        print("=" * 60)
        
        # Split 400m
        if not self.split_400m_understand(question, context):
            return MorpheusOutput(
                response="❌ AMBIGUÏTÉ DÉTECTÉE : Veuillez reformuler votre question avec plus de précision.",
                source_grounding=JudgeResult(Verdict.FAIL, "Question ambiguë", 0),
                factuality_check=JudgeResult(Verdict.FAIL, "Non évalué", 0),
                logical_consistency=JudgeResult(Verdict.FAIL, "Non évalué", 0),
                final_decision=Decision.ABSTAIN,
                epistemic_confidence=0.0,
                known_limitations="Le système nécessite une question non ambiguë pour fonctionner."
            )
        
        # Split 800m
        self.split_800m_verify(information, context)
        
        # Split 1200m
        decision, confidence = self.split_1200m_decide()
        
        # Formatage de la réponse finale
        if decision == Decision.ABSTAIN:
            final_response = f"❌ Je ne peux pas répondre avec certitude. {self._verdicts.get('logical_consistency', JudgeResult(Verdict.FAIL, '', 0)).justification}"
        elif decision == Decision.PRUDENCE:
            final_response = f"⚠️ Réponse sous réserve : {information}\n\nNote: Cette information n'a pas pu être entièrement vérifiée par tous les juges."
        else:
            final_response = information
            
        print("=" * 60)
        print("PROTOCOLE MORPHEUS TERMINÉ")
        print("=" * 60)
        
        return MorpheusOutput(
            response=final_response,
            source_grounding=self._verdicts['source_grounding'],
            factuality_check=self._verdicts['factuality_check'],
            logical_consistency=self._verdicts['logical_consistency'],
            final_decision=decision,
            epistemic_confidence=confidence,
            known_limitations="Vérification automatique limitée aux bases de connaissances intégrées. Nécessite validation humaine pour les sujets critiques."
        )


# ==============================================================================
# TEST UNITAIRE RAPIDE (À SUPPRIMER EN PRODUCTION)
# ==============================================================================
if __name__ == "__main__":
    morpheus = MORPHEUS(rigor_level='high')
    
    # Test 1 : Cas valide avec contexte
    result1 = morpheus.execute(
        question="Quelle est la capitale de la France ?",
        information="Paris est la capitale de la France.",
        context="La France est un pays d'Europe occidentale. Paris est sa capitale."
    )
    print(f"\n[RÉSULTAT TEST 1] Décision: {result1.final_decision.value} | Confiance: {result1.epistemic_confidence}%")
    
    # Test 2 : Cas contradictoire
    result2 = morpheus.execute(
        question="Quel temps fait-il ?",
        information="Il pleut aujourd'hui.",
        context="Le soleil brille et il fait beau aujourd'hui."
    )
    print(f"[RÉSULTAT TEST 2] Décision: {result2.final_decision.value} | Confiance: {result2.epistemic_confidence}%")