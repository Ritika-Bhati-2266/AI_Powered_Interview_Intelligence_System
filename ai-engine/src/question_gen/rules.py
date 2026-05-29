from typing import List, Dict, Any

# Extensive catalog of skills mapped to technical questions
TECH_QUESTION_BANK: Dict[str, List[str]] = {
    "python": [
        "What is the difference between deep copy and shallow copy in Python?",
        "Can you explain Python's Global Interpreter Lock (GIL) and how it impacts multi-threading?",
        "How do generators work in Python, and when would you use them over list comprehensions?"
    ],
    "javascript": [
        "Explain event delegation and event bubbling in JavaScript.",
        "What is a closure in JavaScript, and what are some common use cases for it?",
        "What is the event loop, and how does it handle asynchronous code execution?"
    ],
    "typescript": [
        "What are the key benefits of TypeScript over vanilla JavaScript, and how do interfaces differ from types?",
        "Explain generics in TypeScript and how you have used them to build reusable components.",
        "How does TypeScript's utility type 'ReturnType' or 'Partial' work?"
    ],
    "react": [
        "How does React's Virtual DOM work under the hood, and how does it optimize rendering performance?",
        "Explain the lifecycle of a React component and how the 'useEffect' dependency array works.",
        "What are the differences between React Context and state management systems like Redux?"
    ],
    "docker": [
        "What is the difference between a Docker image and a Docker container?",
        "How do you optimize a Dockerfile to achieve smaller, multi-stage build sizes?",
        "What are Docker volumes and when would you use them over bind mounts?"
    ],
    "sql": [
        "What is the difference between INNER JOIN, LEFT JOIN, and outer joins in SQL?",
        "Explain database normalization (1NF, 2NF, 3NF) and when you might denormalize a database for performance.",
        "How do database indexes speed up query performance, and what are their drawbacks?"
    ],
    "machine learning": [
        "Explain the bias-variance tradeoff and how you prevent overfitting in deep learning models.",
        "How does the transformer architecture differ from traditional RNNs and LSTMs?",
        "What metrics would you use to evaluate an imbalanced classification model?"
    ],
    "node.js": [
        "How does the Node.js event-driven, non-blocking I/O model work?",
        "What is the difference between 'setImmediate()' and 'process.nextTick()' in Node?",
        "How do you manage worker threads or clusters to scale a heavy-CPU application in Node?"
    ]
}

# Standard HR Question Bank
HR_QUESTION_BANK: List[str] = [
    "Tell me about a time when you faced a difficult challenge at work and how you overcame it.",
    "Why are you interested in joining our company, and what do you hope to accomplish in your next role?",
    "Describe a situation where you had a conflict with a team member. How did you resolve it?",
    "Where do you see yourself in five years, and how does this role align with your long-term career goals?",
    "How do you prioritize your tasks and manage tight deadlines in a fast-paced development environment?"
]

# Standard Follow-up Question Templates (based on project descriptions)
FOLLOW_UP_TEMPLATES: List[str] = [
    "You mentioned a project in your resume: '{project_name}'. What was the biggest technical roadblock you encountered, and how did you resolve it?",
    "Looking at '{project_name}', what architectural changes would you make if you had to rebuild this system today?",
    "How did you measure the success or performance impact of '{project_name}' in your role?",
    "If you were tasked with scaling '{project_name}' to handle 10x more users or data, what bottlenecks would you expect to hit first?"
]

def generate_fallback_questions(resume_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate interview questions using a structured rule-based system.
    Parses resume_data (skills, projects, experience) and matches templates.
    """
    skills = [s.lower().strip() for s in resume_data.get("skills", [])]
    projects = resume_data.get("projects", [])
    experience_years = resume_data.get("experience_years", 2)
    
    # 1. Determine seniority level
    seniority = "Junior"
    if experience_years >= 5:
        seniority = "Senior"
    elif experience_years >= 3:
        seniority = "Mid-level"

    # 2. Extract Technical Questions
    tech_questions = []
    matched_skills = []
    
    for skill in skills:
        if skill in TECH_QUESTION_BANK:
            matched_skills.append(skill)
            # Add questions for this skill
            for idx, q in enumerate(TECH_QUESTION_BANK[skill]):
                tech_questions.append({
                    "id": f"tech-{skill}-{idx}",
                    "question": q,
                    "focus": skill,
                    "difficulty": "Advanced" if seniority == "Senior" else "Medium"
                })
                
    # Fallbacks if no specific tech skills are matched
    if not tech_questions:
        tech_questions.append({
            "id": "tech-generic-1",
            "question": "Can you describe your ideal local software engineering tech stack and explain why you prefer it?",
            "focus": "Software Architecture",
            "difficulty": "Medium"
        })
        tech_questions.append({
            "id": "tech-generic-2",
            "question": "How do you ensure your code is maintainable, clean, and well-tested?",
            "focus": "Clean Code",
            "difficulty": "Medium"
        })
    
    # 3. Extract HR Questions
    hr_questions = []
    for idx, q in enumerate(HR_QUESTION_BANK[:3]):
        hr_questions.append({
            "id": f"hr-{idx}",
            "question": q,
            "focus": "Behavioral",
            "difficulty": "Medium"
        })
        
    # Add a seniority specific behavioral question
    if seniority == "Senior":
        hr_questions.append({
            "id": "hr-senior-1",
            "question": "Describe a time you had to mentor a junior engineer or lead a cross-functional technical initiative. What was your strategy?",
            "focus": "Leadership",
            "difficulty": "Hard"
        })

    # 4. Extract Follow-up Questions based on Projects
    follow_up_questions = []
    if projects:
        for p_idx, project in enumerate(projects[:2]):
            project_name = project if isinstance(project, str) else project.get("name", "Key Project")
            for t_idx, template in enumerate(FOLLOW_UP_TEMPLATES[:2]):
                follow_up_questions.append({
                    "id": f"follow-{p_idx}-{t_idx}",
                    "question": template.format(project_name=project_name),
                    "focus": f"Project: {project_name}",
                    "difficulty": "Medium"
                })
    else:
        # Fallback project followups
        follow_up_questions.append({
            "id": "follow-generic-1",
            "question": "In your most recent project, what was the division of labor, and how did you coordinate API definitions with other team members?",
            "focus": "Collaboration",
            "difficulty": "Medium"
        })

    return {
        "hr": hr_questions,
        "technical": tech_questions[:5], # Cap technical questions to 5
        "follow_up": follow_up_questions[:4] # Cap follow-ups to 4
    }
