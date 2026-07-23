import sys
sys.path.append("ml_models")
from similarity_scorer import calculate_similarity

text_a = "I have experience building machine learning models using Python."
text_b = "Proficient in developing ML models with Python programming."
score1 = calculate_similarity(text_a, text_b)
print(f"Test 1 (same meaning, different words): {score1}%")

text_c = "I enjoy cooking Italian food on weekends."
score2 = calculate_similarity(text_a, text_c)
print(f"Test 2 (unrelated content): {score2}%")

score3 = calculate_similarity(text_a, text_a)
print(f"Test 3 (identical text): {score3}%")