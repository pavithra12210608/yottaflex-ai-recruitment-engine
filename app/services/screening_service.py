"""Deterministic Candidate Screening Service based strictly on job-related criteria."""
from typing import Dict, List, Tuple, Any

PROFICIENCY_SCORES = {
    "Beginner": 1.0,
    "Intermediate": 2.0,
    "Advanced": 3.0,
    "Expert": 4.0,
}

EDUCATION_SCORES = {
    "Bootcamp": 70.0,
    "BSc": 80.0,
    "MSc": 90.0,
    "PhD": 100.0,
}

SCREENING_PASS_THRESHOLD = 70.0


def calculate_candidate_score(
    candidate_experience: float,
    candidate_education: str,
    candidate_domain: str,
    candidate_skills: Dict[str, Dict[str, Any]],  # skill_id -> {proficiency_level, years_experience}
    req_min_experience: int,
    req_title: str,
    screening_rules: List[Dict[str, Any]],  # List of rule dicts with skill_id, is_mandatory, min_proficiency, weight
) -> Tuple[float, bool, str, Dict[str, Any]]:
    """Calculates deterministic screening score for a candidate against a requisition.
    
    Job-Related Criteria Only:
    1. Skill Match Score (50% weight):
       - Mandatory skills: If candidate lacks any mandatory skill or has insufficient proficiency, score penalty applies.
       - Weighted match across all required skills.
    2. Experience Score (30% weight):
       - Compares candidate years of experience against requisition minimum.
    3. Education Score (10% weight):
       - Structured baseline rating for degree / vocational preparation.
    4. Domain Specialization Score (10% weight):
       - Semantic domain match between resume artifact domain and requisition role family.
    
    Returns:
        (total_score, passed, rejection_reason, breakdown_dict)
    """
    rejection_reasons = []

    # 1. Skill Match
    total_rule_weight = sum(rule.get("weight", 1.0) for rule in screening_rules) or 1.0
    accumulated_skill_score = 0.0
    mandatory_failed = False

    for rule in screening_rules:
        skill_id = rule["skill_id"]
        weight = rule.get("weight", 1.0)
        min_prof = rule.get("min_proficiency", "Intermediate")
        required_prof_val = PROFICIENCY_SCORES.get(min_prof, 2.0)
        is_mandatory = rule.get("is_mandatory", False)

        if skill_id in candidate_skills:
            cand_prof = candidate_skills[skill_id]["proficiency_level"]
            cand_prof_val = PROFICIENCY_SCORES.get(cand_prof, 1.0)

            if cand_prof_val >= required_prof_val:
                ratio = 1.0
            else:
                ratio = cand_prof_val / required_prof_val
                if is_mandatory:
                    mandatory_failed = True
                    rejection_reasons.append(f"Mandatory skill {skill_id} proficiency ({cand_prof}) below required ({min_prof})")

            accumulated_skill_score += ratio * weight
        else:
            if is_mandatory:
                mandatory_failed = True
                rejection_reasons.append(f"Missing mandatory skill {skill_id}")

    skill_score = (accumulated_skill_score / total_rule_weight) * 100.0

    # 2. Experience Score (30%)
    if req_min_experience <= 0:
        exp_score = 100.0
    else:
        exp_ratio = candidate_experience / req_min_experience
        if exp_ratio >= 1.5:
            exp_score = 100.0
        elif exp_ratio >= 1.0:
            exp_score = 85.0 + (exp_ratio - 1.0) * 30.0  # 85 to 100
        elif exp_ratio >= 0.7:
            exp_score = 60.0 + (exp_ratio - 0.7) * (25.0 / 0.3)  # 60 to 85
        else:
            exp_score = max(0.0, exp_ratio * 70.0)
            rejection_reasons.append(f"Experience ({candidate_experience} yrs) significantly below required ({req_min_experience} yrs)")

    # 3. Education Score (10%)
    edu_score = EDUCATION_SCORES.get(candidate_education, 75.0)

    # 4. Domain Specialization Score (10%)
    domain_score = 75.0
    req_title_lower = req_title.lower()
    cand_domain_lower = (candidate_domain or "").lower()

    if any(k in req_title_lower and k in cand_domain_lower for k in ["ai", "machine learning", "backend", "cloud", "data", "full stack"]):
        domain_score = 100.0
    elif any(k in cand_domain_lower for k in ["engineering", "systems", "analytics"]):
        domain_score = 85.0

    # Total Score Formula
    total_score = (skill_score * 0.50) + (exp_score * 0.30) + (edu_score * 0.10) + (domain_score * 0.10)
    total_score = round(min(100.0, max(0.0, total_score)), 2)

    passed = (total_score >= SCREENING_PASS_THRESHOLD) and (not mandatory_failed)

    reason = None
    if not passed:
        if rejection_reasons:
            reason = "; ".join(rejection_reasons[:2])
        else:
            reason = f"Screening score {total_score:.1f} below threshold {SCREENING_PASS_THRESHOLD:.1f}"

    breakdown = {
        "skill_score": round(skill_score, 2),
        "experience_score": round(exp_score, 2),
        "education_score": round(edu_score, 2),
        "domain_score": round(domain_score, 2),
        "total_score": total_score,
        "mandatory_failed": mandatory_failed,
    }

    return total_score, passed, reason, breakdown
