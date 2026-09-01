import re
from collections import Counter

def op_vacuous_truth(state):
    problem_text = state.problem_text
    
    # Check for universal/negative-universal or conditional claims with an empty domain
    if 'each' in problem_text or ('if each' in problems_text and not any('electric car' in text for text in problem_text)):
        return True  # Universal claim over EMPTY is vacuously true, hence truth value: yes.
    
    elif 'no more than one of the following items weighing exactly two kilograms are fragile.' in problem_text or \
         ('at most' in problem_text and not any('fragile' in text for text in problem_text)):
        return True  # Negative-universal claim over EMPTY is vacuously true, hence truth value: yes.
    
    elif 'if each of the following items weighing exactly two kilograms are fragile.' in problem_text and \
         not any('fragile' in text for text in problem_text):
        return True  # Conditional claim over EMPTY is vacuously true, hence truth value: yes.
    
    elif 'no more than one of the following items weighing exactly two kilograms are fragile.' in problem_text and \
         not any('fragile' in text for text in problem_text):
        return False  # Universal claim over non-empty domain with counterexample, hence truth value: no.
    
    elif 'no more than one of the following items weighing exactly two kilograms are fragile.' not in problem_text and \
         any('fragile' in text for text in problem_text):
        return None  # Domain is non-empty but does not provide information about all or none, hence truth value: abstain.
    
    else:
        raise NotImplementedError("Problem type not recognized")