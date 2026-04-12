from neural_plasticity_phenomenology_counterfactual import ReasoningTool

tool = ReasoningTool()

# Test 1: Conditional reasoning
print("Test 1: Conditional")
results = tool.evaluate(
    "If it rains, the ground gets wet. It rained.",
    ["The ground is wet", "The ground is dry"]
)
for r in results:
    print(f"  {r['candidate']}: {r['score']:.3f}")

# Test 2: Presupposition detection
print("\nTest 2: Presupposition (should have low confidence)")
conf = tool.confidence("Have you stopped cheating on tests?", "Yes")
print(f"  Confidence: {conf:.3f}")

# Test 3: Ambiguity detection
print("\nTest 3: Pronoun ambiguity (should have low confidence)")
conf = tool.confidence("John told Bill he was wrong. Who was wrong?", "John")
print(f"  Confidence: {conf:.3f}")

# Test 4: Normal question
print("\nTest 4: Normal question")
conf = tool.confidence("What is 2 + 2?", "4")
print(f"  Confidence: {conf:.3f}")

print("\nAll tests complete!")
