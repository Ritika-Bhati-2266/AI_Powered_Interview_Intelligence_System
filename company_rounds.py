"""
Company-Specific Interview Round Structures
Defines FIXED rounds per company for multi-round interviews.
Each round specifies its type (coding/technical/hr), question count, duration, and focus area.
"""

COMPANY_ROUNDS = {
    "Google": [
        {"name": "Phone Screen", "type": "coding", "questions": 2, "duration_min": 45, "focus": "DSA - Arrays, Strings, Hash Maps"},
        {"name": "Technical Round 1", "type": "coding", "questions": 2, "duration_min": 45, "focus": "Trees, Graphs, Recursion"},
        {"name": "Technical Round 2", "type": "coding", "questions": 2, "duration_min": 45, "focus": "Dynamic Programming, System Design basics"},
        {"name": "Googleyness/Behavioral", "type": "hr", "questions": 5, "duration_min": 30, "focus": "Leadership, ambiguity, collaboration"},
    ],
    "Amazon": [
        {"name": "Online Assessment", "type": "coding", "questions": 2, "duration_min": 60, "focus": "DSA - Medium difficulty"},
        {"name": "Technical Round 1", "type": "coding", "questions": 2, "duration_min": 45, "focus": "Data Structures + 1 Leadership Principle"},
        {"name": "Technical Round 2", "type": "coding", "questions": 2, "duration_min": 45, "focus": "System Design + 1 Leadership Principle"},
        {"name": "Bar Raiser", "type": "hr", "questions": 6, "duration_min": 45, "focus": "All 16 Leadership Principles, deep behavioral"},
        {"name": "Hiring Manager", "type": "hr", "questions": 5, "duration_min": 30, "focus": "Role fit, motivation, team dynamics"},
    ],
    "Microsoft": [
        {"name": "Online Assessment", "type": "coding", "questions": 2, "duration_min": 60, "focus": "DSA fundamentals"},
        {"name": "Technical Round 1", "type": "coding", "questions": 2, "duration_min": 45, "focus": "OOP, Design Patterns"},
        {"name": "Technical Round 2", "type": "coding", "questions": 2, "duration_min": 45, "focus": "System Design, Azure/Cloud concepts"},
        {"name": "As Appropriate (AA) Round", "type": "hr", "questions": 5, "duration_min": 30, "focus": "Growth mindset, collaboration, culture fit"},
    ],
    "Meta": [
        {"name": "Phone Screen", "type": "coding", "questions": 2, "duration_min": 45, "focus": "DSA - Graphs, Arrays"},
        {"name": "Coding Round 1", "type": "coding", "questions": 2, "duration_min": 45, "focus": "Medium-Hard DSA"},
        {"name": "Coding Round 2", "type": "coding", "questions": 2, "duration_min": 45, "focus": "Hard DSA, optimization"},
        {"name": "System Design", "type": "technical", "questions": 2, "duration_min": 45, "focus": "Scalability, distributed systems"},
        {"name": "Behavioral", "type": "hr", "questions": 5, "duration_min": 30, "focus": "Meta values, conflict resolution"},
    ],
    "Apple": [
        {"name": "Technical Screen", "type": "technical", "questions": 3, "duration_min": 45, "focus": "Core CS fundamentals"},
        {"name": "Technical Round", "type": "coding", "questions": 2, "duration_min": 45, "focus": "DSA + domain specific (iOS/Swift if relevant)"},
        {"name": "Team Fit", "type": "hr", "questions": 5, "duration_min": 30, "focus": "Attention to detail, design thinking, culture"},
    ],
    "Flipkart": [
        {"name": "Online Assessment", "type": "coding", "questions": 2, "duration_min": 60, "focus": "DSA Medium-Hard"},
        {"name": "Technical Round 1", "type": "coding", "questions": 2, "duration_min": 45, "focus": "Java/Python + DSA"},
        {"name": "Technical Round 2", "type": "technical", "questions": 2, "duration_min": 45, "focus": "System Design - e-commerce scale"},
        {"name": "HR Round", "type": "hr", "questions": 5, "duration_min": 30, "focus": "Culture fit, career goals"},
    ],
    "TCS": [
        {"name": "Aptitude Test", "type": "aptitude", "questions": 10, "duration_min": 30, "focus": "Quantitative, Logical Reasoning, Verbal Ability"},
        {"name": "Technical Round", "type": "coding", "questions": 3, "duration_min": 45, "focus": "Basic DSA, OOP, SQL"},
        {"name": "Managerial Round", "type": "technical", "questions": 3, "duration_min": 30, "focus": "Project discussion, basic concepts"},
        {"name": "HR Round", "type": "hr", "questions": 5, "duration_min": 20, "focus": "Communication, willingness to relocate"},
    ],
    "Infosys": [
        {"name": "Aptitude Test", "type": "aptitude", "questions": 10, "duration_min": 30, "focus": "Quantitative, Logical Reasoning, Verbal Ability"},
        {"name": "Technical Round", "type": "coding", "questions": 3, "duration_min": 45, "focus": "Basic DSA, OOP, SQL, Java/Python basics"},
        {"name": "HR Round", "type": "hr", "questions": 5, "duration_min": 20, "focus": "Communication, background, motivation"},
    ],
    "Wipro": [
        {"name": "Aptitude Test", "type": "aptitude", "questions": 10, "duration_min": 30, "focus": "Quantitative, Logical Reasoning, Verbal Ability"},
        {"name": "Technical Round", "type": "coding", "questions": 3, "duration_min": 45, "focus": "Basic DSA, programming fundamentals"},
        {"name": "HR Round", "type": "hr", "questions": 5, "duration_min": 20, "focus": "Communication, culture fit"},
    ],
    "HCL": [
        {"name": "Aptitude Test", "type": "aptitude", "questions": 10, "duration_min": 30, "focus": "Quantitative, Logical Reasoning, Verbal Ability"},
        {"name": "Technical Round", "type": "coding", "questions": 3, "duration_min": 45, "focus": "Basic DSA, fundamentals"},
        {"name": "HR Round", "type": "hr", "questions": 5, "duration_min": 20, "focus": "Communication, background"},
    ],
    "Startup": [
        {"name": "Technical Round", "type": "coding", "questions": 3, "duration_min": 45, "focus": "Practical problem solving, full-stack basics"},
        {"name": "Founder/Culture Fit", "type": "hr", "questions": 4, "duration_min": 25, "focus": "Ownership, adaptability, passion"},
    ],
    "General": [
        {"name": "Technical Round", "type": "technical", "questions": 4, "duration_min": 40, "focus": "Role-relevant technical questions"},
        {"name": "HR Round", "type": "hr", "questions": 4, "duration_min": 25, "focus": "Behavioral, communication"},
    ],
}


def get_rounds_for_company(company: str) -> list:
    """Get the fixed round structure for a given company. Falls back to General if not found."""
    return COMPANY_ROUNDS.get(company, COMPANY_ROUNDS["General"])
