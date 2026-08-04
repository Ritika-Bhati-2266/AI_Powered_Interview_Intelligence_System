"""
Aptitude Question Bank — Company-Specific Pattern Subsets
Each company subset is curated to match the known real interview patterns
that candidates widely report on Glassdoor, GeeksforGeeks, and LeetCode forums.

All questions are ORIGINAL text written in each company's known style/format.
No verbatim reproduction of copyrighted question banks.

Pattern sources:
- TCS NQT: known for number series, time-speed-distance, percentages, profit-loss,
  SI/CI, coding-decoding, blood relations, seating arrangements, syllogisms,
  sentence correction, para jumbles, synonyms/antonyms
- Infosys (InfyTQ): known for pseudocode-reading, logical reasoning emphasis
- Wipro (NLTH): known for heavy verbal/English weighting, written communication
- HCL: known for simpler/easier quant and logical than other Indian IT
"""

import random

# ── HELPER: Question factory ─────────────────────────────────────────────────

def _q(question, options, correct, explanation, category, company_tag="general", is_advanced=False):
    """Build a standardized question dict with company tag."""
    return {
        "question": question,
        "options": options,
        "correct": correct,
        "explanation": explanation,
        "category": category,
        "company": company_tag,
        "is_advanced": is_advanced,
    }


# ═════════════════════════════════════════════════════════════════════════════
# TCS NQT PATTERN SUBSET
# Real TCS NQT is known for heavy emphasis on:
#   QUANT: Time-Speed-Distance, Percentages, Profit & Loss, SI/CI, Number Series
#   LOGIC: Coding-Decoding, Blood Relations, Seating Arrangement, Syllogisms
#   VERBAL: Sentence Correction, Para Jumbles, Email Scenario, Synonyms/Antonyms
# ═════════════════════════════════════════════════════════════════════════════

TCS_QUESTIONS = {
    "quantitative": [
        _q(
            "A train 150 m long passes a pole in 15 seconds. What is the speed of the train in km/h?",
            ["30 km/h", "36 km/h", "45 km/h", "54 km/h"],
            1,
            "Speed = Distance/Time = 150/15 = 10 m/s = 10 × 18/5 = 36 km/h",
            "quantitative", "tcs"
        ),
        _q(
            "If the price of sugar increases by 25%, by what percentage should a household reduce consumption so that expenditure remains unchanged?",
            ["20%", "25%", "16.67%", "33.33%"],
            0,
            "Let original price = 100, new price = 125. To keep expenditure same, new consumption = (100/125) × 100 = 80%. Reduction = 20%",
            "quantitative", "tcs"
        ),
        _q(
            "A shopkeeper sells an item at Rs. 720 after giving a 10% discount on the marked price. If he still makes a 20% profit on cost, what is the cost price?",
            ["Rs. 500", "Rs. 540", "Rs. 600", "Rs. 480"],
            1,
            "MP × 0.9 = 720 → MP = 800. SP = 720, profit = 20% → CP = 720/1.2 = Rs. 540",
            "quantitative", "tcs"
        ),
        _q(
            "Find the next number in the series: 7, 13, 25, 49, ?",
            ["97", "99", "95", "101"],
            0,
            "Pattern: ×2 - 1, ×2 - 1, ×2 - 1... 49 × 2 - 1 = 97. Or: +6, +12, +24, +48 → 49+48=97",
            "quantitative", "tcs"
        ),
        _q(
            "What is the compound interest on Rs. 8000 at 15% per annum for 2 years, compounded annually?",
            ["Rs. 2400", "Rs. 2520", "Rs. 2580", "Rs. 2600"],
            2,
            "A = 8000(1+0.15)² = 8000 × 1.3225 = 10580. CI = 10580 - 8000 = Rs. 2580",
            "quantitative", "tcs"
        ),
        _q(
            "A person covers a certain distance at 60 km/h in 4 hours. In how many hours will he cover the same distance at 80 km/h?",
            ["2.5 hours", "3 hours", "3.5 hours", "4 hours"],
            1,
            "Distance = 60 × 4 = 240 km. Time = 240/80 = 3 hours",
            "quantitative", "tcs"
        ),
        _q(
            "The difference between simple interest and compound interest on a sum for 2 years at 10% per annum is Rs. 50. What is the sum?",
            ["Rs. 4000", "Rs. 5000", "Rs. 6000", "Rs. 4500"],
            1,
            "Difference for 2 years = P × (R/100)² = P × 0.01 = 50 → P = Rs. 5000",
            "quantitative", "tcs"
        ),
        _q(
            "Find the missing number: 5, 11, 23, 47, 95, ?",
            ["187", "191", "189", "193"],
            1,
            "×2 + 1 pattern: 5×2+1=11, 11×2+1=23, 23×2+1=47, 47×2+1=95, 95×2+1=191",
            "quantitative", "tcs"
        ),
        _q(
            "If 15 men can build a wall in 12 days, how many days will 20 men take to build the same wall?",
            ["8 days", "9 days", "10 days", "7 days"],
            1,
            "M1D1 = M2D2 → 15 × 12 = 20 × D2 → D2 = 180/20 = 9 days",
            "quantitative", "tcs"
        ),
        _q(
            "A buys an article for Rs. 1200 and sells it to B at a profit of 15%. B sells it to C at a loss of 10%. What does C pay?",
            ["Rs. 1242", "Rs. 1260", "Rs. 1340", "Rs. 1180"],
            0,
            "B's cost = 1200 × 1.15 = 1380. C's cost = 1380 × 0.9 = Rs. 1242",
            "quantitative", "tcs"
        ),
        _q(
            "The average of 8 observations was 42. Later it was found that one observation 28 was misread as 36. What is the correct average?",
            ["40.5", "41", "42.5", "43"],
            1,
            "Diff = 28 - 36 = -8 (overcounted). Correct sum = 42×8 - 8 = 336 - 8 = 328. Correct avg = 328/8 = 41",
            "quantitative", "tcs"
        ),
        _q(
            "Two numbers are in ratio 5:7. If their LCM is 140, what is the sum of the numbers?",
            ["48", "60", "72", "84"],
            0,
            "Numbers = 5k and 7k. LCM = 35k = 140 → k = 4. Numbers are 20 and 28. Sum = 48",
            "quantitative", "tcs"
        ),
        _q(
            "A man can complete a work in 12 days. His son is 60% as efficient. How many days will they take together?",
            ["7 days", "7.5 days", "8 days", "6.5 days"],
            1,
            "Son's efficiency = 0.6 → Son takes 12/0.6 = 20 days. Together: 1/12 + 1/20 = (5+3)/60 = 8/60 = 2/15 → 7.5 days",
            "quantitative", "tcs"
        ),
        _q(
            "If 35% of a number is 140, what is 60% of that number?",
            ["200", "240", "260", "280"],
            1,
            "Number = 140/0.35 = 400. 60% of 400 = 240",
            "quantitative", "tcs"
        ),
        _q(
            "Series: 1, 4, 10, 22, 46, ?",
            ["92", "94", "96", "88"],
            1,
            "Pattern: ×2+2, ×2+2, ×2+2... 46×2+2 = 94",
            "quantitative", "tcs"
        ),
        # TCS NQT Advanced section (optional)
        _q(
            "How many numbers between 200 and 600 are divisible by 3, 5, and 7?",
            ["2", "3", "4", "1"],
            2,
            "LCM of 3, 5, 7 = 105. Multiples of 105 between 200 and 600: 210, 315, 420, 525. That is 4 numbers.",
            "quantitative", "tcs", is_advanced=True
        ),
        _q(
            "The ratio of milk to water in a mixture is 3:2. If 10 litres of water is added, the ratio becomes 1:1. What was the original quantity of milk?",
            ["20 L", "30 L", "40 L", "25 L"],
            1,
            "Original: milk=3k, water=2k. After adding 10L water: 3k/(2k+10) = 1/1 → 3k = 2k+10 → k=10. Milk = 30L",
            "quantitative", "tcs"
        ),
    ],
    "logical_reasoning": [
        _q(
            "In a certain code, 'COUNTRY' is written as 'DPVOUSZ'. How is 'VILLAGE' written?",
            ["WKMBHF", "WJMBBH", "WJMBH", "WJMBHF"],
            3,
            "Each letter is replaced by the next letter in the alphabet (C→D, O→P, U→V...). V→W, I→J, L→M, L→M, A→B, G→H, E→F → WJMBHF",
            "logical_reasoning", "tcs"
        ),
        _q(
            "If 'SELECTION' is coded as 'SFMDUJPO', what is the code for 'POSITION'?",
            ["QQTJTJPO", "QPTJUUJPO", "QPTJUJPO", "PQTJUJPOU"],
            2,
            "Each letter is replaced by the next letter (S→T, E→F, L→M, E→F...). P→Q, O→P, S→T, I→J, T→U, I→J, O→P, N→O → QPTJUJPO",
            "logical_reasoning", "tcs"
        ),
        _q(
            "Pointing to a man, Riya said, 'His brother is the father of my only sister's son.' How is the man related to Riya?",
            ["Brother", "Cousin", "Nephew", "Uncle"],
            3,
            "Riya's only sister's son = Riya's nephew. His father = Riya's sister's husband (Riya's brother-in-law). The man being pointed to is that person's brother, making the man Riya's uncle.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "If 'STONE' is written as 'TUPOF', how is 'BRICK' written?",
            ["CSJDL", "CSJDM", "CQJDL", "DSKEM"],
            0,
            "Each letter is shifted by +1, +2, +1, +2, +1 alternately: S→T(+1), T→U(+1)... Actually let's check: S→T(+1), T→U(+1), O→P(+1), N→O(+1), E→F(+1). That's simply +1 for all. For BRICK: B→C, R→S, I→J, C→D, K→L → CSJDL.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "Six friends P, Q, R, S, T, U sit in a circle facing the centre. P is between Q and U. R is between T and S. Q is to the immediate left of T. Who is opposite U?",
            ["R", "S", "T", "Q"],
            0,
            "In a circle of 6 facing center: P is between Q and U, forming Q-P-U chain. R is between T and S, forming T-R-S chain. Q is to the immediate left of T (so T is clockwise-adjacent to Q). Arranging clockwise: U-P-Q-T-R-S. The person opposite U is R.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "Statement: All cats are mammals. Some mammals are dogs. No dog is a bird. Conclusion I: Some cats are not birds. Conclusion II: Some mammals are not birds.",
            ["Only I follows", "Only II follows", "Both I and II follow", "Neither follows"],
            1,
            "From the statements: Some mammals are dogs + No dog is a bird → Some mammals are not birds (II follows). But we cannot conclude about cats specifically (I doesn't follow because all cats could be a subset of mammals that are not dogs).",
            "logical_reasoning", "tcs"
        ),
        _q(
            "How many 6s are there in the sequence that are immediately followed by an even number? 4 6 7 6 8 6 2 6 9 6 3 6 4 6 6 2",
            ["4", "3", "5", "6"],
            2,
            "Sequence: 4 6 7 6 8 6 2 6 9 6 3 6 4 6 6 2. Checking each 6: (6,7)→odd no, (6,8)→even yes, (6,2)→even yes, (6,9)→odd no, (6,3)→odd no, (6,4)→even yes, (6,6)→even yes, (6,2)→even yes. Total = 5 occurrences.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "Find the next term in the series: AZB, CYD, EXF, GWH, ?",
            ["IVJ", "IUK", "IVK", "JWJ"],
            0,
            "First letter: A→C→E→G (+2 each), next = I. Second letter: Z→Y→X→W (-1 each), next = V. Third letter: B→D→F→H (+2 each), next = J. So = IVJ",
            "logical_reasoning", "tcs"
        ),
        _q(
            "If 4 × 3 = 14, 5 × 4 = 21, then 6 × 5 = ?",
            ["30", "31", "29", "32"],
            0,
            "Pattern: (a × b) + (a − 2) = answer. For 4×3: 12 + 2 = 14. For 5×4: 20 + 1 = 21. For 6×5: 30 + 0 = 30.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "Read the information and answer: A is the mother of B. C is the brother of B. D is the husband of C. E is the sister of D. How is A related to E?",
            ["No relation", "Sister-in-law", "Mother", "Cannot be determined"],
            0,
            "A is mother of B and C. C is married to D. D has sister E. So A is the mother-in-law of D. E is the sister of D, so E is not directly related to A. No relation.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "Seven persons A, B, C, D, E, F, G sit in a row. A sits at one extreme. B sits two places away from A. C sits between B and E. D sits immediately left of C. F is at the other extreme. Who sits in the middle?",
            ["C", "D", "E", "B"],
            1,
            "Seven persons in a row. A at one end (position 1). B at position 3 (two places from A). F at the other end (position 7). D sits immediately left of C. C sits between B and E. Arranging: A, _, B, D, C, E, F. Position 2 must be G. The middle position (4th of 7) is occupied by D.",
            "logical_reasoning", "tcs"
        ),
        _q(
            "If 'NIGHT' is coded as 'OIIHU' (each letter shifted +1), what is 'LIGHT' coded as?",
            ["MJHU", "MKIHU", "MJIHU", "MJJHU"],
            2,
            "Each letter advanced by +1: L→M, I→J, G→H, H→I, T→U → MJIHU",
            "logical_reasoning", "tcs"
        ),
        _q(
            "All books are files. No file is an eraser. Some erasers are pins. Conclusion: Some books are not pins.",
            ["True", "False", "Cannot be determined", "Probably true"],
            2,
            "Books ⊂ Files. Files ∩ Erasers = ∅. Erasers ⊂ Pins? Only 'some erasers are pins', meaning there is overlap between erasers and pins, but we don't know if all erasers are pins or some aren't. Since books are a subset of files, and files have no overlap with erasers, but erasers overlap with pins, we can't conclude anything about books and pins.",
            "logical_reasoning", "tcs"
        ),
    ],
    "verbal": [
        _q(
            "Choose the correctly spelled word:",
            ["Accomodate", "Acommodate", "Accommodate", "Acomodate"],
            2,
            "'Accommodate' has double 'c' and double 'm' — commonly tested in TCS NQT verbal section",
            "verbal", "tcs"
        ),
        _q(
            "Choose the synonym of 'Aberration':",
            ["Deviation", "Perfection", "Standard", "Normalcy"],
            0,
            "Aberration means a departure from what is normal or expected. Deviation is the closest synonym.",
            "verbal", "tcs"
        ),
        _q(
            "Sentences given with a blank: 'The manager asked the team to ______ the project before the deadline.'",
            ["hasten", "expedite", "delay", "prolong"],
            1,
            "Expedite means to make happen faster or sooner — the most appropriate word in this context.",
            "verbal", "tcs"
        ),
        _q(
            "Identify the correct sentence:",
            ["Neither the manager nor his colleagues was present", "Neither the manager nor his colleagues were present", "Neither the manager nor his colleagues is present", "Neither the manager or his colleagues were present"],
            1,
            "When subjects are joined by 'neither...nor', the verb agrees with the subject closest to it. 'Colleagues' (plural) → 'were'",
            "verbal", "tcs"
        ),
        _q(
            "Select the antonym of 'Ephemeral':",
            ["Fleeting", "Transient", "Perpetual", "Momentary"],
            2,
            "Ephemeral means lasting a very short time. Perpetual means lasting forever — the opposite.",
            "verbal", "tcs"
        ),
        _q(
            "Choose the correct synonym of 'Pragmatic':",
            ["Idealistic", "Realistic", "Optimistic", "Pessimistic"],
            1,
            "Pragmatic means dealing with things realistically and practically. Realistic is the closest synonym.",
            "verbal", "tcs"
        ),
        _q(
            "Fill in the blank: 'The CEO's speech was so ______ that everyone felt inspired.'",
            ["eloquent", "ambiguous", "redundant", "monotonous"],
            0,
            "Eloquent means fluent or persuasive in speaking — a speech that inspires people is eloquent.",
            "verbal", "tcs"
        ),
        _q(
            "Choose the word that is OPPOSITE in meaning to 'Benevolent':",
            ["Kind", "Generous", "Malevolent", "Charitable"],
            2,
            "Benevolent means well-meaning and kindly; malevolent means having/showing ill will.",
            "verbal", "tcs"
        ),
        _q(
            "Rearrange the following sentences to form a coherent paragraph:\nP: This is because they help break down organic matter into nutrients.\nQ: Earthworms are often called 'nature's ploughmen'.\nR: These nutrients enrich the soil and promote plant growth.\nS: Farmers consider them beneficial for soil health.",
            ["Q-P-S-R", "Q-S-P-R", "P-Q-R-S", "S-P-Q-R"],
            1,
            "Q introduces the topic (earthworms as nature's ploughmen). S explains farmers' view. P gives the reason. R continues the nutrient cycle. Q-S-P-R is the correct order.",
            "verbal", "tcs"
        ),
        _q(
            "Choose the correctly spelled word:",
            ["Priviledge", "Privilige", "Privilege", "Privelege"],
            2,
            "Privilege — commonly misspelled word in competitive exams. Note: 'i' before 'e' except after 'c' doesn't always apply!",
            "verbal", "tcs"
        ),
        _q(
            "Identify the correctly punctuated sentence:",
            ["Its a beautiful day outside", "Its' a beautiful day outside", "It's a beautiful day outside", "Its a beautiful day outside."],
            2,
            "'It's' is the contraction of 'it is'. The possessive 'its' has no apostrophe.",
            "verbal", "tcs"
        ),
        _q(
            "Compose a professional email declining a job offer. Which opening line is most appropriate?",
            ["Sorry, I don't want the job.", "Thank you for offering me the position of Software Engineer at your company.", "Hey, I'm not taking this job.", "I received your offer letter."],
            1,
            "Professional email openings should express gratitude and mention the specific position — this is the kind of email scenario TCS NQT verbal section tests.",
            "verbal", "tcs"
        ),
        _q(
            "Choose the synonym of 'Ubiquitous':",
            ["Rare", "Everywhere", "Unusual", "Unique"],
            1,
            "Ubiquitous means found everywhere. 'Everywhere' is the closest synonym.",
            "verbal", "tcs"
        ),
        _q(
            "Given below is a sentence with an error. Find the part with the error:\nThe team (A) / have submitted (B) / their reports (C) / on time. (D)",
            ["A", "B", "C", "No error"],
            1,
            "'Team' is a collective noun and in standard English, when considered as a unit, takes singular verb 'has'. So 'have submitted' (B) is the error.",
            "verbal", "tcs"
        ),
        _q(
            "Directions: A company wants to hire candidates with strong communication skills. Which of the following is the MOST important quality to assess?",
            ["Ability to code in multiple languages", "Clarity of expression and logical flow of ideas", "Years of experience", "Number of certifications"],
            1,
            "Communication skills are primarily about clarity of expression and logical flow — this type of scenario-based question appears in TCS NQT verbal.",
            "verbal", "tcs"
        ),
        _q(
            "Select the word that best completes the analogy:\nBooks : Library :: Paintings : ______",
            ["Canvas", "Museum", "Artist", "Frame"],
            1,
            "Books are collected in a library; paintings are collected in a museum/art gallery.",
            "verbal", "tcs"
        ),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# INFOSYS (InfyTQ) PATTERN SUBSET
# Known for: pseudocode-reading, logical reasoning, standard quant,
# emphasis on 'what does this code output' style questions
# ═════════════════════════════════════════════════════════════════════════════

INFOSYS_QUESTIONS = {
    "quantitative": [
        _q(
            "If the sum of three consecutive odd numbers is 63, what is the largest number?",
            ["21", "23", "25", "27"],
            1,
            "Let numbers be n-2, n, n+2. Sum = 3n = 63 → n = 21. Largest = 23",
            "quantitative", "infosys"
        ),
        _q(
            "A boat can travel 20 km upstream in 4 hours and 30 km downstream in 3 hours. What is the speed of the stream?",
            ["2.5 km/h", "3 km/h", "2 km/h", "1.5 km/h"],
            2,
            "Upstream speed = 20/4 = 5 km/h. Downstream speed = 30/3 = 10 km/h. Stream speed = (downstream − upstream)/2 = (10−5)/2 = 2.5 km/h",
            "quantitative", "infosys"
        ),
        _q(
            "12 men can complete a piece of work in 15 days. 10 women can complete the same work in 24 days. In how many days will 8 men and 12 women together complete the work?",
            ["9 days", "10 days", "12 days", "8 days"],
            1,
            "1 man's 1-day work = 1/(12×15) = 1/180. 1 woman's 1-day work = 1/(10×24) = 1/240. 8 men + 12 women per day = 8/180 + 12/240 = 32/720 + 36/720 = 68/720 = 17/180. Total days = 180/17 ≈ 10.6. The closest integer option is 10 days.",
            "quantitative", "infosys"
        ),
        _q(
            "A test has 100 questions. Each correct answer gives +3 marks, each wrong answer gives -1 mark, and unanswered questions give 0. A candidate scored 200 marks. How many questions did they answer correctly if they attempted all?",
            ["70", "75", "80", "85"],
            1,
            "Let correct = c, wrong = 100-c (since all attempted). 3c - (100-c) = 200 → 3c - 100 + c = 200 → 4c = 300 → c = 75",
            "quantitative", "infosys"
        ),
        _q(
            "If log₂x + log₂(x-2) = 3, find x.",
            ["2", "4", "6", "8"],
            1,
            "log₂(x(x-2)) = 3 → x(x-2) = 8 → x²-2x-8=0 → (x-4)(x+2)=0 → x=4 (x>2)",
            "quantitative", "infosys"
        ),
        _q(
            "What is the remainder when 3¹²⁵ is divided by 5?",
            ["1", "2", "3", "4"],
            2,
            "3¹=3, 3²=9≡4, 3³=27≡2, 3⁴=81≡1 (mod 5). Pattern repeats every 4. 125÷4 = 31 rem 1. So 3¹²⁵ ≡ 3¹ ≡ 3 (mod 5)",
            "quantitative", "infosys"
        ),
        _q(
            "If the mean of 10 numbers is 24 and the mean of 6 of them is 20, what is the mean of the remaining 4?",
            ["28", "30", "32", "26"],
            1,
            "Sum of 10 = 240. Sum of 6 = 120. Sum of 4 = 120. Mean of 4 = 30",
            "quantitative", "infosys"
        ),
        _q(
            "A sum of Rs. 5000 becomes Rs. 7200 in 2 years at compound interest. What is the annual rate of interest?",
            ["18%", "20%", "22%", "25%"],
            1,
            "A = P(1+r/100)² → 7200 = 5000(1+r/100)² → (1+r/100)² = 7200/5000 = 1.44 → 1+r/100 = 1.2 → r = 20%",
            "quantitative", "infosys"
        ),
        _q(
            "If a:b = 2:3 and b:c = 5:7, what is a:c?",
            ["10:21", "10:7", "2:7", "5:7"],
            0,
            "a/c = (a/b) × (b/c) = 2/3 × 5/7 = 10/21 → a:c = 10:21",
            "quantitative", "infosys"
        ),
        _q(
            "The probability of getting a sum of 7 when two dice are thrown together is:",
            ["1/9", "1/6", "5/36", "1/12"],
            1,
            "Favorable outcomes: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1) = 6. Total outcomes = 36. Probability = 6/36 = 1/6",
            "quantitative", "infosys"
        ),
    ],
    "logical_reasoning": [
        # Infosys is known for pseudocode-reading questions
        _q(
            "What will be the output of the following pseudocode?\nFOR i = 1 TO 4\n    FOR j = 1 TO i\n        PRINT \"*\"\n    NEXT j\n    PRINT newline\nNEXT i",
            ["4 stars in a row", "A right triangle pattern of stars", "A square of 16 stars", "4 rows of 4 stars each"],
            1,
            "Outer loop runs 4 times. Inner loop runs 'i' times (1,2,3,4). This creates a right-angled triangle pattern with 1, 2, 3, and 4 stars in successive rows.",
            "logical_reasoning", "infosys"
        ),
        _q(
            "What is the output of this pseudocode?\nA = 10\nB = 20\nA = A + B\nB = A - B\nA = A - B\nPRINT A, B",
            ["10, 20", "20, 10", "10, 10", "20, 20"],
            1,
            "This is the classic swap algorithm without a temp variable. Initially A=10, B=20. A = 10+20=30. B = 30-20=10. A = 30-10=20. Result: A=20, B=10.",
            "logical_reasoning", "infosys"
        ),
        _q(
            "What does this pseudocode output?\nFUNCTION check(n)\n    IF n <= 1 THEN RETURN n\n    RETURN check(n-1) + check(n-2)\nENDFUNC\nPRINT check(6)",
            ["5", "8", "13", "6"],
            1,
            "This is the Fibonacci sequence. check(0)=0, check(1)=1, check(2)=1, check(3)=2, check(4)=3, check(5)=5, check(6)=8.",
            "logical_reasoning", "infosys"
        ),
        _q(
            "What will be the value of X after execution?\nX = 1\nFOR K = 1 TO 5 STEP 2\n    X = X * K\nNEXT K",
            ["15", "45", "105", "25"],
            0,
            "K takes values 1, 3, 5. X = 1×1×3×5 = 15",
            "logical_reasoning", "infosys"
        ),
        _q(
            "Given pseudocode:\na = [5, 2, 8, 1, 9]\nFOR i = 0 TO 3\n    FOR j = 0 TO 3-i\n        IF a[j] > a[j+1] THEN\n            SWAP a[j], a[j+1]\n        ENDIF\n    NEXT j\nNEXT i\nPRINT a[2]",
            ["2", "5", "8", "1"],
            1,
            "Bubble sort on [5,2,8,1,9] produces [1,2,5,8,9]. After sorting, a[2] = 5 (0-indexed).",
            "logical_reasoning", "infosys"
        ),
        _q(
            "What does this code fragment compute?\nresult = 1\nFOR i = 1 TO n\n    result = result * i\nNEXT i",
            ["n²", "n!", "2ⁿ", "n+n"],
            1,
            "This computes factorial of n (n! = 1×2×3×...×n)",
            "logical_reasoning", "infosys"
        ),
        _q(
            "What is the output?\nx = 5\ny = 0\nWHILE x > 0\n    y = y + x\n    x = x - 1\nENDWHILE\nPRINT y",
            ["10", "15", "20", "5"],
            1,
            "Loop sums 5+4+3+2+1 = 15",
            "logical_reasoning", "infosys"
        ),
        _q(
            "A series: 2, 3, 5, 9, 17, ? What is the next term?",
            ["31", "33", "35", "29"],
            1,
            "Pattern: ×2-1, ×2-1? 2×2-1=3, 3×2-1=5, 5×2-1=9, 9×2-1=17, 17×2-1=33. Or: +1,+2,+4,+8,+16 → 17+16=33",
            "logical_reasoning", "infosys"
        ),
        _q(
            "Identify the missing term: ACE, GIK, MOQ, ?",
            ["RTV", "SUV", "RUV", "STV"],
            0,
            "Pattern: A→C→E (+2,+2). A=1, C=3, E=5. Next group: G=7, I=9, K=11 (+2,+2). M=13, O=15, Q=17 (+2,+2). Next: R=18, T=20, V=22 → RTV",
            "logical_reasoning", "infosys"
        ),
        _q(
            "If a = 10, b = 5, what is the value of a - b / 2 + 3?",
            ["10", "10.5", "7.5", "8"],
            1,
            "Following operator precedence: division before subtraction. b/2 = 2.5, then a - 2.5 + 3 = 10 - 2.5 + 3 = 10.5",
            "logical_reasoning", "infosys"
        ),
    ],
    "verbal": [
        _q(
            "Choose the correct synonym of 'Perspicacious':",
            ["Dull", "Perceptive", "Careless", "Naive"],
            1,
            "Perspicacious means having a ready insight into things; perceptive.",
            "verbal", "infosys"
        ),
        _q(
            "Fill in the blank: 'His ______ attitude towards work earned him the respect of his colleagues.'",
            ["nonchalant", "diligent", "apathetic", "languid"],
            1,
            "Diligent means hard-working and careful — a positive attribute that earns respect.",
            "verbal", "infosys"
        ),
        _q(
            "Identify the error in the sentence: 'The collection of rare stamps are kept in a vault.'",
            ["collection", "rare", "are kept", "vault"],
            2,
            "The subject is 'collection' (singular), so the verb should be 'is kept', not 'are kept'.",
            "verbal", "infosys"
        ),
        _q(
            "Select the antonym of 'Ostentatious':",
            ["Showy", "Lavish", "Modest", "Grandiose"],
            2,
            "Ostentatious means designed to impress or attract notice; modest is the opposite.",
            "verbal", "infosys"
        ),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# WIPRO (NLTH) PATTERN SUBSET
# Known for: HEAVY verbal/English weighting, written communication tests,
# standard logical reasoning, less focus on advanced quant
# ═════════════════════════════════════════════════════════════════════════════

WIPRO_QUESTIONS = {
    "quantitative": [
        _q(
            "If a number is increased by 15% and then decreased by 15%, what is the net percentage change?",
            ["2.25% increase", "2.25% decrease", "No change", "1.5% decrease"],
            1,
            "Let number = 100. After increase = 115. After decrease = 115 × 0.85 = 97.75. Net change = -2.25%",
            "quantitative", "wipro"
        ),
        _q(
            "The difference between a two-digit number and the number formed by reversing its digits is 36. If the ratio of the digits is 2:1, what is the number?",
            ["63", "84", "72", "48"],
            1,
            "Let digits be 2x (tens) and x (units). Number = 20x + x = 21x. Reversed = 10x + 2x = 12x. Difference = 21x − 12x = 9x = 36 → x = 4. Digits: 2x=8, x=4. Number = 84. Reversed = 48. 84 − 48 = 36 ✓. Answer: 84.",
            "quantitative", "wipro"
        ),
        _q(
            "A man spends 70% of his salary. If his salary increases by 20% and his expenditure increases by 10%, what is the percentage change in his savings?",
            ["43.33% increase", "50% increase", "33.33% increase", "40% increase"],
            0,
            "Let salary = 100. Exp = 70, Savings = 30. New salary = 120. New exp = 70×1.1 = 77. New savings = 43. Change = (43-30)/30 × 100 = 43.33% increase",
            "quantitative", "wipro"
        ),
        _q(
            "Simple interest on a sum for 3 years at 8% per annum is Rs. 600. What is the compound interest on the same sum at the same rate for 2 years?",
            ["Rs. 400", "Rs. 416", "Rs. 424", "Rs. 440"],
            1,
            "SI = PRT/100 → 600 = P×8×3/100 → P = 60000/24 = 2500. CI for 2 years: 2500(1.08²-1) = 2500(1.1664-1) = 2500×0.1664 = Rs. 416",
            "quantitative", "wipro"
        ),
    ],
    "logical_reasoning": [
        _q(
            "Find the missing number: 3, 7, 13, 21, 31, ?",
            ["41", "43", "39", "45"],
            1,
            "Differences: +4, +6, +8, +10, +12 → 31+12 = 43",
            "logical_reasoning", "wipro"
        ),
        _q(
            "If 'GREEN' is coded as 'HSFFO' (each letter advanced by +1), what is 'BLACK' coded as?",
            ["CMBDL", "CMBZL", "CNBEL", "CMCDL"],
            0,
            "Each letter is replaced by the next letter: B→C, L→M, A→B, C→D, K→L → CMBDL",
            "logical_reasoning", "wipro"
        ),
        _q(
            "Statement: Some pencils are pens. All pens are erasers. Conclusion: Some pencils are erasers. Does the conclusion follow?",
            ["Yes", "No", "Can't say", "Depends"],
            0,
            "Some pencils are pens (subset). All pens are erasers (superset). Therefore, some pencils (which are pens) must be erasers. Conclusion follows.",
            "logical_reasoning", "wipro"
        ),
        _q(
            "A man walks 5 km east, turns right and walks 3 km, turns right again and walks 5 km. How far is he from his starting point?",
            ["3 km", "5 km", "8 km", "2 km"],
            0,
            "He walks 5 km east, then 3 km south, then 5 km west. He ends up 3 km from start (directly south).",
            "logical_reasoning", "wipro"
        ),
        _q(
            "Find the odd one out: 12, 24, 36, 45, 60",
            ["12", "24", "36", "45"],
            3,
            "All are multiples of 12 except 45.",
            "logical_reasoning", "wipro"
        ),
        _q(
            "If today is Monday, what day will it be after 100 days?",
            ["Wednesday", "Tuesday", "Thursday", "Friday"],
            0,
            "100 ÷ 7 = 14 weeks + 2 days. Monday + 2 = Wednesday",
            "logical_reasoning", "wipro"
        ),
    ],
    "verbal": [
        # Wipro has proportionally more verbal questions
        _q(
            "Choose the correct synonym of 'Gregarious':",
            ["Shy", "Sociable", "Aggressive", "Reserved"],
            1,
            "Gregarious means fond of company; sociable.",
            "verbal", "wipro"
        ),
        _q(
            "Select the word that is opposite in meaning to 'Lethargic':",
            ["Sluggish", "Energetic", "Tired", "Lazy"],
            1,
            "Lethargic means lacking energy; energetic is the opposite.",
            "verbal", "wipro"
        ),
        _q(
            "Fill in the blank: 'The professor's ______ explanation made the complex topic easy to understand.'",
            ["ambiguous", "lucid", "vague", "convoluted"],
            1,
            "Lucid means expressed clearly and easy to understand.",
            "verbal", "wipro"
        ),
        _q(
            "Identify the correctly spelled word:",
            ["Occurence", "Occurrence", "Occurance", "Ocurrence"],
            1,
            "Occurrence has double 'c' and double 'r'.",
            "verbal", "wipro"
        ),
        _q(
            "Choose the correct antonym of 'Ameliorate':",
            ["Improve", "Worsen", "Enhance", "Upgrade"],
            1,
            "Ameliorate means to make better; worsen is the opposite.",
            "verbal", "wipro"
        ),
        _q(
            "Find the correctly punctuated option:\n'Well I never expected to see you here'",
            ["Well, I never expected to see you here.", "Well I never expected, to see you here.", "Well, I never expected, to see you here.", "Well I never, expected to see you here."],
            0,
            "The interjection 'Well' should be followed by a comma.",
            "verbal", "wipro"
        ),
        _q(
            "Which sentence uses 'affect' correctly?",
            ["The weather will effect our plans.", "The medicine had no affect on the patient.", "The new policy will affect all employees.", "His affect was calm and composed."],
            2,
            "'Affect' as a verb means to influence or have an impact on. 'Effect' is most commonly used as a noun meaning result.",
            "verbal", "wipro"
        ),
        _q(
            "Rearrange the following sentences to form a meaningful paragraph:\nP: This diversity makes the country culturally rich.\nQ: India is a land of diverse cultures and traditions.\nR: Each state has its own language, cuisine, and festivals.\nS: From north to south, the variety is remarkable.",
            ["Q-R-S-P", "Q-P-R-S", "R-Q-S-P", "S-R-Q-P"],
            0,
            "Q introduces India's diversity. R elaborates on state-wise differences. S emphasizes the geographical range. P concludes with cultural richness. Q-R-S-P.",
            "verbal", "wipro"
        ),
        _q(
            "What is the correct verb form? 'Neither the principal nor the teachers ______ in favor of the new policy.'",
            ["is", "was", "are", "has been"],
            2,
            "With 'neither...nor', the verb agrees with the subject closest to it — 'teachers' (plural) → 'are'",
            "verbal", "wipro"
        ),
        _q(
            "Select the word most similar in meaning to 'Tenacious':",
            ["Weak", "Persistent", "Yielding", "Timid"],
            1,
            "Tenacious means holding firmly; persistent.",
            "verbal", "wipro"
        ),
        _q(
            "Identify the error in the following sentence:\n'Each of the students have submitted their assignments.'",
            ["Each", "students", "have submitted", "their"],
            2,
            "'Each' is singular, so the verb should be 'has submitted', not 'have submitted'.",
            "verbal", "wipro"
        ),
        _q(
            "Choose the word that best completes the sentence:\n'The detective's ______ mind quickly solved the complex case.'",
            ["inquisitive", "analytical", "creative", "emotional"],
            1,
            "An analytical mind is well-suited for solving complex cases through logical reasoning.",
            "verbal", "wipro"
        ),
        _q(
            "Select the correct meaning of the idiom 'To burn the midnight oil':",
            ["To stay up late working or studying", "To start a fire", "To waste resources", "To work efficiently"],
            0,
            "'Burn the midnight oil' means to work late into the night.",
            "verbal", "wipro"
        ),
        _q(
            "Fill in the blank with the appropriate preposition:\n'The committee agreed ______ the proposed changes.'",
            ["for", "to", "on", "with"],
            2,
            "'Agree on' is used when reaching a decision about something.",
            "verbal", "wipro"
        ),
        _q(
            "Write one sentence describing your greatest strength in a professional setting.\n\n(This is a written communication test question — typical Wipro NLTH style)",
            ["A clear, concise sentence about a professional strength with a specific example", "A vague general statement", "A list of multiple strengths without focus", "A paragraph without structure"],
            0,
            "Wipro NLTH written tests evaluate your ability to communicate clearly and concisely — a focused sentence with a concrete example is ideal.",
            "verbal", "wipro"
        ),
        _q(
            "Choose the correctly spelled word:",
            ["Neccessary", "Necesary", "Necessary", "Necessarry"],
            2,
            "Necessary has one 'c' and two 's's.",
            "verbal", "wipro"
        ),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# HCL PATTERN SUBSET
# Known for: easier/simpler quant and logical than other Indian IT,
# less verbal-heavy than Wipro, straightforward questions
# ═════════════════════════════════════════════════════════════════════════════

HCL_QUESTIONS = {
    "quantitative": [
        _q(
            "What is 12% of 250?",
            ["30", "35", "40", "25"],
            0,
            "12% of 250 = (12/100) × 250 = 30",
            "quantitative", "hcl"
        ),
        _q(
            "Find 15% of Rs. 340.",
            ["Rs. 51", "Rs. 48", "Rs. 55", "Rs. 45"],
            0,
            "15% of 340 = 0.15 × 340 = Rs. 51",
            "quantitative", "hcl"
        ),
        _q(
            "A train covers 120 km in 2 hours. What is its speed?",
            ["50 km/h", "60 km/h", "70 km/h", "55 km/h"],
            1,
            "Speed = 120/2 = 60 km/h",
            "quantitative", "hcl"
        ),
        _q(
            "What is the area of a rectangle with length 12 cm and width 8 cm?",
            ["96 sq cm", "86 sq cm", "80 sq cm", "100 sq cm"],
            0,
            "Area = 12 × 8 = 96 sq cm",
            "quantitative", "hcl"
        ),
        _q(
            "What is 25% of 200 plus 10% of 150?",
            ["65", "70", "75", "80"],
            0,
            "25% of 200 = 50, 10% of 150 = 15. Sum = 65",
            "quantitative", "hcl"
        ),
        _q(
            "If the cost of 15 pens is Rs. 225, what is the cost of 8 pens?",
            ["Rs. 100", "Rs. 120", "Rs. 140", "Rs. 110"],
            1,
            "Cost per pen = 225/15 = 15. Cost of 8 = 8 × 15 = Rs. 120",
            "quantitative", "hcl"
        ),
        _q(
            "The average of 5 numbers is 18. If one number is removed, the average becomes 16. What is the removed number?",
            ["24", "26", "22", "20"],
            1,
            "Sum of 5 = 90. Sum of 4 (after removing) = 64. Removed number = 90 - 64 = 26",
            "quantitative", "hcl"
        ),
        _q(
            "If 4 chairs cost Rs. 2400, what will be the cost of 10 chairs?",
            ["Rs. 4800", "Rs. 6000", "Rs. 5000", "Rs. 5500"],
            1,
            "Cost per chair = 2400/4 = 600. Cost of 10 = 10 × 600 = Rs. 6000",
            "quantitative", "hcl"
        ),
        _q(
            "Find the simple interest on Rs. 1500 at 6% per annum for 2 years.",
            ["Rs. 160", "Rs. 170", "Rs. 180", "Rs. 190"],
            2,
            "SI = (1500 × 6 × 2)/100 = Rs. 180",
            "quantitative", "hcl"
        ),
        _q(
            "What is the perimeter of a square with side 7 cm?",
            ["28 cm", "24 cm", "32 cm", "30 cm"],
            0,
            "Perimeter = 4 × 7 = 28 cm",
            "quantitative", "hcl"
        ),
        _q(
            "If a+b = 20 and a-b = 4, what is the value of a?",
            ["10", "12", "14", "8"],
            1,
            "Adding: 2a = 24 → a = 12",
            "quantitative", "hcl"
        ),
        _q(
            "What is the value of 2³ + 3²?",
            ["17", "15", "13", "11"],
            0,
            "2³=8, 3²=9. Sum=17",
            "quantitative", "hcl"
        ),
    ],
    "logical_reasoning": [
        _q(
            "Find the next number: 5, 10, 15, 20, ?",
            ["22", "25", "30", "18"],
            1,
            "Difference of 5 → 20+5=25",
            "logical_reasoning", "hcl"
        ),
        _q(
            "If 'CAT' is coded as 'DBU', how is 'DOG' coded?",
            ["EPH", "FPH", "EQI", "DPE"],
            0,
            "Each letter is replaced by the next letter in the alphabet. D→E, O→P, G→H → EPH",
            "logical_reasoning", "hcl"
        ),
        _q(
            "Find the missing number: 2, 4, 8, 16, ?",
            ["24", "30", "32", "36"],
            2,
            "Multiply by 2 each time → 16×2=32",
            "logical_reasoning", "hcl"
        ),
        _q(
            "Statement: All chairs are furniture. Some furniture is wooden. Conclusion: Some chairs are wooden.",
            ["True", "False", "Cannot be determined", "Probably true"],
            2,
            "All chairs are furniture but not all furniture is necessarily chairs. The wooden furniture could be non-chair items.",
            "logical_reasoning", "hcl"
        ),
        _q(
            "If 'RAT' is coded as '41' (R=18, A=1, T=20 → 18+1+20=39, then 39+2=41), what is 'DOG'?",
            ["30", "28", "26", "32"],
            1,
            "R=18, A=1, T=20. Sum = 39. Code given = 41 (sum + 2). For DOG: D=4, O=15, G=7. Sum = 26 + 2 = 28.",
            "logical_reasoning", "hcl"
        ),
        _q(
            "A is taller than B. C is taller than A. D is shorter than B. Who is the shortest?",
            ["A", "B", "C", "D"],
            3,
            "Order: C > A > B > D → D is shortest.",
            "logical_reasoning", "hcl"
        ),
        _q(
            "Complete the series: 1, 4, 9, 16, 25, ?",
            ["30", "36", "35", "40"],
            1,
            "Squares of 1,2,3,4,5 → next is 6² = 36",
            "logical_reasoning", "hcl"
        ),
        _q(
            "If a man is standing in a queue and he is 5th from the front and 8th from the back, how many people are in the queue?",
            ["12", "13", "14", "11"],
            0,
            "Total = 5 + 8 - 1 = 12",
            "logical_reasoning", "hcl"
        ),
    ],
    "verbal": [
        _q(
            "Choose the correct antonym of 'Expand':",
            ["Grow", "Shrink", "Increase", "Spread"],
            1,
            "Expand means to increase in size; shrink is the opposite.",
            "verbal", "hcl"
        ),
        _q(
            "Identify the correctly spelled word:",
            ["Recieve", "Receive", "Receeve", "Recive"],
            1,
            "Receive — 'i before e except after c' rule applies here.",
            "verbal", "hcl"
        ),
        _q(
            "Fill in the blank: 'She is ______ to attend the meeting tomorrow.'",
            ["going", "go", "gone", "went"],
            0,
            "'Is going to' expresses a future plan.",
            "verbal", "hcl"
        ),
        _q(
            "Choose the synonym of 'Happy':",
            ["Sad", "Joyful", "Angry", "Tired"],
            1,
            "Happy and joyful are synonyms.",
            "verbal", "hcl"
        ),
        _q(
            "Select the correctly punctuated sentence:",
            ["Where are you going", "Where are you going?", "Where are you going.", "Where are you going!"],
            1,
            "A question requires a question mark at the end.",
            "verbal", "hcl"
        ),
        _q(
            "Which of the following is a complete sentence?",
            ["Running fast", "The dog runs fast", "Under the table", "When she arrives"],
            1,
            "'The dog runs fast' has a subject (dog) and verb (runs) and expresses a complete thought.",
            "verbal", "hcl"
        ),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# GENERAL / FALLBACK SUBSET (original merged questions)
# Used when company doesn't have a specific pattern or for fallback
# ═════════════════════════════════════════════════════════════════════════════

GENERAL_QUESTIONS = {
    "quantitative": [
        _q("If a train travels 360 km in 4 hours, what is its average speed?",
           ["80 km/h", "90 km/h", "100 km/h", "85 km/h"], 1,
           "Speed = Distance / Time = 360 / 4 = 90 km/h", "quantitative", "general"),
        _q("A shopkeeper bought an item for Rs. 500 and sold it for Rs. 625. What is his profit percentage?",
           ["20%", "25%", "30%", "15%"], 1,
           "Profit = 125. Profit% = (125/500) × 100 = 25%", "quantitative", "general"),
        _q("What is 30% of 450?",
           ["125", "135", "145", "150"], 1,
           "30% of 450 = 135", "quantitative", "general"),
        _q("In a class, the average marks of 30 students is 70. If the teacher adds 5 more marks to each student's score, what is the new average?",
           ["70", "75", "80", "65"], 1,
           "Adding 5 to each student increases the average by 5. New average = 75", "quantitative", "general"),
        _q("Find the simple interest on Rs. 2000 at 8% per annum for 3 years.",
           ["Rs. 420", "Rs. 480", "Rs. 520", "Rs. 400"], 1,
           "SI = (2000 × 8 × 3)/100 = Rs. 480", "quantitative", "general"),
        _q("If 12 workers can build a wall in 15 days, how many workers are needed to build the same wall in 10 days?",
           ["15", "18", "20", "22"], 1,
           "M1 × D1 = M2 × D2 → 12×15 = M2×10 → M2 = 18", "quantitative", "general"),
        _q("Find the next number in the series: 3, 9, 27, 81, ?",
           ["162", "243", "324", "189"], 1,
           "Each term multiplied by 3: 81×3=243", "quantitative", "general"),
        _q("A pipe can fill a tank in 8 hours. Another pipe can fill it in 12 hours. How long will both take together?",
           ["4.8 hours", "5.2 hours", "6 hours", "4 hours"], 0,
           "Combined rate = 1/8 + 1/12 = 5/24. Time = 24/5 = 4.8 hours", "quantitative", "general"),
        _q("In a mixture of 60 litres, the ratio of milk to water is 2:1. How much water must be added to make the ratio 1:1?",
           ["15 litres", "20 litres", "25 litres", "30 litres"], 1,
           "Milk=40L, Water=20L. To get 1:1, water=40L. Additional=20L", "quantitative", "general"),
    ],
    "logical_reasoning": [
        _q("Find the next number in the series: 2, 6, 12, 20, 30, ?",
           ["40", "42", "44", "36"], 1,
           "Differences: 4,6,8,10,12 → next is 42", "logical_reasoning", "general"),
        _q("In a certain code, 'APPLE' is written as 'BQQMF'. How is 'MANGO' written?",
           ["NBOHP", "NBPOH", "NCOHP", "MBNGP"], 0,
           "Each letter replaced by next letter: M→N, A→B, N→O, G→H, O→P → NBOHP", "logical_reasoning", "general"),
        _q("A is the father of B. C is the sister of B. D is the mother of C. How is D related to A?",
           ["Sister", "Wife", "Mother", "Daughter"], 1,
           "D is mother of A's children → D is A's wife", "logical_reasoning", "general"),
        _q("Complete the analogy: Book : Page :: Tree : ?",
           ["Root", "Branch", "Leaf", "Forest"], 2,
           "A book is made of pages; a tree is made of leaves", "logical_reasoning", "general"),
        _q("If 'PAPER' is written as 'QBSFS', how is 'PENCIL' written?",
           ["QFODJM", "QFOEJM", "QENCHM", "QFOEKN"], 0,
           "Each letter replaced by next: P→Q, E→F, N→O, C→D, I→J, L→M", "logical_reasoning", "general"),
        _q("Find the odd one out: 24, 36, 48, 57, 72",
           ["24", "36", "48", "57"], 3,
           "All are multiples of 12 except 57", "logical_reasoning", "general"),
    ],
    "verbal": [
        _q("Choose the synonym of 'Ephemeral':",
           ["Permanent", "Short-lived", "Eternal", "Strong"], 1,
           "Ephemeral means lasting a very short time", "verbal", "general"),
        _q("Choose the antonym of 'Abundant':",
           ["Plentiful", "Scarce", "Plenty", "Ample"], 1,
           "Abundant means plentiful; scarce is opposite", "verbal", "general"),
        _q("Choose the correct sentence:",
           ["He don't like coffee", "He doesn't likes coffee", "He doesn't like coffee", "He do not likes coffee"], 2,
           "Third person singular requires 'doesn't' + base verb", "verbal", "general"),
        _q("Select the correct meaning of the idiom 'Break the ice':",
           ["To break something frozen", "To initiate conversation", "To destroy something", "To cool down"], 1,
           "Break the ice means to start a conversation or reduce tension", "verbal", "general"),
        _q("Choose the synonym of 'Ubiquitous':",
           ["Rare", "Everywhere", "Unusual", "Unique"], 1,
           "Ubiquitous means present everywhere", "verbal", "general"),
        _q("Complete the sentence: 'Neither the teacher nor the students ______ satisfied.'",
           ["was", "were", "is", "has been"], 1,
           "Verb agrees with closest subject 'students' (plural) → 'were'", "verbal", "general"),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# COMPANY MASTER CONFIG
# Maps company names to their question subsets and distribution rules
# ═════════════════════════════════════════════════════════════════════════════

# Each company config specifies:
#   - subset: which question set to use
#   - distribution: (quant_pct, logical_pct, verbal_pct) — proportion ratios
#   - label: display label for the "Why This Question" context
COMPANY_APTITUDE_CONFIG = {
    "tcs": {
        "subset": TCS_QUESTIONS,
        "distribution": (0.35, 0.35, 0.30),  # Balanced TCS NQT emphasis
        "label": "TCS NQT Pattern",
        "subtopics": {
            "quantitative": "Time-Speed-Distance, Percentages, Profit-Loss, SI/CI, Number Series",
            "logical_reasoning": "Coding-Decoding, Blood Relations, Seating Arrangement, Syllogisms",
            "verbal": "Sentence Correction, Para Jumbles, Synonyms/Antonyms, Email Scenarios",
        },
    },
    "infosys": {
        "subset": INFOSYS_QUESTIONS,
        "distribution": (0.30, 0.40, 0.30),  # Higher logical reasoning weight
        "label": "Infosys InfyTQ Pattern",
        "subtopics": {
            "quantitative": "Standard Quant, Percentages, Averages",
            "logical_reasoning": "Pseudocode Analysis, Number Series, Blood Relations",
            "verbal": "Synonyms/Antonyms, Sentence Correction, Grammar",
        },
    },
    "wipro": {
        "subset": WIPRO_QUESTIONS,
        "distribution": (0.20, 0.30, 0.50),  # Heavy verbal weighting — Wipro known for this
        "label": "Wipro NLTH Pattern",
        "subtopics": {
            "quantitative": "Percentages, Profit-Loss, SI/CI Basics",
            "logical_reasoning": "Coding-Decoding, Direction Sense, Syllogisms",
            "verbal": "Written Communication, Synonyms/Antonyms, Grammar, Para Jumbles, Idioms",
        },
    },
    "hcl": {
        "subset": HCL_QUESTIONS,
        "distribution": (0.40, 0.35, 0.25),  # More straightforward quant, less verbal
        "label": "HCL Pattern",
        "subtopics": {
            "quantitative": "Basic Arithmetic, Percentages, Averages, Geometry Basics",
            "logical_reasoning": "Simple Series, Coding-Decoding, Blood Relations",
            "verbal": "Basic Grammar, Spelling, Vocabulary",
        },
    },
}

# Companies whose aptitude rounds use an Indian IT pattern (TCS/Infosys/Wipro/HCL)
APTITUDE_COMPANIES = {"tcs", "infosys", "wipro", "hcl"}


def get_aptitude_set(num_quant: int = 4, num_logical: int = 4, num_verbal: int = 2,
                    company: str = "general") -> list:
    """
    Randomly select aptitude questions matching a company's real interview pattern.

    Args:
        num_quant: Target number of quantitative questions
        num_logical: Target number of logical reasoning questions
        num_verbal: Target number of verbal ability questions
        company: Company name (case-insensitive). Supported:
                 'tcs', 'infosys', 'wipro', 'hcl', or anything else for general/mixed

    Returns:
        Shuffled list of question dicts with shuffled option order.
        Each dict includes: question, options, correct, explanation, category,
        company, is_advanced, company_pattern_label
    """
    company_lower = company.lower().strip()

    # Get the company config and subset
    if company_lower in COMPANY_APTITUDE_CONFIG:
        config = COMPANY_APTITUDE_CONFIG[company_lower]
        subset = config["subset"]
        # Use company-specific distribution ratios
        dist = config["distribution"]
        total = num_quant + num_logical + num_verbal
        num_quant = max(1, round(total * dist[0]))
        num_logical = max(1, round(total * dist[1]))
        num_verbal = max(1, total - num_quant - num_logical)
        company_label = config["label"]
    else:
        # Fallback to general/mixed bank
        subset = GENERAL_QUESTIONS
        company_label = "General"
        # Use default distribution

    def _shuffle_options(q: dict) -> dict:
        """Shuffle options while tracking the correct answer index."""
        options = q["options"]
        correct_original = q["correct"]
        correct_text = options[correct_original]

        paired = list(enumerate(options))
        random.shuffle(paired)

        new_options = [p[1] for p in paired]
        new_correct = next(i for i, p in enumerate(paired) if p[1] == correct_text)

        return {
            "question": q["question"],
            "options": new_options,
            "correct": new_correct,
            "explanation": q["explanation"],
            "category": q.get("category", ""),
            "company": q.get("company", company_lower),
            "is_advanced": q.get("is_advanced", False),
            "company_pattern_label": company_label,
        }

    def _sample_from_subset(subset_dict: dict, category: str, count: int) -> list:
        """Sample questions from a specific category in a subset, falling back to general."""
        # Get company-specific questions for this category
        cat_questions = subset_dict.get(category, [])

        # Also pull from general subset for variety
        general_cat = GENERAL_QUESTIONS.get(category, [])

        # Mix: prioritize company-specific but supplement with general
        combined = []

        # Take all company-specific questions (they define the authentic pattern)
        tagged = [{**q, "company_pattern_label": company_label} for q in cat_questions]

        # Supplement with general questions tagged as fallback
        general_tagged = [{**q, "company_pattern_label": "General"} for q in general_cat]

        # Company-specific subset might be small; use all + supplement
        combined = list(tagged)

        # If we don't have enough, supplement from general
        if len(combined) < count:
            # Shuffle general and pick enough to fill
            random.shuffle(general_tagged)
            existing_qs = {q["question"] for q in combined}
            needed = count - len(combined)
            for gq in general_tagged:
                if needed <= 0:
                    break
                if gq["question"] not in existing_qs:
                    combined.append(gq)
                    existing_qs.add(gq["question"])
                    needed -= 1

        # Randomly sample the requested count
        random.shuffle(combined)
        return combined[:min(count, len(combined))]

    # Sample from the company-specific subset
    quant = _sample_from_subset(subset, "quantitative", num_quant)
    logical = _sample_from_subset(subset, "logical_reasoning", num_logical)
    verbal = _sample_from_subset(subset, "verbal", num_verbal)

    combined = quant + logical + verbal
    random.shuffle(combined)

    # Shuffle options for each question (prevents rote memorization)
    combined = [_shuffle_options(q) for q in combined]

    return combined


def format_aptitude_answer_record(q_data: dict, selected_option: int) -> dict:
    """
    Build a standardized answer record dict from aptitude question data.
    Called by interview_engine._handle_aptitude_answer().

    Args:
        q_data: Aptitude question dict with keys: question, options, correct,
                explanation, category, company, is_advanced, company_pattern_label
        selected_option: Index (0-3) of the option chosen, or -1 for no selection

    Returns:
        Dict matching the answer record schema expected by save_answers_to_db()
        with binary scoring (10/0), full feedback, and MCQ-specific fields.
    """
    is_correct = 0 <= selected_option < len(q_data["options"]) and selected_option == q_data["correct"]
    correct_idx = q_data["correct"]
    correct_text = q_data["options"][correct_idx] if 0 <= correct_idx < len(q_data["options"]) else ""

    return {
        "question": q_data["question"],
        "answer": q_data["options"][selected_option] if 0 <= selected_option < len(q_data["options"]) else "No selection",
        "category": q_data.get("category", "aptitude"),
        "difficulty": "medium",
        "overall_score": 10 if is_correct else 0,
        "technical_score": 10 if is_correct else 0,
        "communication_score": 5,
        "confidence_score": 5,
        "problem_solving_score": 10 if is_correct else 0 if selected_option >= 0 else 2,
        "time_management_score": 5,
        "conceptual_clarity_score": 10 if is_correct else 0,
        "feedback": "Correct!" if is_correct else (
            f"Incorrect. The correct answer is: {correct_text}" if selected_option >= 0
            else "Time expired. No option selected."
        ),
        "improved_answer": "",
        "ideal_answer": correct_text,
        "improvement_tip": "Review the explanation below to understand the correct approach.",
        "score_explanation": "Aptitude questions use binary scoring: 10 for correct, 0 for incorrect.",
        "strengths": [],
        "weaknesses": [] if is_correct else ["Incorrect answer"],
        "keywords_used": [],
        "keywords_missed": [],
        "filler_word_count": 0,
        "filler_words": {},
        "rewrite_used": False,
        "rewrite_text": "",
        "rewrite_scores": {},
        "is_mcq": True,
        "selected_option": selected_option if selected_option >= 0 else None,
        "is_correct": is_correct,
        "time_expired": selected_option < 0 or selected_option >= len(q_data.get("options", [])),
        "correct_option": correct_idx,
        "correct_answer": correct_text,
        "explanation": q_data.get("explanation", ""),
    }
