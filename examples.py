"""
MORPHEUS Protocol - Basic Usage Examples
=========================================
Demonstrates the Triple-Judge Verification System in action.

Run this script to see how MORPHEUS handles:
1. Verified facts (GENERATE)
2. Unverified but plausible info (PRUDENCE)  
3. Logical contradictions (ABSTAIN)

Author: Kacem Mansouri
License: MIT
"""

import sys
import os

# Ensure the parent directory is in the path for local testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from morpheus import MORPHEUS


def print_separator(title: str):
    """Affiche un séparateur visuel pour chaque test."""
    print("\n" + "=" * 70)
    print(f"  TEST CASE: {title}")
    print("=" * 70)


def main():
    # Initialisation du protocole avec niveau de rigueur élevé
    morpheus = MORPHEUS(rigor_level='high')
    
    # --------------------------------------------------------------------------
    # CAS 1 : FAIT VÉRIFIÉ → GÉNÉRER
    # --------------------------------------------------------------------------
    print_separator("VERIFIED FACT (Should GENERATE)")
    
    result1 = morpheus.execute(
        question="What is the capital of France?",
        information="Paris is the capital of France.",
        context="France is a country in Western Europe. Paris is its capital and largest city."
    )
    
    print(f"\n📋 Response: {result1.response}")
    print(f"🔍 Decision: {result1.final_decision.value}")
    print(f"📊 Confidence: {result1.epistemic_confidence}%")
    print(f"️ Limitations: {result1.known_limitations}")
    
    # --------------------------------------------------------------------------
    # CAS 2 : INFORMATION NON VÉRIFIÉE → PRUDENCE
    # --------------------------------------------------------------------------
    print_separator("UNVERIFIED INFO (Should PRUDENCE)")
    
    result2 = morpheus.execute(
        question="Who won the 1976 World Cup?",
        information="Brazil won the 1976 World Cup.",
        context=None  # Aucun contexte fourni
    )
    
    print(f"\n📋 Response: {result2.response}")
    print(f"🔍 Decision: {result2.final_decision.value}")
    print(f"📊 Confidence: {result2.epistemic_confidence}%")
    
    # --------------------------------------------------------------------------
    # CAS 3 : CONTRADICTION LOGIQUE → ABSTENIR
    # --------------------------------------------------------------------------
    print_separator("LOGICAL CONTRADICTION (Should ABSTAIN)")
    
    result3 = morpheus.execute(
        question="What's the weather today?",
        information="It is raining heavily today.",
        context="The sky is clear and sunny with no clouds."
    )
    
    print(f"\n📋 Response: {result3.response}")
    print(f"🔍 Decision: {result3.final_decision.value}")
    print(f" Confidence: {result3.epistemic_confidence}%")
    
    # --------------------------------------------------------------------------
    # RÉSUMÉ FINAL
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  EXECUTION SUMMARY")
    print("=" * 70)
    print(f"  Test 1 (Verified):     {result1.final_decision.value:<10} | {result1.epistemic_confidence}% confidence")
    print(f"  Test 2 (Unverified):   {result2.final_decision.value:<10} | {result2.epistemic_confidence}% confidence")
    print(f"  Test 3 (Contradiction):{result3.final_decision.value:<10} | {result3.epistemic_confidence}% confidence")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()