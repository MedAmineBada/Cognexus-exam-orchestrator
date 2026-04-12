organize_exam_text_prompt = r"""
    You will receive raw text extracted from an exam PDF. The text may contain noise such as headers, page numbers, formatting artifacts, and repeated titles.

    Your task is to clean the content and convert it into structured JSON.

    Remove:
    - headers
    - footers
    - page numbers
    - repeated exam titles
    - formatting artifacts

    Keep:
    - the logical structure of exercises

    SPECIAL HANDLING RULES

    1. TEXT VS QUESTION
    - If an exercise contains only a question (no separate description, context, or introduction), then:
      - Set "text" to null
      - Put ALL content inside the "question" field
    - Only use "text" when there is clear introductory/contextual information separate from the question(s)

    2. LATEX EXTRACTION
    - Any mathematical expressions, equations, symbols, or formulas MUST be converted into valid LaTeX code
    - Do NOT keep raw symbols like √, ∑, fractions, etc.
    - Convert them into proper LaTeX using these EXACT commands:
      * Square root: \sqrt{}
      * Fractions: \frac{}{}
      * Summation: \sum
      * Multiplication (cross): \times
      * Multiplication (dot, only if explicitly a dot product): \cdot
      * Plus/minus: \pm
      * Greek letters: \alpha, \beta, \Delta, etc.
      * Powers: x^{2}
      * Subscripts: x_{i}

    3. LATEX BACKSLASH RULES (CRITICAL)
    - ALL LaTeX commands use a SINGLE backslash with NO space after it: \frac, \sqrt, \times, \pm
    - NEVER put a space between the backslash and the command name: "\ frac" is WRONG, "\frac" is CORRECT
    - NEVER double the backslash: \\frac is WRONG, \frac is CORRECT
    - NEVER write \\ before a Greek letter: \\Delta is WRONG, \Delta is CORRECT
    - These are the most important rules. Violating them will completely break rendering.

    4. LATEX MARKING (IMPORTANT)
    - Wrap ALL LaTeX content using:
      - Inline math: $...$
      - Block math (if clearly separate): $$...$$
    - This must be applied consistently so LaTeX is easily detectable and renderable in a frontend

    Examples of CORRECT output:
    - "x^2 + y^2 = 1" → "$x^2 + y^2 = 1$"
    - Standalone equation → "$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$"
    - Square root of 5 → "$\sqrt{5}$"
    - Half times root 5 → "$\frac{1}{2} \times \sqrt{5}$"
    - Discriminant → "$\Delta = b^2 - 4ac$"

    Examples of WRONG output (never do this):
    - "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$"  ← double backslashes are WRONG
    - "$\\sqrt{5}$"  ← double backslash is WRONG
    - "$\ frac{1}{2}$"  ← space after backslash is WRONG
    - "$\ \Delta$"  ← space and extra backslash are WRONG
    - "$\cdot$" for regular multiplication ← use \times instead

    5. MULTIPLICATION OPERATOR RULE
    - Use \times for general multiplication (e.g., 2 \times 3, \frac{1}{2} \times \sqrt{5})
    - Only use \cdot when the source explicitly shows a dot product or dot notation

    OUTPUT FORMAT

    Return ONLY valid JSON.

    Structure:

    {
      "1": {
        "text": "main description or null if none",
        "grading": "total points of the exercise",
        "given": ["list of given values, assumptions, constants"],
        "examples": ["examples provided in the exercise"],
        "questions": {
          "1": {
            "question": "question text (with LaTeX properly wrapped)",
            "grade": "points if specified, otherwise null",
            "type": "hv or lv"
          }
        }
      }
    }

    QUESTION TYPE DEFINITIONS

    - "hv" (High-Variation):
      Use for open-ended responses requiring reasoning or multiple possible answers.
      Examples:
      - math problem solving
      - coding tasks
      - essays
      - explanations
      - critiques

    - "lv" (Low-Variation):
      Use for constrained or objective answers.
      Examples:
      - multiple choice questions (MCQ)
      - true/false
      - single-answer fill-in-the-blank
      - short factual responses

    RULES
    1. Each exercise must be keyed by its number.
    2. Do not invent information.
    3. Assign "type" to every question based on its expected answer format.
    4. Use null when a field is not present (do NOT leave empty strings).
    5. Ensure all mathematical content is valid LaTeX and properly wrapped in $ or $$.
    6. Return ONLY JSON. Do NOT wrap the result in markdown or code blocks.
    7. NEVER use double backslashes (\\) in LaTeX commands. Always single backslash (\).
    8. NEVER put a space after a backslash: "\ frac" is WRONG, "\frac" is CORRECT.
    9. ALWAYS use \times for multiplication unless dot product is explicitly indicated.

    Now process the following raw extracted exam text:

"""

def generate_organize_correction_prompt(exam_content: dict, correction_text: str) -> str:
    """
    Generates a prompt to organize correction text to match exam structure.

    Args:
        exam_content (dict): Structured exam JSON as dictionary
        correction_text (str): Raw correction text extracted from PDF

    Returns:
        str: Formatted prompt ready to be sent to LLM
    """
    import json

    # Convert exam_content dict to formatted JSON string
    exam_json_str = json.dumps(exam_content, indent=2, ensure_ascii=False)

    prompt = f"""You will receive two inputs:
    1. A structured JSON of an exam with exercises and questions
    2. Raw text extracted from the correction/answer key PDF
    
    The correction text may contain noise such as headers, page numbers, formatting artifacts, and repeated titles.
    
    Your task is to clean the correction content and match it to the corresponding exercises and questions from the exam JSON, adding answer/correction information to each question.
    
    Remove from correction text:
    - headers
    - footers
    - page numbers
    - repeated exam titles
    - formatting artifacts
    
    Keep:
    - solution steps and explanations
    - grading rubrics or point distributions
    - final answers
    
    OUTPUT FORMAT
    
    Return ONLY valid JSON.
    
    Structure:
    
    {{
      "1": {{
          "1": "the correct answer"
      }}
    }}
    
    RULES
    1. Preserve the exact structure and numbering from the exam JSON
    2. Match correction content to the corresponding exercise and question numbers
    3. If correction text for a question is not found, set "correction" to null
    4. Do not invent information - only use what's in the correction text
    5. Keep all original content
    6. Return ONLY JSON. Do NOT wrap the result in ```json``` or markdown.
    
    EXAM JSON:
    {exam_json_str}
    
    CORRECTION TEXT:
    {correction_text}
    
    Now process and merge these inputs:"""

    return prompt


