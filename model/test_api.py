import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))

import json
from model.recommender import CollegeRecommender

def run_tests():
    print("Initializing CollegeRecommender...")
    rec = CollegeRecommender()

    test_cases = [
        {
            "desc": "High rank student (Rank 1200, General) seeking CS, EC in government colleges",
            "keam_rank": 1200,
            "category": "general",
            "courses": ["CS", "EC"],
            "types": ["government"]
        },
        {
            "desc": "Moderate rank student (Rank 4500, BX) seeking CS, CY in government/autonomous",
            "keam_rank": 4500,
            "category": "bx",
            "courses": ["CS", "CY"],
            "types": ["government", "autonomous"]
        },
        {
            "desc": "Rank 15000 student (OBC) seeking ME, CE in autonomous/private",
            "keam_rank": 15000,
            "category": "obc",
            "courses": ["ME", "CE"],
            "types": ["autonomous", "private"]
        },
        {
            "desc": "Rank 32000 student (SC) seeking CS, AD in private colleges",
            "keam_rank": 32000,
            "category": "sc",
            "courses": ["CS", "AD"],
            "types": ["private"]
        }
    ]

    for tc in test_cases:
        print(f"\n==========================================")
        print(f"TEST: {tc['desc']}")
        print(f"Inputs: Rank={tc['keam_rank']}, Category={tc['category']}, Courses={tc['courses']}, Types={tc['types']}")
        print(f"==========================================")
        results = rec.recommend(
            keam_rank=tc['keam_rank'],
            courses=tc['courses'],
            types=tc['types'],
            category=tc['category'],
            top_n=5
        )
        print(f"Returned {len(results)} recommendations:")
        for idx, r in enumerate(results, 1):
            print(f"  {idx}. [{r['recommendation_category']}] ID:{r['college_id']} ({r['college_code']}) {r['college_name'][:35]} | Branch: {r['course_code']} | Type: {r['college_type']} | Dist: {r['district']} | Prob: {r['admission_probability']}")

    print("\nAll model recommendation test cases executed successfully!")

if __name__ == '__main__':
    run_tests()
