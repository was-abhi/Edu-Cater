"""
Edu-Cater College Recommendation Engine
Input Specification:
  - keam_rank: int (gt=0)
  - category: "general" | "obc" | "bx" | "sc" | "st"
  - courses: list[str] (min_length=1, in preferred order: CS, CY, ME, EC, etc.)
  - types: list[str] (min_length=1, in preferred order: Govt., Autonomous, Private)
"""

import os
import pandas as pd
from typing import List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_DAMA_MINING_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Dama Mining'))
import sys
if _DAMA_MINING_DIR not in sys.path:
    sys.path.insert(0, _DAMA_MINING_DIR)
from model.db import query_recommendation_catalog

# Normalized Branch Dictionary for the 8 Permitted Engineering Branches
BRANCH_CANONICAL = {
    'CSE': 'CS', 'CS': 'CS', 'COMPUTER SCIENCE': 'CS', 'COMPUTER SCIENCE & ENGINEERING': 'CS',
    'MECH': 'ME', 'ME': 'ME', 'MECHANICAL': 'ME', 'MECHANICAL ENGINEERING': 'ME',
    'EC': 'EC', 'ECE': 'EC', 'ELECTRONICS': 'EC', 'ELECTRONICS & COMMUNICATION': 'EC',
    'CIVIL': 'CE', 'CE': 'CE', 'CIVIL ENGINEERING': 'CE',
    'EEE': 'EE', 'EE': 'EE', 'ELECTRICAL': 'EE', 'ELECTRICAL & ELECTRONICS': 'EE',
    'AI & DS': 'AD', 'AI_DS': 'AD', 'AD': 'AD', 'ARTIFICIAL INTELLIGENCE AND DATA SCIENCE': 'AD', 'ARTIFICIAL INTELLIGENCE & DATA SCIENCE': 'AD', 'DATA SCIENCE': 'AD',
    'CSE CYBER': 'CY', 'CYBER': 'CY', 'CY': 'CY', 'CSE_CYBER': 'CY', 'CYBER SECURITY': 'CY', 'COMPUTER SCIENCE (CYBER SECURITY)': 'CY',
    'CSE AI': 'AH', 'CSE_AI': 'AH', 'AI': 'AH', 'AH': 'AH', 'ARTIFICIAL INTELLIGENCE': 'AH', 'AI_ML': 'AH', 'AI & ML': 'AH', 'COMPUTER SCIENCE (AI & ML)': 'AH', 'CA': 'AH'
}

CATEGORY_MAP = {
    'general': 'GN', 'gn': 'GN', 'open': 'GN', 'sm': 'GN',
    'obc': 'BH',
    'bh': 'BH',
    'bx': 'BX',
    'sc': 'SC',
    'st': 'ST',
    'ez': 'EZ', 'ezhava': 'EZ',
    'mu': 'MU', 'muslim': 'MU',
    'ew': 'EW', 'ews': 'EW'
}

TYPE_MAP = {
    'govt': 'government',
    'govt.': 'government',
    'government': 'government',
    'autonomous': 'autonomous',
    'autonomous.': 'autonomous',
    'private': 'private',
    'self-financing': 'private'
}

class CollegeRecommender:
    def __init__(self):
        catalog = query_recommendation_catalog()
        if not catalog:
            raise RuntimeError("Supabase returned no recommendation data")

        self.colleges_df = pd.DataFrame(
            [
                {
                    "id": row["id"],
                    "college_code": row["college_code"],
                    "college_name": row["college_name"],
                    "college_type": row["college_type"],
                    "district": row["district"],
                    "pass_percentage": row["pass_percentage"],
                    "nba_accredited": row["nba_accredited"],
                    "naac_accredited": row["naac_accredited"],
                }
                for row in catalog
            ]
        ).drop_duplicates(subset=["id"])

        self.cat_stats = {}
        self.overall_stats = {}
        for row in catalog:
            stats = {
                "opening_rank": int(row["opening_rank"]),
                "closing_rank": int(row["closing_rank"]),
            }
            if row["category"]:
                key = f"{row['college_code']}__{row['course_code']}__{row['category']}"
                self.cat_stats[key] = stats
            else:
                key = f"{row['college_code']}__{row['course_code']}"
                self.overall_stats[key] = stats

        all_stats = list(self.cat_stats.values()) + list(self.overall_stats.values())
        self.min_closing_rank = min(stat["closing_rank"] for stat in all_stats)
        self.max_closing_rank = max(stat["closing_rank"] for stat in all_stats)

    def normalize_branch(self, branch: str) -> Optional[str]:
        cleaned = branch.strip().upper().replace('_', ' ').replace('-', ' ')
        if branch.strip().upper() in BRANCH_CANONICAL:
            return BRANCH_CANONICAL[branch.strip().upper()]
        if cleaned in BRANCH_CANONICAL:
            return BRANCH_CANONICAL[cleaned]
        for key, code in BRANCH_CANONICAL.items():
            if key in cleaned or cleaned in key:
                return code
        return None

    def normalize_category(self, cat: Optional[str]) -> str:
        if not cat:
            return 'GN'
        return CATEGORY_MAP.get(cat.strip().lower(), 'GN')

    def normalize_type(self, t: str) -> Optional[str]:
        t_clean = t.strip().lower()
        if t_clean in TYPE_MAP:
            return TYPE_MAP[t_clean]
        for k, mapped in TYPE_MAP.items():
            if k in t_clean or t_clean in k:
                return mapped
        return None

    def recommend(
        self,
        keam_rank: int,
        courses: List[str],
        types: List[str],
        category: str = "general",
        top_n: int = 5
    ):
        # 1. Normalize Category
        category_code = self.normalize_category(category)

        # 2. Normalize and order Courses
        valid_courses = []
        for c in courses:
            norm_c = self.normalize_branch(c)
            if norm_c and norm_c not in valid_courses:
                valid_courses.append(norm_c)

        if not valid_courses:
            valid_courses = ['CS', 'AD', 'EC', 'ME', 'EE', 'CY', 'AH', 'CE']

        # 3. Normalize and order Types
        ordered_types = []
        if types:
            for t in types:
                norm_t = self.normalize_type(t)
                if norm_t and norm_t not in ordered_types:
                    ordered_types.append(norm_t)

        if ordered_types:
            eligible_colleges = self.colleges_df[self.colleges_df['college_type'].isin(ordered_types)]
        else:
            eligible_colleges = self.colleges_df
            ordered_types = ['government', 'autonomous', 'private']

        candidates = []

        # 4. Process preferences
        for course_priority_idx, course_code in enumerate(valid_courses):
            # Priority decay for courses (1.0 for 1st, 0.9 for 2nd, etc.)
            course_weight = max(0.60, 1.0 - (course_priority_idx * 0.10))

            for _, college in eligible_colleges.iterrows():
                col_code = college['college_code']
                col_type = college['college_type']

                # Type priority weight (1.0 for 1st type preference, 0.85 for 2nd, etc.)
                type_priority_idx = ordered_types.index(col_type) if col_type in ordered_types else len(ordered_types)
                type_weight = max(0.70, 1.0 - (type_priority_idx * 0.15))

                cat_key = f"{col_code}__{course_code}__{category_code}"
                overall_key = f"{col_code}__{course_code}"

                stats = None
                used_reservation = False

                if cat_key in self.cat_stats:
                    stats = self.cat_stats[cat_key]
                    used_reservation = True
                elif overall_key in self.overall_stats:
                    stats = self.overall_stats[overall_key]
                    used_reservation = False
                else:
                    continue

                opening_rank = stats['opening_rank']
                closing_rank = stats['closing_rank']
                # Closing rank is the historical feasibility boundary. Keep a
                # limited aspirational band, but never rank an ineligible row.
                if keam_rank > closing_rank * 1.30:
                    continue

                rank_ratio = keam_rank / max(1, closing_rank)
                if keam_rank <= opening_rank:
                    admission_prob = 0.98
                    fit_tier = "Safe"
                elif keam_rank <= closing_rank:
                    admission_prob = 0.55 + 0.43 * (1.0 - rank_ratio)
                    fit_tier = "Safe" if admission_prob >= 0.80 else "Match"
                else:
                    admission_prob = 0.20 + 0.34 * (
                        ((closing_rank * 1.30) - keam_rank) / max(1, closing_rank * 0.30)
                    )
                    fit_tier = "Dream"

                pass_pct = float(college['pass_percentage']) if pd.notnull(college['pass_percentage']) else 60.0
                nba_bonus = 1.05 if college['nba_accredited'] else 1.00
                naac_bonus = 1.05 if college['naac_accredited'] else 1.00

                cutoff_selectivity = (
                    (self.max_closing_rank - closing_rank)
                    / max(1, self.max_closing_rank - self.min_closing_rank)
                )
                quality_score = (
                    ((pass_pct / 100.0) * 0.45)
                    + (cutoff_selectivity * 0.25)
                    + (course_weight * 0.15)
                    + (type_weight * 0.15)
                ) * nba_bonus * naac_bonus

                course_labels = {
                    'CS': 'Computer Science & Engineering (CSE)',
                    'ME': 'Mechanical Engineering (MECH)',
                    'EC': 'Electronics & Communication (EC)',
                    'CE': 'Civil Engineering (CIVIL)',
                    'EE': 'Electrical & Electronics (EEE)',
                    'AD': 'Artificial Intelligence & Data Science',
                    'CY': 'CSE (Cyber Security)',
                    'AH': 'CSE (AI & ML)'
                }

                candidates.append({
                    "college_id": int(college['id']),
                    "college_code": col_code,
                    "college_name": str(college['college_name']),
                    "college_type": str(col_type),
                    "course_code": course_code,
                    "course_name": course_labels.get(course_code, course_code),
                    "applied_category": category_code,
                    "reservation_quota_used": used_reservation,
                    "admission_probability": round(float(admission_prob), 2),
                    "recommendation_category": fit_tier,
                    "category_opening_rank": int(opening_rank),
                    "category_closing_rank": int(closing_rank),
                    "pass_percentage": round(float(pass_pct), 2),
                    "district": str(college['district']),
                    "nba_accredited": bool(college['nba_accredited']),
                    "naac_accredited": bool(college['naac_accredited']),
                    "_quality_score": float(quality_score),
                    "_admission_score": float(admission_prob)
                })

        # Feasibility and quality are separate: only eligible candidates reach
        # this point, then the strongest colleges are ranked by quality.
        candidates.sort(
            key=lambda x: (x["_quality_score"], x["_admission_score"]),
            reverse=True
        )

        # Select Top 5 recommendations with diversity (prefer unique colleges)
        seen_colleges = set()
        top_recommendations = []

        for cand in candidates:
            if cand['college_code'] not in seen_colleges:
                seen_colleges.add(cand['college_code'])
                c_copy = dict(cand)
                c_copy.pop('_quality_score', None)
                c_copy.pop('_admission_score', None)
                top_recommendations.append(c_copy)
                if len(top_recommendations) == top_n:
                    break

        if len(top_recommendations) < top_n:
            for cand in candidates:
                if len(top_recommendations) == top_n:
                    break
                c_copy = dict(cand)
                c_copy.pop('_quality_score', None)
                c_copy.pop('_admission_score', None)
                if c_copy not in top_recommendations:
                    top_recommendations.append(c_copy)

        return top_recommendations
