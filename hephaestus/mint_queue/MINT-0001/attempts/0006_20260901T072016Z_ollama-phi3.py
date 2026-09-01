import re
from collections import Counter

def op_vacuous_truth(state):
    problem_text = state.problem_text
    
    # Check for universal/negative-universal claims with empty domain using keywords and structure of the sentence
    if "each" in problem_text or "no" in problems:  # Assuming 'problems' is a list extracted from text containing negative statements, not provided here.
        words = re.findall(r'\b\w+\b', problem_text)
        word_count = Counter(words)
        
        if "no" in state.candidates or ("each" in problem_text and len(word_count) == 1):
            return True
    
    # Check for existential claims with empty domain using keywords like 'some' or explicit mention of zero items satisfying the predicate
    elif any(keyword in problem_text.lower() for keyword in ["some", "at least one"]):
        if state.candidates == []:
            return False
    
    # Default to abstain when no clear information about domain or counterexample is provided
    else:
        return None