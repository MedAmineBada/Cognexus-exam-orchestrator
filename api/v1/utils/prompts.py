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


def generate_organize_correction_prompt(
    exam_content: dict, correction_text: str
) -> str:
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


def generate_organize_submission_prompt(exam_content: dict, ocr_result: list) -> str:
    """
    Generates a prompt to organize OCR result to match exam structure.

    Args:
        exam_content (dict): Structured exam JSON as dictionary
        ocr_result (list): List of OCR results from scanned submission images

    Returns:
        str: Formatted prompt ready to be sent to LLM
    """
    import json
    import re

    exam_json_str = json.dumps(exam_content, indent=2, ensure_ascii=False)

    # Concatenate all OCR text from all pages/images
    # Replace $math[i]$ placeholders with actual LaTeX from the math array
    full_ocr_text_parts = []

    for item in ocr_result:
        text = item["text"]
        math_array = item.get("math", [])

        # Replace all $math[i]$ with actual math content
        def replace_math(match):
            index = int(match.group(1))
            if 0 <= index < len(math_array):
                return math_array[index]
            return match.group(0)  # Keep original if index out of range

        text = re.sub(r"\$math\[(\d+)\]\$", replace_math, text)

        full_ocr_text_parts.append(f"[Image: {item['filename']}]\n{text}")

    full_ocr_text = "\n\n".join(full_ocr_text_parts)

    prompt = f"""You will receive two inputs:
    1. A structured JSON of an exam with exercises and questions
    2. Raw OCR text extracted from a student's handwritten or printed submission (possibly spanning multiple images/pages)
    
    Your task is to read the student's submission and map each answer to its corresponding exercise and question in the exam JSON.
    
    The OCR text may contain:
    - Noise, spelling errors, or garbled characters (due to handwriting recognition)
    - Student names, headers, or irrelevant text
    - Answers written in various formats (e.g., "Ex1", "Exercise 1", "Q1", "1.", "a)", etc.)
    - Mathematical expressions in plain text or LaTeX notation
    
    MATCHING RULES
    1. Use context clues and the exam questions to figure out which answer belongs to which exercise/question
    2. If the student clearly labels their answer (e.g., "Exercise 2, Q1" or "Ex2 a)"), use that
    3. If labeling is absent or ambiguous, use the order of answers and the exam structure to infer the mapping
    4. If no answer can be found for a question, set its value to null
    5. Do NOT invent or complete answers — only extract what the student wrote
    6. Keep the student's answer as-is (do not correct spelling or content)
    7. For math answers, preserve all mathematical expressions and working steps shown by the student
    
    OUTPUT FORMAT
    
    Return ONLY valid JSON with this exact structure:
    
    {{
      "1": {{
        "1": "student's answer to exercise 1 question 1",
        "2": "student's answer to exercise 1 question 2"
      }},
      "2": {{
        "1": "student's answer to exercise 2 question 1"
      }}
    }}
    
    The keys must match exactly the exercise and question numbers from the exam JSON.
    Return ONLY JSON. Do NOT wrap the result in ```json``` or markdown code blocks.
    
    EXAM JSON:
    {exam_json_str}
    
    STUDENT SUBMISSION (OCR):
    {full_ocr_text}
    
    Now process and map the student's answers to the exam structure:"""

    return prompt


def generate_grading_prompt(grading_model: dict) -> str:
    import json

    grading_model_str = json.dumps(grading_model, indent=2, ensure_ascii=False)

    prompt = f"""You are a strict but fair academic examiner. Your task is to grade a student's exam submission.

You will receive a grading model containing:
- The exam exercise text and context
- The correct answer/correction for each question
- The student's submitted answer for each question
- The question type (hv or lv) found in each question's "type" field
- Grade allocations per exercise ("grading" field) and/or per question ("grade" field)

---

GRADING SCALE RULE (CRITICAL)
- ALL grades MUST be in 0.25 increments ONLY
- Valid values: 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, ... etc.
- FORBIDDEN: any grade like 1.1, 1.3, 1.9, 0.6, etc.
- If your raw assessment gives you a non-0.25 value, round to the nearest 0.25
- Grade strings may contain units like "4pts" or "1pt" — extract the numeric value and ignore the unit

---

GRADE ALLOCATION RULES

CASE 1 — Per-question "grade" field is provided (e.g., "grade": "2pt"):
- Use that grade as the maximum for that specific question
- Do NOT redistribute

CASE 2 — Only total exercise "grading" is provided (e.g., "grading": "4pts") with no per-question grades:
- Convert the total into 0.25 units
- Divide evenly among all questions in that exercise
- If remainder exists after equal distribution, distribute the remaining 0.25 units across questions you judge to be more important or difficult based on the question content and type
- The sum of all question grades in an exercise MUST equal the exercise total

Example of CASE 2:
- Total = 4 points, 3 questions
- 4 / 3 = 1.33 → not a valid increment
- Convert: 4 = 16 units of 0.25
- 16 / 3 = 5 units each (1.25) with 1 unit (0.25) remaining
- Distribute remaining to the hardest/most important question
- Result: two questions get 1.25, one question gets 1.5
- You decide which question gets the extra 0.25 based on complexity and type

---

QUESTION TYPE RULES (CRITICAL)
Each question has a "type" field, either "hv", "lv", or null:

QUESTION TYPE FALLBACK:
- If the "type" field is null or missing, default to "hv"
- Apply rubric based partial credit grading in that case

"lv" (Low-Variation) — MCQ, true/false, single answer fill-in-the-blank:
- Grading is BINARY: full marks or zero, NO partial credit
- The answer is either correct or it is not
- Do not award 0.25 or 0.5 for a wrong lv answer
- Confidence for lv questions should generally be high (0.9-1.0) unless the answer is corrupted

"hv" (High-Variation) — open ended, math, essay, explanation, coding:
- Use rubric based partial credit (0, 25%, 50%, 75%, 100% of max)
- See GRADING METHODOLOGY section below for detailed hv grading rules per sub-type

---

GRADING METHODOLOGY

For ALL question types:
- Compare the student's answer to the correction using the exam context and the question itself
- Grade based on conceptual accuracy, completeness, and relevance

---

LATEX AND MATHEMATICAL NOTATION HANDLING

When comparing student answers to corrections:
- The correction may contain LaTeX notation wrapped in $ or $$ (e.g., "$\pi r^2$", "$x^{2}$")
- The student's answer (from OCR) will likely contain plain text or symbols (e.g., "pi r squared", "πr²", "x^2")
- Do NOT penalize the student for writing math in plain text or using symbols instead of LaTeX
- Treat these as EQUIVALENT:
  - "$\pi r^2$" = "pi r squared" = "πr²" = "A = πr²"
  - "$x^{2}$" = "x^2" = "x squared"
  - "$\frac{{1}}{{2}}$" = "1/2" = "½"
  - "$\sqrt{{5}}$" = "sqrt(5)" = "√5"
  - "$\Delta$" = "delta" = "Δ"
  - "$\times$" = "×" = "*" = "x" (when clearly multiplication)
- Focus on mathematical MEANING, not notation format
- If the student's mathematical expression is correct but uses different notation, award full marks for that part

Examples:
- Correction: "$A = \pi r^{{2}}$"
- Student: "Area = pi times r squared" → CORRECT, award full marks
- Student: "A = πr²" → CORRECT, award full marks
- Student: "A = 2πr" → INCORRECT, wrong formula

--- MATH QUESTIONS (hv) ---
Math questions involve equations, calculations, proofs, or numerical problem solving.

Grading priority (in order):
1. METHODOLOGY (worth ~70% of the grade):
   - Did the student use the correct approach and formula?
   - Did they show their working steps?
   - Did they set up the problem correctly?
2. INTERMEDIATE STEPS (worth ~20% of the grade):
   - Are the intermediate calculations correct?
   - Are units carried through correctly?
3. FINAL RESULT (worth ~10% of the grade):
   - Is the final numerical answer correct?
   - A correct answer with no working shown gets at most 25% of marks

Partial credit levels for math:
- 100%: Correct method, correct steps, correct answer
- 75%: Correct method, correct steps, minor arithmetic error in final answer
- 50%: Correct method setup but significant errors in execution
- 25%: Some relevant formulas or concepts used but mostly incorrect approach
- 0%: Wrong method, irrelevant content, or blank

--- CODING QUESTIONS (hv) ---
Coding questions involve writing, completing, or debugging code.

Grading priority (in order):
1. LOGIC AND APPROACH (worth ~60% of the grade):
   - Does the student's solution follow the correct algorithmic logic?
   - Is the overall structure of the solution correct?
   - Are edge cases considered?
2. IMPLEMENTATION (worth ~30% of the grade):
   - Is the syntax mostly correct?
   - Are the right data structures or constructs used?
   - Does the code look like it would run correctly?
3. FINAL OUTPUT CORRECTNESS (worth ~10% of the grade):
   - Would the code produce the correct output?
   - Minor syntax errors that don't affect logic should not heavily penalize

Partial credit levels for coding:
- 100%: Correct logic, correct implementation, would produce correct output
- 75%: Correct logic and approach, minor syntax or implementation errors
- 50%: Partially correct logic, correct structure but missing key parts
- 25%: Some relevant constructs or logic used but fundamentally flawed approach
- 0%: Completely wrong, irrelevant, or blank

--- ESSAY QUESTIONS (hv) ---

ESSAY DETECTION:
First, determine if the question is an ACTUAL ESSAY or just a long-form explanation/description:

An ACTUAL ESSAY has these characteristics in the question prompt:
- Asks to "write an essay", "compose", "discuss in essay format"
- Requires formal structured writing (introduction, body, conclusion)
- Asks for argumentative, persuasive, or narrative writing
- Specifies word count or paragraph requirements
- Asks to "analyze and discuss", "compare and contrast", "argue for/against"

NOT an essay (just explanations/descriptions):
- "Explain how...", "Describe the process...", "What is...and why?"
- "Define and give examples..."
- Short answer conceptual questions
- Technical descriptions or step-by-step explanations

IF THE QUESTION IS AN ACTUAL ESSAY:

Grading is divided into TWO major components:

A. CONTENT (worth 60% of the grade):
   1. CONCEPTUAL ACCURACY (30%):
      - Is the core argument or thesis correct and relevant?
      - Does the student demonstrate understanding of the topic?
      - Are the ideas logically sound?

   2. COMPLETENESS (20%):
      - Are all required points addressed?
      - Is there sufficient depth and development of ideas?
      - Are examples and evidence provided?

   3. STRUCTURE AND ORGANIZATION (10%):
      - Is there a clear introduction, body, and conclusion?
      - Do paragraphs flow logically?
      - Are transitions smooth?

B. WRITING QUALITY (worth 40% of the grade):
   1. GRAMMAR AND SYNTAX (15%):
      - Are sentences grammatically correct?
      - Are there subject-verb agreement errors?
      - Are tenses used correctly?
      - Deduct for: run-on sentences, fragments, major grammatical errors

   2. PUNCTUATION AND MECHANICS (10%):
      - Correct use of commas, periods, semicolons, etc.
      - Proper capitalization
      - Correct spelling (not OCR-related errors)
      - Deduct for: missing punctuation, incorrect comma usage, spelling mistakes

   3. VOCABULARY AND LANGUAGE USE (10%):
      - Appropriate and varied vocabulary
      - Sophisticated word choices where appropriate
      - Avoidance of repetitive or overly simplistic language
      - Academic tone maintained
      - Reward: rich vocabulary, precise word choice, eloquent expression
      - Deduct for: repetitive words, overly simple language, informal tone

   4. CLARITY AND STYLE (5%):
      - Clear and concise expression
      - Appropriate sentence variety
      - Engaging writing style

IMPORTANT ESSAY GRADING NOTES:
- A student with perfect content but poor grammar/vocabulary should NOT get full marks
- A student with excellent writing quality but weak content should get ~40% max
- Beautiful, well-structured essays with rich vocabulary deserve higher grades than grammatically weak essays with same content
- Do NOT penalize OCR artifacts (garbled words due to scanning), but DO penalize actual spelling/grammar errors
- Compare writing quality between what the student demonstrated vs. what is expected at their academic level

Partial credit levels for ESSAYS:
- 100%: Excellent content (60%) + Excellent writing (40%) - grammatically flawless, sophisticated vocabulary, well-structured
- 75%: Strong content with minor gaps + Good writing with few grammatical errors and decent vocabulary
- 50%: Adequate content but missing key elements + Acceptable writing with multiple grammatical errors and simple vocabulary
- 25%: Weak content with some relevance + Poor writing with major grammatical issues and very basic language
- 0%: Completely off-topic or blank

IF THE QUESTION IS NOT AN ESSAY (just explanation/description):

Grading priority (in order):
1. CONCEPTUAL ACCURACY (worth ~50% of the grade):
   - Is the core idea or concept correct?
   - Does the student demonstrate understanding?
2. COMPLETENESS (worth ~30% of the grade):
   - Are all required points addressed?
   - Is the answer sufficiently detailed?
3. CLARITY AND RELEVANCE (worth ~20% of the grade):
   - Is the answer clear and on-topic?
   - Are irrelevant points included that dilute the answer?

For non-essay explanations, do NOT heavily penalize grammar/vocabulary as long as the meaning is clear.

Partial credit levels for non-essay explanations:
- 100%: Fully correct, complete, and clearly expressed
- 75%: Mostly correct with minor omissions or slight inaccuracies
- 50%: Core concept correct but missing significant details or partially off-topic
- 25%: Minimal correct elements, mostly incorrect or irrelevant
- 0%: Completely wrong, irrelevant, or blank

---

OCR NOISE AWARENESS (IMPORTANT)
- The student's answer was extracted via OCR from a handwritten or printed submission
- The text may contain garbled characters, missing words, spelling errors, or broken sentences due to OCR artifacts
- Do NOT penalize the student for spelling mistakes or minor text corruption that are clearly OCR-related
- For coding questions: do not penalize for garbled variable names or symbols that are clearly OCR artifacts
- For math questions: do not penalize for garbled symbols that are clearly OCR artifacts, try to infer the intended formula
- For essays: distinguish between OCR corruption (garbled text, nonsense words) vs. actual spelling/grammar errors
- Try to infer the intended meaning from context before grading
- If the answer is so corrupted it is completely unreadable or meaningless, award 0 and set "flag" to true

---

LANGUAGE DETECTION
- Detect the language the student used in their answers
- Write all "feedback" fields in the SAME language the student used
- If the student's language cannot be determined (blank, null, corrupted), default to English for feedback

---

FLAGGING RULES
- Set "flag" to true and provide a "flag_reason" when ANY of the following apply:
  1. The answer appears heavily corrupted by OCR and meaning cannot be inferred
  2. The student's answer is word-for-word identical to the correction (possible plagiarism)
  3. The grading was ambiguous and confidence is below 0.6
  4. The answer is in a language or format that makes grading unreliable
- Set "flag" to false otherwise
- "flag_reason" should be null when "flag" is false

---

CONFIDENCE SCORE
- After grading each question, assign a "confidence" score between 0.0 and 1.0
- This reflects how certain you are that your awarded grade is accurate
- 1.0 = completely certain (e.g., clear correct/incorrect lv answer)
- 0.8 = mostly certain with minor ambiguity
- 0.6 = borderline, could reasonably go either way
- Below 0.6 = uncertain, must set "flag" to true
- lv questions should typically score 0.9-1.0 unless corrupted
- Be honest, do not always return 1.0

---

OUTPUT FORMAT

Return ONLY valid JSON. Do NOT wrap in markdown or code blocks.

Structure:
{{
  "1": {{
    "total_grade": <number>,
    "questions": {{
      "1": {{
        "awarded": <number>,
        "max": <number>,
        "feedback": "brief justification in the student's language",
        "confidence": <number between 0.0 and 1.0>,
        "flag": <true or false>,
        "flag_reason": "reason if flagged, otherwise null"
      }}
    }}
  }}
}}

RULES
1. Every awarded grade MUST be a multiple of 0.25
2. The sum of awarded grades per exercise must NOT exceed the exercise total grading
3. If student answer is null or empty, award 0
4. Keep feedback concise but informative (1-2 sentences max)
5. Do not invent corrections or answers
6. lv questions are graded binary: full marks or 0, no exceptions
7. hv questions use rubric based partial credit
8. Always set flag to true if confidence is below 0.6
9. Grade strings like "4pts" or "1pt" must have their numeric value extracted before processing
10. If "type" is null or missing, treat the question as "hv" and apply partial credit grading
11. For math and coding questions, methodology and logic are weighted more than the final answer
12. Do not penalize OCR artifacts in coding or math answers, infer intent from context
13. For ACTUAL ESSAYS, writing quality (grammar, punctuation, vocabulary) is worth 40% of the grade
14. For non-essay explanations, focus on content accuracy and do not heavily penalize grammar
15. Distinguish between OCR corruption and actual spelling/grammar errors in essays
16. Return ONLY JSON
17. LaTeX notation in corrections and plain text/symbols in student answers are considered equivalent if mathematically identical

---

GRADING MODEL:
{grading_model_str}

Now grade the student's submission:"""

    return prompt