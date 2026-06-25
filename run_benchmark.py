"""
MORPHEUS Benchmark Runner
=========================
Automated evaluation of the Triple-Judge Verification System 
against a dataset of trick questions.

Generates a structured report comparing MORPHEUS decisions 
with expected behaviors.

Author: Kacem Mansouri
License: MIT
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Ensure parent directory is in path for local execution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from morpheus import MORPHEUS, Decision


class BenchmarkRunner:
    """Orchestrates the execution of MORPHEUS against the benchmark dataset."""

    def __init__(self, benchmark_path: str = "benchmarks/trick_questions.json", rigor_level: str = 'high'):
        self.benchmark_path = benchmark_path
        self.morpheus = MORPHEUS(rigor_level=rigor_level)
        self.results: List[Dict[str, Any]] = []
        
    def load_benchmark(self) -> List[Dict]:
        """Loads and validates the benchmark JSON file."""
        if not os.path.exists(self.benchmark_path):
            raise FileNotFoundError(f"Benchmark file not found: {self.benchmark_path}")
            
        with open(self.benchmark_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f" Loaded {len(data['questions'])} test cases from {data['benchmark_metadata']['name']}")
        return data['questions']

    def evaluate_case(self, case: Dict) -> Dict[str, Any]:
        """Runs a single test case through MORPHEUS and compares with ground truth."""
        # Execute MORPHEUS protocol
        result = self.morpheus.execute(
            question=case['question'],
            information="N/A",  # Information will be evaluated by the judges based on context/knowledge
            context=None        # Context is intentionally empty to test base knowledge verification
        )
        
        # Determine pass/fail status
        passed = (result.final_decision.value == case['expected_behavior'])
        
        return {
            'id': case['id'],
            'category': case['category'],
            'question': case['question'],
            'expected': case['expected_behavior'],
            'actual': result.final_decision.value,
            'confidence': result.epistemic_confidence,
            'passed': passed,
            'trap_type': case['trap_type']
        }

    def run(self) -> None:
        """Executes the full benchmark suite and prints the report."""
        print("\n" + "=" * 80)
        print("  MORPHEUS BENCHMARK EXECUTION v1.0")
        print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")
        
        questions = self.load_benchmark()
        
        for i, case in enumerate(questions, 1):
            print(f"[{i}/{len(questions)}] Running: {case['id']} ({case['category']})...")
            result = self.evaluate_case(case)
            self.results.append(result)
            
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"      Expected: {result['expected']} | Actual: {result['actual']} | {status}")
            
        self._print_summary()

    def _print_summary(self) -> None:
        """Prints the final aggregated performance report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        accuracy = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("  BENCHMARK SUMMARY REPORT")
        print("=" * 80)
        print(f"  Total Test Cases : {total}")
        print(f"  Passed           : {passed}")
        print(f"  Failed           : {total - passed}")
        print(f"  Accuracy         : {accuracy:.1f}%")
        print("-" * 80)
        
        # Breakdown by category
        categories = {}
        for r in self.results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if r['passed']:
                categories[cat]['passed'] += 1
                
        print("  PERFORMANCE BY CATEGORY:")
        for cat, stats in categories.items():
            cat_acc = (stats['passed'] / stats['total'] * 100)
            print(f"    - {cat:<30} : {cat_acc:.1f}% ({stats['passed']}/{stats['total']})")
            
        print("=" * 80 + "\n")


if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run()