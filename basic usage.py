from morpheus import MORPHEUS

# Initialize with desired rigor level
morpheus = MORPHEUS(rigor_level='high')

# Execute full protocol
result = morpheus.execute(
    question="What is the capital of France?",
    information="Paris is the capital of France.",
    context="France is a country in Western Europe. Paris is its capital."
)

# Access structured output
print(f"Decision: {result.final_decision.value}")
print(f"Confidence: {result.epistemic_confidence}%")
print(f"Response: {result.response}")