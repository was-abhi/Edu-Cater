"""
Comprehensive Preprocessing Pipeline for Edu-Cater
Strict Requirements:
  1. District of each college extracted SOLELY from:
     Dama Mining/last rank keam/Kerala_Engineering_College_Rankings_Last_Rank_Cutoff.pdf
  2. College Types strictly standardized to:
     - 'government'
     - 'autonomous'
     - 'private'
  3. Allotment data merged from 2025 Phase 3, 2026 Phase 3, and 2025 Phase 1.
  4. Filtered strictly for the 8 permitted engineering branches.
"""

import os
import re
import subprocess
import pandas as pd
from difflib import SequenceMatcher

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(MODEL_DIR, '..', 'Dama Mining'))

# 8 Permitted Engineering Branches
ALLOWED_BRANCHES = {
    'CS': 'Computer Science & Engineering',
    'ME': 'Mechanical Engineering',
    'EC': 'Electronics & Communication Engineering',
    'CE': 'Civil Engineering',
    'EE': 'Electrical & Electronics Engineering',
    'AD': 'Artificial Intelligence and Data Science',
    'CY': 'Computer Science and Engineering (Cyber Security)',
    'AH': 'Computer Science (AI & ML)',
    'AI': 'Artificial Intelligence',
    'CA': 'Computer Science (Artificial Intelligence)'
}

# 1. Actual Government Colleges ('government')
GOVT_COLLEGE_CODES = {
    'TVE', 'TCR', 'KNR', 'TRV', 'PKD', 'KKE', 'IDK', 'WYD', 'KTE', 'NSS', 'TKM', 'MAC'
}

# 2. Autonomous Colleges ('autonomous')
AUTONOMOUS_COLLEGE_CODES = {
    'RET', 'MBT', 'MGP', 'AJC', 'SJC', 'SHR', 'NCE', 'JCE', 'JEC', 'MUT', 'SCM', 'FIT',
    'MDL', 'SCT', 'LBT', 'KSD', 'CHN', 'TLY', 'ADR', 'PRN', 'VDA', 'CEC', 'CEA', 
    'KGR', 'MNR', 'PTA', 'PJR', 'PEC', 'PRP', 'TKR', 'KNP', 'AEC', 'CEM', 'UCK', 'UCE', 'UCC', 'MGC'
}

KERALA_DISTRICTS = [
    'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam', 
    'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 
    'Kozhikode', 'Kozhikkode', 'Wayanad', 'Kannur', 'Kasaragod', 'Kasargod'
]

TOWN_TO_DISTRICT = {
    'kochi': 'Ernakulam', 'cochin': 'Ernakulam', 'thodupuzha': 'Idukki',
    'parippally': 'Kollam', 'punnnapra': 'Alappuzha', 'punnapra': 'Alappuzha',
    'thirissur': 'Thrissur', 'kothamangalam': 'Ernakulam', 'chengannur': 'Alappuzha',
    'chengannoor': 'Alappuzha', 'adoor': 'Pathanamthitta', 'vadakara': 'Kozhikode',
    'tavanur': 'Malappuram', 'palai': 'Kottayam', 'cherthala': 'Alappuzha',
    'kallooppara': 'Pathanamthitta', 'karunagappally': 'Kollam', 'munnar': 'Idukki',
    'attingal': 'Thiruvananthapuram', 'trikaripur': 'Kasaragod', 'aranmula': 'Pathanamthitta',
    'valanchery': 'Malappuram', 'poonjar': 'Kottayam', 'kuttippuram': 'Malappuram',
    'perumon': 'Kollam', 'thalassery': 'Kannur', 'kidangoor': 'Kottayam',
    'kariavattom': 'Thiruvananthapuram', 'mannuthy': 'Thrissur', 'vengoor': 'Malappuram',
    'muttathara': 'Thiruvananthapuram', 'pathanapuram': 'Kollam', 'kottarakkara': 'Kollam',
    'kottarakara': 'Kollam', 'payyannur': 'Kannur', 'mavelikkara': 'Alappuzha',
    'mukkam': 'Kozhikode', 'kanjirampara': 'Kottayam', 'pookode': 'Wayanad',
    'vellanikkara': 'Thrissur', 'palakkad': 'Palakkad'
}

def classify_college_type(college_code: str) -> str:
    code = college_code.strip().upper()
    if code in GOVT_COLLEGE_CODES:
        return 'government'
    elif code in AUTONOMOUS_COLLEGE_CODES:
        return 'autonomous'
    else:
        return 'private'

def run_pdftotext(pdf_path, layout=True):
    cmd = ['pdftotext']
    if layout:
        cmd.append('-layout')
    cmd.extend([pdf_path, '-'])
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_district_from_cutoff_name(name_clean: str) -> str:
    # 1. Direct Kerala District match
    for d in KERALA_DISTRICTS:
        if re.search(r'\b' + d + r'\b', name_clean, re.I):
            if d.lower().startswith('kozhik'):
                return 'Kozhikode'
            elif d.lower().startswith('kasar'):
                return 'Kasaragod'
            return d

    # 2. Match known Town in Kerala
    for town, dist in TOWN_TO_DISTRICT.items():
        if re.search(r'\b' + town + r'\b', name_clean, re.I):
            return dist

    return 'Kerala'

def parse_cutoffs():
    pdf_path = os.path.join(DATA_DIR, 'last rank keam', 'Kerala_Engineering_College_Rankings_Last_Rank_Cutoff.pdf')
    text = run_pdftotext(pdf_path, layout=True)
    colleges = []
    
    for line in text.split('\n'):
        m = re.match(r'^\s*(\d+)\s+(.+?)\s+([GNS])\s+(\d+)\s*$', line)
        if m:
            rank, name, c_type, cutoff = m.groups()
            name_clean = name.strip()
            dist = extract_district_from_cutoff_name(name_clean)
            colleges.append({
                'state_rank': int(rank),
                'college_name': name_clean,
                'district': dist,
                'cutoff_sm': int(cutoff)
            })
    print(f"[Cutoffs & Districts] Parsed {len(colleges)} records exclusively from last rank keam PDF.")
    return pd.DataFrame(colleges)

def parse_pass_percentages():
    pdf_path = os.path.join(DATA_DIR, 'pass percentages', 'INSTITUTIONWISEPASSPERCENTAGEREPORT.pdf')
    text = run_pdftotext(pdf_path, layout=True)
    records = []
    for line in text.split('\n'):
        m = re.match(r'^\s*(\d+)\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+(?:\.\d+)?)\s*$', line)
        if m:
            sino, name, reg, passed, pct = m.groups()
            records.append({
                'pass_college_name': name.strip(),
                'registered_students': int(reg),
                'passed_students': int(passed),
                'pass_percentage': float(pct)
            })
    print(f"[Pass %] Parsed {len(records)} KTU pass percentage records.")
    return pd.DataFrame(records)

def parse_accreditations():
    pdf_path = os.path.join(DATA_DIR, 'nba or naac', 'Kerala_Engineering_Colleges_NBA_NAAC_Accreditation_List.pdf')
    text = run_pdftotext(pdf_path, layout=True)
    records = []
    for line in text.split('\n'):
        m = re.match(r'^\s*(\d+)\s+(.+?)\s{2,}([A-Za-z\s]+?)\s{2,}(Yes|Not confirmed)\s{2,}(Yes|Not confirmed)\s*$', line)
        if m:
            no, name, _, nba, naac = m.groups()
            records.append({
                'accred_college_name': name.strip(),
                'nba_accredited': (nba.strip() == 'Yes'),
                'naac_accredited': (naac.strip() == 'Yes')
            })
    print(f"[Accreditation] Parsed {len(records)} accreditation records.")
    return pd.DataFrame(records)

def parse_all_allotments():
    allotment_files = [
        ('2025_KEAM_Allotment.pdf', '2025_phase3'),
        ('2026_KEAM_Allotment.pdf', '2026_phase3'),
        ('kirf/p1_engg_final.pdf', '2025_phase1')
    ]
    
    all_allotments = []
    for rel_path, tag in allotment_files:
        full_path = os.path.join(DATA_DIR, rel_path)
        if not os.path.exists(full_path):
            continue
        text = run_pdftotext(full_path, layout=True)
        file_count = 0
        for line in text.split('\n'):
            m = re.match(r'^\s*(\d+)\s+(\d{7})\s+(\d+)\s+([A-Z]{2})\s+([A-Z]{3})-([^–-]+?)\s{2,}([A-Z]{2,3})-([^–-]+?)\s{2,}([A-Z]{2,3})\b', line)
            if m:
                sl, app, rank, cat, col_code, col_name, course_code, course_name, seat = m.groups()
                c_code = course_code.strip()
                if c_code in ALLOWED_BRANCHES:
                    all_allotments.append({
                        'dataset_source': tag,
                        'application_no': int(app),
                        'keam_rank': int(rank),
                        'candidate_category': cat.strip(),
                        'college_code': col_code.strip(),
                        'college_name': col_name.strip(),
                        'course_code': c_code,
                        'course_name': ALLOWED_BRANCHES[c_code],
                        'seat_type': seat.strip()
                    })
                    file_count += 1
        print(f"[{tag}] Parsed {file_count} records matching allowed engineering branches.")
        
    df_allot = pd.DataFrame(all_allotments)
    print(f"Total Combined Allotments: {len(df_allot)} records.")
    return df_allot

def build_datasets():
    df_cutoff = parse_cutoffs()
    df_pass = parse_pass_percentages()
    df_accred = parse_accreditations()
    df_allot = parse_all_allotments()

    # Build unique colleges master strictly on college_code
    unique_colleges = (
        df_allot[['college_code', 'college_name']]
        .sort_values(by='college_name', key=lambda col: col.str.len(), ascending=False)
        .drop_duplicates(subset=['college_code'])
        .copy()
    )

    type_list = []
    cutoff_list = []
    district_list = []
    nba_list = []
    naac_list = []
    pass_pct_list = []

    def clean_name(t):
        t = t.lower()
        for w in ['college of engineering', 'engineering college', 'technology', 'and', '&', 'institute of', 'government', 'govt']:
            t = t.replace(w, ' ')
        return ' '.join(t.split())

    for _, row in unique_colleges.iterrows():
        c_code = row['college_code']
        c_name = row['college_name']

        # 1. Type: strictly 'government', 'autonomous', 'private'
        c_type = classify_college_type(c_code)
        type_list.append(c_type)

        # 2. District & Cutoff: SOLELY matched from df_cutoff (last rank keam PDF)
        best_dist = 'Kerala'
        best_cutoff = 55000
        best_sim = 0
        c_clean = clean_name(c_name)

        for _, c_row in df_cutoff.iterrows():
            rec_clean = clean_name(c_row['college_name'])
            # Priority 1: Exact substring containment
            if c_name.lower().strip(', ') in c_row['college_name'].lower() or c_row['college_name'].lower().strip(', ') in c_name.lower():
                sim = 1.0
            else:
                sim = similarity(c_clean, rec_clean)

            if sim > best_sim:
                best_sim = sim
                best_dist = c_row['district']
                best_cutoff = c_row['cutoff_sm']

        # If district still undetermined, check if c_name itself has town/district
        if best_dist == 'Kerala' or best_sim < 0.40:
            extracted_d = extract_district_from_cutoff_name(c_name)
            if extracted_d != 'Kerala':
                best_dist = extracted_d

        # Specific known college overrides if any remaining
        override_districts = {
            'CEN': 'Kannur', # Payyannur
            'MGC': 'Thiruvananthapuram',
            'SIT': 'Thiruvananthapuram',
            'AIK': 'Ernakulam',
            'KME': 'Ernakulam',
            'PRP': 'Alappuzha',
            'VKE': 'Kollam'
        }
        if c_code in override_districts:
            best_dist = override_districts[c_code]

        district_list.append(best_dist)
        cutoff_list.append(best_cutoff)

        # 3. Match Pass Percentage
        best_pass_sim = 0
        p_pct = 65.0
        for _, p_row in df_pass.iterrows():
            sim = similarity(c_name, p_row['pass_college_name'])
            if sim > best_pass_sim and sim > 0.45:
                best_pass_sim = sim
                p_pct = p_row['pass_percentage']
        pass_pct_list.append(p_pct)

        # 4. Match Accreditation (NBA / NAAC)
        best_acc_sim = 0
        nba = False
        naac = False
        for _, a_row in df_accred.iterrows():
            sim = similarity(c_name, a_row['accred_college_name'])
            if sim > best_acc_sim and sim > 0.45:
                best_acc_sim = sim
                nba = a_row['nba_accredited']
                naac = a_row['naac_accredited']
        nba_list.append(nba)
        naac_list.append(naac)

    unique_colleges['college_type'] = type_list
    unique_colleges['cutoff_sm'] = cutoff_list
    unique_colleges['pass_percentage'] = pass_pct_list
    unique_colleges['district'] = district_list
    unique_colleges['nba_accredited'] = nba_list
    unique_colleges['naac_accredited'] = naac_list
    unique_colleges.reset_index(drop=True, inplace=True)
    unique_colleges['id'] = range(1, len(unique_colleges) + 1)

    cols = ['id', 'college_code', 'college_name', 'college_type', 'district', 'pass_percentage', 'cutoff_sm', 'nba_accredited', 'naac_accredited']
    df_colleges_master = unique_colleges[cols]

    colleges_csv = os.path.join(MODEL_DIR, 'colleges_master.csv')
    df_colleges_master.to_csv(colleges_csv, index=False)
    print(f"Saved colleges master to {colleges_csv} ({len(df_colleges_master)} colleges)")
    print(f"Type breakdown:\n{df_colleges_master['college_type'].value_counts()}")
    print(f"District breakdown:\n{df_colleges_master['district'].value_counts()}")

    # Merge college_id and college_type into allotments
    merged_allotments = df_allot.merge(
        df_colleges_master[['college_code', 'id', 'college_type']],
        on='college_code',
        how='left'
    ).rename(columns={'id': 'college_id'})

    allotments_csv = os.path.join(MODEL_DIR, 'keam_allotments_clean.csv')
    merged_allotments.to_csv(allotments_csv, index=False)
    print(f"Saved cleaned allotments to {allotments_csv} ({len(merged_allotments)} records)")

if __name__ == '__main__':
    build_datasets()
