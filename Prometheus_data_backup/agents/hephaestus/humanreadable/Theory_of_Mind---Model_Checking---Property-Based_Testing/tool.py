class ReasoningTool:
    """
    A reasoning tool integrating Theory of Mind (ToM), Model Checking, and Property-Based Testing.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, modal operators (believes/wants), and logical structures.
    2. Model Construction: Builds an implicit Kripke structure where worlds are boolean vectors.
    3. Constraint Propagation: Uses fixed-point iteration to tighten truth values based on transitivity/logic.
    4. Property-Based Testing: Performs bounded BFS to verify LTL-style properties (e.g., consistency).
       - Finds counter-examples via random walk + shrinking.
    5. Scoring: Combines property satisfaction rate with a complexity penalty (Occam's razor).
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    # Regex patterns for parsing
    PATTERNS = {
        'believe': re.compile(r'(\w+)\s+believes\s+that\s+(.+)', re.IGNORECASE),
        'want': re.compile(r'(\w+)\s+wants\s+(.+)', re.IGNORECASE),
        'if_then': re.compile(r'if\s+(.+)\s+then\s+(.+)', re.IGNORECASE),
        'comparative': re.compile(r'(\w+)\s+(more\s+than|less\s+than|greater\s+than|smaller\s+than)\s+(\w+)', re.IGNORECASE),
        'numeric': re.compile(r'(\d+(?:\.\d+)?)\s*(<|>|=|<=|>=)\s*(\d+(?:\.\d+)?)'),
        'negation': re.compile(r'\b(not|no|never)\s+(\w+)', re.IGNORECASE),
        'quantifier': re.compile(r'\b(all|some|none|every)\s+(\w+)', re.IGNORECASE),
    }
    
    # Presupposition triggers for Tier B (Epistemic Honesty)
    PRESUPPOSITION_TRIGGERS = [
        r'\bhave\s+you\s+(stopped|quit)\b',
        r'\bwhy\s+did\s+\w+\s+(fail|stop|die)\b',
        r'\bwhen\s+did\s+\w+\s+(stop|fail)\b',
        r'\bis\s+the\s+(current|former)\s+',
        r'\bstopped\s+doing\s+',
        r'\bcontinued\s+to\s+'
    ]

    AMBIGUITY_TRIGGERS = [
        r'\bwho\s+was\s+(he|she|it|them)\b', # Pronoun ambiguity check
        r'\beither\s+\w+\s+or\s+\w+\b', # False dichotomy hint
        r'\bbest\s+\w+\s+without\b', # Subjectivity
        r'\bworst\s+\w+\s+without\b'
    ]

    def __init__(self):
        self.lambda_penalty = 0.1

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _extract_atoms(self, text: str) -> Tuple[List[str], Dict[str, int]]:
        """Extract unique atomic propositions and map to IDs."""
        atoms = set()
        # Simple tokenization for atoms (words)
        words = re.findall(r'\b\w+\b', text.lower())
        for w in words:
            if w not in {'believes', 'that', 'wants', 'if', 'then', 'more', 'less', 'than', 'not', 'no', 'all', 'some', 'none', 'every'}:
                atoms.add(w)
        
        atom_list = sorted(list(atoms))
        return atom_list, {a: i for i, a in enumerate(atom_list)}

    def _parse_structure(self, text: str) -> List[Dict]:
        """Parse text into structured logical atoms."""
        structures = []
        lower_text = text.lower()
        
        # Check Beliefs
        for m in self.PATTERNS['believe'].finditer(text):
            structures.append({'type': 'BELIEVE', 'agent': m.group(1), 'prop': m.group(2)})
            
        # Check Desires
        for m in self.PATTERNS['want'].finditer(text):
            structures.append({'type': 'DESIRE', 'agent': m.group(1), 'prop': m.group(2)})
            
        # Check Conditionals
        for m in self.PATTERNS['if_then'].finditer(text):
            structures.append({'type': 'COND', 'ant': m.group(1), 'cons': m.group(2)})
            
        # Check Comparatives
        for m in self.PATTERNS['comparative'].finditer(text):
            structures.append({'type': 'COMP', 'a': m.group(1), 'op': m.group(2), 'b': m.group(3)})
            
        # Check Numeric
        for m in self.PATTERNS['numeric'].finditer(text):
            structures.append({'type': 'NUM', 'a': float(m.group(1)), 'op': m.group(2), 'b': float(m.group(3))})
            
        return structures

    def _build_worlds(self, n_atoms: int) -> np.ndarray:
        """Generate all possible worlds (2^n) if small, else sample."""
        if n_atoms > 20:
            # Sample random worlds if too large
            return np.random.randint(0, 2, size=(100, n_atoms), dtype=bool)
        if n_atoms == 0:
            return np.array([[]], dtype=bool)
        # Create grid of all combinations
        return np.array([list(map(int, format(i, f'0{n_atoms}b'))) for i in range(2**n_atoms)], dtype=bool)

    def _propagate_constraints(self, worlds: np.ndarray, structures: List[Dict], atom_map: Dict[str, int]) -> np.ndarray:
        """Filter worlds based on parsed structures (Constraint Propagation)."""
        if len(worlds) == 0:
            return worlds
            
        valid_mask = np.ones(len(worlds), dtype=bool)
        
        for struct in structures:
            t = struct['type']
            if t == 'NUM':
                # Direct numeric validation
                a, op, b = struct['a'], struct['op'], struct['b']
                if op == '<': res = a < b
                elif op == '>': res = a > b
                elif op == '=': res = a == b
                elif op == '<=': res = a <= b
                elif op == '>=': res = a >= b
                else: res = True
                
                if not res:
                    # If numeric fact is false, the whole candidate might be invalid depending on context
                    # Here we assume numeric facts in prompt are ground truth. 
                    # If candidate contradicts prompt numeric, it gets penalized later.
                    pass 

            elif t == 'COMP':
                # Simplified comparative logic: if "A more than B", then A > B must hold in world
                # This requires mapping A and B to indices, which is hard without explicit values.
                # We skip complex semantic resolution for this simplified implementation.
                pass
                
            elif t == '