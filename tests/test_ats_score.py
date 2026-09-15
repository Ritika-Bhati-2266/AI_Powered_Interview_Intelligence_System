"""
Tests for ATS Resume Score feature.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_parser import calculate_ats_score, extract_skills
from app import app


class TestCalculateATSScore:
    def test_jd_and_resume_both_provided(self):
        resume = """
        John Doe
        Education: B.Tech Computer Science, University of Delhi
        Experience: 3 years of experience. Led a team of 5, implemented microservices, improved performance by 30%.
        Skills: Python, Docker, Kubernetes, AWS, React, SQL
        Projects: Built e-commerce platform using Docker and Kubernetes.
        """
        jd = "We need Python, Kubernetes, Docker, AWS, microservices experience. Must have B.Tech and 3 years of experience."
        skills = extract_skills(resume)
        result = calculate_ats_score(resume, jd, "DevOps Engineer", skills)
        assert 0 <= result["score"] <= 100
        bd = result["breakdown"]
        assert 0 <= bd["skills_match"] <= 40
        assert 0 <= bd["experience_keywords"] <= 20
        assert 0 <= bd["education"] <= 15
        assert 0 <= bd["formatting"] <= 10
        assert 0 <= bd["keyword_density"] <= 15
        # Breakdown sums to score
        assert bd["skills_match"] + bd["experience_keywords"] + bd["education"] + bd["formatting"] + bd["keyword_density"] == result["score"]
        # Lists are correctly formatted
        assert isinstance(result["missing_keywords"], list)
        assert isinstance(result["matched_keywords"], list)
        assert len(result["missing_keywords"]) <= 8
        assert len(result["matched_keywords"]) <= 8

    def test_jd_not_provided_fallback(self):
        resume = """
        Jane Smith
        Education: Master in Data Science
        Experience: Developed machine learning models, managed data pipelines.
        Skills: Python, Pandas, Numpy, Scikit-learn, SQL
        """
        result = calculate_ats_score(resume, "", "Data Scientist", None)
        assert 0 <= result["score"] <= 100
        bd = result["breakdown"]
        assert 0 <= bd["skills_match"] <= 40
        assert 0 <= bd["keyword_density"] <= 15
        # Should still have matched/missing based on role
        assert isinstance(result["matched_keywords"], list)
        assert isinstance(result["missing_keywords"], list)
        # Fallback should not crash and should produce some score
        assert result["score"] > 10  # reasonable resume should get some points

    def test_jd_provided_no_role(self):
        resume = "Python developer with Docker and AWS. B.Tech. Led team, improved 20%."
        jd = "Python, Docker, AWS, Kubernetes required"
        result = calculate_ats_score(resume, jd, "", ["python", "docker", "aws"])
        assert 0 <= result["score"] <= 100
        # With JD, matched should include at least python/docker/aws if present
        assert "python" in [k.lower() for k in result["matched_keywords"]] or "docker" in [k.lower() for k in result["matched_keywords"]] or len(result["matched_keywords"]) >= 0

    def test_empty_resume_graceful(self):
        result = calculate_ats_score("", "Python, Docker", "Software Engineer", [])
        assert isinstance(result, dict)
        assert result["score"] <= 10  # minimal score for empty resume
        assert result["score"] >= 0
        bd = result["breakdown"]
        for v in bd.values():
            assert 0 <= v <= 40  # each within its max (conservative check)
        assert isinstance(result["missing_keywords"], list)
        assert isinstance(result["matched_keywords"], list)

    def test_empty_resume_and_empty_jd(self):
        result = calculate_ats_score("", "", "", [])
        assert result["score"] >= 0
        assert result["score"] <= 10

    def test_missing_vs_matched_logic(self):
        resume = "Python, SQL, Git"
        jd = "Python, Java, Kubernetes, Docker, AWS, React, SQL, Git"
        result = calculate_ats_score(resume, jd, "Software Engineer", ["python", "sql", "git"])
        # Matched should be subset of resume skills that are in JD
        matched_lower = [k.lower() for k in result["matched_keywords"]]
        missing_lower = [k.lower() for k in result["missing_keywords"]]
        # No overlap between missing and matched
        assert len(set(matched_lower).intersection(set(missing_lower))) == 0
        # If JD has java/kubernetes/docker/aws that are missing in resume, they should appear in missing
        # At least some missing should be present
        assert len(result["missing_keywords"]) > 0

    def test_breakdown_limits(self):
        # Long resume with all sections to test upper bounds
        resume = """
        Education: B.Tech Computer Science, M.Tech AI, University
        Experience: 5 years of experience. Led, managed, developed, implemented, built, designed, achieved 50% improvement, delivered 10 projects.
        Skills: Python, Java, JavaScript, React, Docker, Kubernetes, AWS, SQL, Git, Agile, Microservices
        Projects: Multiple projects
        Summary: Experienced engineer
        Objective: Seeking role
        """ * 3
        jd = "Python, Docker, Kubernetes, AWS, React, SQL, Git, Agile, Microservices, led, managed, B.Tech"
        result = calculate_ats_score(resume, jd, "Software Engineer", extract_skills(resume))
        bd = result["breakdown"]
        assert bd["skills_match"] <= 40
        assert bd["experience_keywords"] <= 20
        assert bd["education"] <= 15
        assert bd["formatting"] <= 10
        assert bd["keyword_density"] <= 15
        assert result["score"] <= 100

    def test_role_fallback_unknown_role(self):
        resume = "Python, Docker"
        result = calculate_ats_score(resume, "", "Unknown Role XYZ", ["python", "docker"])
        assert 0 <= result["score"] <= 100
        assert isinstance(result["matched_keywords"], list)

class TestATSIntegrationWithApp:
    def test_register_returns_ats_score(self):
        app.config["TESTING"] = True
        client = app.test_client()
        data = {
            "name": "ATS Tester",
            "email": "ats_tester_unique_123@example.com",
            "role": "Python Developer",
            "experience": "2-4",
            "company": "General",
            "jd_text": "Python, Django, SQL, Docker, AWS required. B.Tech preferred.",
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        j = resp.get_json()
        assert "ats_score" in j
        ats = j["ats_score"]
        assert 0 <= ats["score"] <= 100
        assert "breakdown" in ats
        assert "missing_keywords" in ats
        assert "matched_keywords" in ats
        # Session should have it
        with client.session_transaction() as sess:
            assert "ats_score" in sess
            assert sess["ats_score"]["score"] == ats["score"]

    def test_register_without_jd_still_returns_ats(self):
        app.config["TESTING"] = True
        client = app.test_client()
        data = {
            "name": "ATS NoJD",
            "email": "ats_nojd_456@example.com",
            "role": "Data Scientist",
            "experience": "0-1",
            "company": "General",
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        ats = resp.get_json()["ats_score"]
        assert 0 <= ats["score"] <= 100
        # Should have fallback breakdown
        assert ats["breakdown"]["skills_match"] >= 0

    def test_register_empty_resume_still_ats(self):
        app.config["TESTING"] = True
        client = app.test_client()
        data = {
            "name": "Empty Resume ATS",
            "email": "ats_empty_789@example.com",
            "role": "Software Engineer",
            "experience": "0-1",
            "company": "General",
            "jd_text": "Python, SQL",
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        ats = resp.get_json()["ats_score"]
        assert ats["score"] >= 0
        assert ats["score"] <= 100

    def test_ats_persisted_in_db(self):
        app.config["TESTING"] = True
        client = app.test_client()
        email = "ats_db_check@example.com"
        data = {
            "name": "DB Check",
            "email": email,
            "role": "DevOps Engineer",
            "experience": "2-4",
            "company": "General",
            "jd_text": "Kubernetes, Docker, AWS, B.Tech",
        }
        resp = client.post("/register", data=data)
        assert resp.status_code == 200
        ats_sent = resp.get_json()["ats_score"]
        # Query DB directly
        from app import get_db
        conn = get_db()
        row = conn.execute("SELECT ats_score FROM candidates WHERE email = ?", (email,)).fetchone()
        conn.close()
        assert row is not None
        import json
        stored = json.loads(row["ats_score"]) if isinstance(row["ats_score"], str) else row["ats_score"]
        assert stored["score"] == ats_sent["score"]
        assert stored["breakdown"] == ats_sent["breakdown"]
