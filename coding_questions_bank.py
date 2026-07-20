"""
Coding Questions Bank — Company-Specific Pattern Subsets
Each company subset reflects the well-known DSA/algorithm topics and
question STYLE that candidates widely report experiencing in:
- Glassdoor interview reviews
- LeetCode company-specific problem lists
- GeeksforGeeks company interview experience articles

All questions are ORIGINAL text written in each company's known style.
No verbatim reproduction of copyrighted problem banks.
"""

import random

# ── Company-specific coding style guides (used in Ollama prompts) ────────────

COMPANY_CODING_STYLE = {
    "google": {
        "style_guide": (
            "Google interviews are known for: graph traversal (BFS/DFS), "
            "dynamic programming, tree problems, and system-design thinking integrated "
            "into coding rounds. Interviewers expect discussion of optimal time/space "
            "complexity, trade-offs in algorithm choice, and handling of edge cases. "
            "Questions often explore multiple approaches from brute-force to optimal."
        ),
        "style_label": "Google-style: DSA depth + complexity analysis",
    },
    "amazon": {
        "style_guide": (
            "Amazon coding rounds often involve array/string manipulation tied to "
            "'practical' scenarios (e.g., order processing, item recommendations). "
            "After the coding problem, interviewers commonly ask a Leadership Principle "
            "question (e.g., 'Tell me about a time you optimized something under deadline'). "
            "Questions test clean code, scalability thinking, and customer-obsession framing."
        ),
        "style_label": "Amazon-style: practical DSA + Leadership Principle",
    },
    "microsoft": {
        "style_guide": (
            "Microsoft interviews focus on clean DSA fundamentals — arrays, strings, "
            "linked lists, trees — with occasional OOP design questions (e.g., "
            "'design a parking lot system'). For cloud-related roles, expect Azure-adjacent "
            "scenario problems. Interviewers value clean, well-structured code with clear "
            "variable names and modular design."
        ),
        "style_label": "Microsoft-style: clean DSA + OOP design",
    },
    "meta": {
        "style_guide": (
            "Meta (Facebook) is known for heavy DSA with mandatory Big-O analysis "
            "follow-ups — interviewers often ask 'what's the runtime and can we do better'. "
            "Product-sense-adjacent coding may appear (e.g., 'design a rate limiter' or "
            "'design a news feed ranking function'). Questions tend toward medium-hard "
            "difficulty on common patterns."
        ),
        "style_label": "Meta-style: DSA + Big-O analysis + product context",
    },
    "flipkart": {
        "style_guide": (
            "Flipkart coding rounds feature e-commerce scenario problems — cart management, "
            "inventory tracking, discount calculation, order sorting/filtering — alongside "
            "standard DSA. System design discussions often reference e-commerce scale "
            "(millions of products, peak sale traffic)."
        ),
        "style_label": "Flipkart-style: e-commerce scenario + DSA",
    },
    "apple": {
        "style_guide": (
            "Apple emphasizes clean code and attention to detail. Questions may test "
            "memory management concepts, especially for iOS/macOS roles. Interviewers "
            "notice code formatting, naming conventions, and careful edge-case handling. "
            "Domain-specific questions for hardware-adjacent roles are common."
        ),
        "style_label": "Apple-style: clean code + attention to detail",
    },
    "tcs": {
        "style_guide": (
            "TCS coding rounds test basic programming fundamentals — loops, arrays, "
            "string manipulation, basic OOP concepts. Focus is on correctness rather "
            "than optimization. Simple SQL query writing may be included. Difficulty "
            "is significantly lower than product companies."
        ),
        "style_label": "TCS-style: fundamentals + SQL basics",
    },
    "infosys": {
        "style_guide": (
            "Infosys coding rounds focus on basic DSA, OOP in Java/Python, and "
            "SQL queries. Questions involve arrays, strings, recursion basics, and "
            "simple class design. Emphasis on fundamental programming concepts."
        ),
        "style_label": "Infosys-style: OOP + SQL + basic DSA",
    },
    "wipro": {
        "style_guide": (
            "Wipro coding assessments test basic programming logic — loops, conditionals, "
            "arrays, string operations. Questions are straightforward with clear specs. "
            "Written communication and code commenting are valued."
        ),
        "style_label": "Wipro-style: programming fundamentals",
    },
    "hcl": {
        "style_guide": (
            "HCL coding questions are relatively simple — basic loops, array traversals, "
            "pattern printing. Focus on correctness over efficiency. Simple SQL queries "
            "and basic OOP concepts may appear."
        ),
        "style_label": "HCL-style: basic programming + logic",
    },
}

# ── Company-specific coding pattern indicators ───────────────────────────────

# Which companies each coding pattern is known for
COMPANY_CODING_PATTERNS = {
    "trees_graphs": ["google", "amazon", "meta", "microsoft"],
    "dynamic_programming": ["google", "meta", "amazon"],
    "arrays_strings": ["google", "amazon", "microsoft", "meta", "flipkart", "apple", "tcs", "infosys", "wipro", "hcl"],
    "system_design": ["google", "amazon", "microsoft", "flipkart"],
    "linked_lists": ["microsoft", "google", "amazon"],
    "recursion": ["google", "meta", "infosys"],
    "sorting_searching": ["google", "amazon", "meta", "microsoft", "flipkart"],
    "oop_design": ["microsoft", "amazon", "infosys"],
    "sql_queries": ["tcs", "infosys", "wipro", "hcl"],
    "basic_programming": ["tcs", "infosys", "wipro", "hcl"],
    "ecommerce_scenarios": ["flipkart"],
    "memory_management": ["apple"],
    "rate_limiting_concurrency": ["meta", "google"],
}

# ── Fallback Coding Questions by Difficulty (tagged with company patterns) ──

FALLBACK_CODING_QUESTIONS = {
    "easy": [
        {
            "question": "Write a function to check whether a given string is a palindrome.",
            "difficulty": "easy",
            "category": "strings",
            "companies": ["tcs", "infosys", "wipro", "hcl", "microsoft", "amazon"],
            "company_style_notes": "Basic string manipulation — common at all levels",
        },
        {
            "question": "Write a function to find the second largest element in an integer array.",
            "difficulty": "easy",
            "category": "arrays",
            "companies": ["tcs", "infosys", "wipro", "hcl", "amazon", "google"],
            "company_style_notes": "Array traversal — tests basic iteration logic",
        },
        {
            "question": "Write a function to count the frequency of each character in a string.",
            "difficulty": "easy",
            "category": "strings",
            "companies": ["tcs", "infosys", "wipro", "hcl", "amazon", "microsoft"],
            "company_style_notes": "Hash map / frequency counting — fundamental pattern",
        },
        {
            "question": "Write a function to reverse an array in-place.",
            "difficulty": "easy",
            "category": "arrays",
            "companies": ["tcs", "infosys", "wipro", "hcl", "apple", "microsoft"],
            "company_style_notes": "In-place manipulation — tests pointer/swap understanding",
        },
        {
            "question": "Write a function that returns the sum of all elements in a 2D matrix.",
            "difficulty": "easy",
            "category": "arrays",
            "companies": ["tcs", "infosys", "wipro", "hcl"],
            "company_style_notes": "Nested loops — basic programming fundamentals",
        },
        {
            "question": "Write a SQL query to select employees who earn more than the average salary in their department.",
            "difficulty": "easy",
            "category": "sql",
            "companies": ["tcs", "infosys", "wipro", "hcl"],
            "company_style_notes": "SQL subquery with GROUP BY — common in Indian IT coding rounds",
        },
        {
            "question": "Write a function to print the Fibonacci series up to n terms.",
            "difficulty": "easy",
            "category": "recursion",
            "companies": ["tcs", "infosys", "wipro", "hcl", "google", "microsoft"],
            "company_style_notes": "Recursion vs iteration — classic entry-level question",
        },
        {
            "question": "Write a class BankAccount with deposit, withdraw, and balance methods. Demonstrate basic OOP.",
            "difficulty": "easy",
            "category": "oop",
            "companies": ["tcs", "infosys", "wipro", "hcl", "microsoft"],
            "company_style_notes": "Basic OOP encapsulation — Infosys and Microsoft commonly test class design",
        },
    ],
    "medium": [
        {
            "question": "Write a function to find if there are two numbers in an array that sum to a target value.",
            "difficulty": "medium",
            "category": "arrays",
            "companies": ["google", "amazon", "meta", "microsoft", "flipkart"],
            "company_style_notes": "Two-sum pattern — Google/Amazon staple with hash map optimization",
        },
        {
            "question": "Write a function to find the longest substring without repeating characters.",
            "difficulty": "medium",
            "category": "strings",
            "companies": ["google", "amazon", "meta", "microsoft"],
            "company_style_notes": "Sliding window — common in FAANG coding rounds",
        },
        {
            "question": "Write a function to merge two sorted linked lists.",
            "difficulty": "medium",
            "category": "linked_lists",
            "companies": ["google", "microsoft", "amazon", "meta"],
            "company_style_notes": "Linked list manipulation — Microsoft and Google commonly ask this",
        },
        {
            "question": "Write a function to check if a binary tree is balanced (height difference ≤ 1 between subtrees).",
            "difficulty": "medium",
            "category": "trees",
            "companies": ["google", "amazon", "meta"],
            "company_style_notes": "Tree recursion + complexity analysis — Google signature style",
        },
        {
            "question": "Design an order discount system for an e-commerce cart. Given items with prices and categories, calculate the total after applying: (1) 10% off if cart total > Rs. 1000, (2) buy-2-get-1-free on the cheapest item.",
            "difficulty": "medium",
            "category": "ecommerce",
            "companies": ["flipkart", "amazon"],
            "company_style_notes": "E-commerce scenario — Flipkart signature style with practical business logic",
        },
        {
            "question": "Write a function to serialize and deserialize a binary tree.",
            "difficulty": "medium",
            "category": "trees",
            "companies": ["google", "amazon", "meta"],
            "company_style_notes": "Tree traversal + string encoding — Google's serialization question pattern",
        },
        {
            "question": "Design a rate limiter that limits API calls to 100 requests per minute per user.",
            "difficulty": "medium",
            "category": "system_design",
            "companies": ["meta", "google"],
            "company_style_notes": "Product-sense-adjacent coding — Meta signature style",
        },
        {
            "question": "Write a function to detect a cycle in a linked list. What is the time and space complexity?",
            "difficulty": "medium",
            "category": "linked_lists",
            "companies": ["google", "amazon", "meta", "microsoft"],
            "company_style_notes": "Fast-slow pointer + complexity analysis — FAANG staples",
        },
        {
            "question": "Write a SQL query to find the top 3 highest-selling products by revenue in each category in the last month.",
            "difficulty": "medium",
            "category": "sql",
            "companies": ["flipkart", "amazon"],
            "company_style_notes": "Window functions (RANK/DENSE_RANK) — used in e-commerce analytics scenarios",
        },
    ],
    "hard": [
        {
            "question": "Design a system to find the shortest path between two nodes in a weighted graph with 1 million nodes. Discuss trade-offs between Dijkstra, A*, and Floyd-Warshall.",
            "difficulty": "hard",
            "category": "graphs",
            "companies": ["google", "amazon", "meta"],
            "company_style_notes": "Graph algorithms + system design thinking — Google's signature depth discussion",
        },
        {
            "question": "Given a streaming data source, write a function to find the median at any point in O(log n) time per insertion.",
            "difficulty": "hard",
            "category": "design",
            "companies": ["google", "amazon", "meta"],
            "company_style_notes": "Two-heap approach — tests data structure selection under constraints",
        },
        {
            "question": "Design a parking lot system with multiple floors, different vehicle types, and entry/exit tracking.",
            "difficulty": "hard",
            "category": "oop_design",
            "companies": ["microsoft", "amazon"],
            "company_style_notes": "OOD + system design — Microsoft signature 'design a parking lot' question style",
        },
        {
            "question": "Implement a function the finds the maximum path sum in a binary tree. A path can start and end at any node.",
            "difficulty": "hard",
            "category": "trees",
            "companies": ["google", "meta", "amazon"],
            "company_style_notes": "Tree recursion + global variable tracking — Google hard-level pattern",
        },
        {
            "question": "Given an array of integers, find the length of the longest increasing subsequence in O(n log n) time.",
            "difficulty": "hard",
            "category": "dynamic_programming",
            "companies": ["google", "meta", "amazon"],
            "company_style_notes": "DP with binary search optimization — Google/Meta classic hard question",
        },
        {
            "question": "Design an LRU cache with O(1) get and put operations.",
            "difficulty": "hard",
            "category": "design",
            "companies": ["amazon", "google", "meta", "microsoft"],
            "company_style_notes": "HashMap + Doubly Linked List — Amazon/Microsoft common design question",
        },
    ],
}


def get_coding_fallback(difficulty: str = "medium", company: str = "general") -> dict:
    """
    Get a fallback coding question appropriate for a given company's known style.

    Args:
        difficulty: 'easy', 'medium', or 'hard'
        company: Company name

    Returns:
        Question dict with question, difficulty, category, company_style_notes
    """
    company_lower = company.lower().strip()

    # Get questions at the requested difficulty
    questions = FALLBACK_CODING_QUESTIONS.get(difficulty, FALLBACK_CODING_QUESTIONS["medium"])

    # Filter by company match or general
    company_qs = [q for q in questions if company_lower in q.get("companies", [])]

    if not company_qs:
        # No company-specific fallback — use any that include "general" or take first
        company_qs = questions

    return random.choice(company_qs)


def get_coding_style_context(company: str) -> str:
    """
    Get the company-specific coding style context for Ollama prompts.

    Returns a string describing what this company is known for asking
    in coding rounds, to be injected into the question generation prompt.
    """
    company_lower = company.lower().strip()
    config = COMPANY_CODING_STYLE.get(company_lower)
    if config:
        return config["style_guide"]
    return ""  # No specific style — use default generic questions


def get_coding_style_label(company: str) -> str:
    """Get the short display label for a company's coding style."""
    company_lower = company.lower().strip()
    config = COMPANY_CODING_STYLE.get(company_lower)
    if config:
        return config["style_label"]
    return "Coding Question"
