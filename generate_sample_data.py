"""
Generate synthetic sample data for Chapin Hall capstone project
- Ensures all missing values are written as 'NULL' for PostgreSQL COPY command.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
N_CHILDREN = 500
N_CASES = 300
N_EPISODES = 400

# Create data directory if it doesn't exist
os.makedirs('data/raw', exist_ok=True)

print("Generating sample data...")

# Helper function to save CSV with correct NULL handling
def save_data(df, filename):
    filepath = os.path.join('data/raw', filename)
    # Replace all NaN/NaT/None with the string 'NULL'
    df_output = df.copy()
    for col in df_output.columns:
        # Convert integers to int (avoiding .0), then handle NULLs
        if df_output[col].dtype in ['float64', 'float32']:
            # Check if this should be an integer column (has only whole numbers or NaN)
            non_null_values = df_output[col].dropna()
            if len(non_null_values) > 0 and all(non_null_values == non_null_values.astype(int)):
                # Convert to Int64 (nullable integer type)
                df_output[col] = df_output[col].astype('Int64')
        
        # Now replace NaN/None with 'NULL'
        df_output[col] = df_output[col].apply(lambda x: 'NULL' if pd.isna(x) or x is None else x)
    
    df_output.to_csv(filepath, index=False)
    print(f"✓ Created {filename} ({len(df)} rows)")

# ============================================
# 1. Children
# ============================================
print("Generating children data...")
children = pd.DataFrame({
    'child_id': range(1, N_CHILDREN + 1),
    'date_of_birth': [
        (datetime.now() - timedelta(days=random.randint(365, 365*18))).strftime('%Y-%m-%d')
        for _ in range(N_CHILDREN)
    ],
    'gender': np.random.choice(['Male', 'Female'], N_CHILDREN, p=[0.51, 0.49]),
    'race': np.random.choice(
        ['Black', 'White', 'Hispanic', 'Asian', 'Other'], N_CHILDREN, p=[0.35, 0.30, 0.25, 0.05, 0.05]
    ),
    'ethnicity': np.random.choice(['Hispanic', 'Non-Hispanic'], N_CHILDREN, p=[0.25, 0.75]),
    'initial_county': np.random.choice(
        ['Cook', 'DuPage', 'Lake', 'Will', 'Kane'], N_CHILDREN, p=[0.40, 0.20, 0.15, 0.15, 0.10]
    )
})
save_data(children, 'children.csv')

# ============================================
# 2. Cases
# ============================================
print("Generating cases data...")
cases = pd.DataFrame({
    'case_id': range(1, N_CASES + 1),
    'case_number': [f'CASE-{i:06d}' for i in range(1, N_CASES + 1)],
    'referral_date': [
        (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d')
        for _ in range(N_CASES)
    ],
    'case_type': np.random.choice(['investigation', 'assessment', 'services'], N_CASES, p=[0.50, 0.30, 0.20]),
    'intake_county': np.random.choice(['Cook', 'DuPage', 'Lake', 'Will', 'Kane'], N_CASES, p=[0.40, 0.20, 0.15, 0.15, 0.10]),
    'case_status': np.random.choice(['open', 'closed'], N_CASES, p=[0.30, 0.70])
})
# Add closure_date - None for open cases
cases['closure_date'] = cases.apply(
    lambda row: (
        pd.to_datetime(row['referral_date']) + timedelta(days=random.randint(30, 365))
    ).strftime('%Y-%m-%d') if row['case_status'] == 'closed' else None,
    axis=1
)
save_data(cases, 'cases.csv')

# ============================================
# 3. Case-Child linking
# ============================================
print("Generating case-child links...")
case_child_links = []
for case_id in range(1, N_CASES + 1):
    n_children_in_case = random.randint(1, 3)
    child_ids = random.sample(range(1, N_CHILDREN + 1), n_children_in_case)
    for child_id in child_ids:
        case_child_links.append({
            'case_id': case_id,
            'child_id': child_id,
            'role_in_case': random.choice(['victim', 'sibling', 'witness'])
        })
case_child = pd.DataFrame(case_child_links)
save_data(case_child, 'case_child.csv')

# ============================================
# 4. Episodes
# ============================================
print("Generating episodes data...")
episodes_list = []
for ep_id in range(1, N_EPISODES + 1):
    child_id = random.randint(1, N_CHILDREN)
    entry_date = datetime.now() - timedelta(days=random.randint(30, 1460))
    is_active = random.random() < 0.70
    exit_date = None if is_active else (entry_date + timedelta(days=random.randint(30, 1095)))
    child_dob = pd.to_datetime(children[children['child_id'] == child_id]['date_of_birth'].values[0])
    age_at_entry_days = (entry_date - child_dob).days
    
    episodes_list.append({
        'episode_id': ep_id,
        'child_id': child_id,
        'entry_date': entry_date.strftime('%Y-%m-%d'),
        'exit_date': exit_date.strftime('%Y-%m-%d') if exit_date else None, 
        'removal_reason': random.choice(['neglect', 'physical_abuse', 'sexual_abuse', 'parental_substance_abuse', 'domestic_violence', 'abandonment']),
        'entry_age_days': age_at_entry_days,
        'episode_status': 'active' if is_active else 'closed',
        'goal': random.choice(['reunification', 'adoption', 'guardianship', 'independent_living', 'relative_placement'])
    })
episodes = pd.DataFrame(episodes_list)
save_data(episodes, 'episodes.csv')

# ============================================
# 5. Placements
# ============================================
print("Generating placements data...")
placements_list = []
placement_id = 1
for _, episode in episodes.iterrows():
    n_placements = random.randint(1, 5)
    current_date = pd.to_datetime(episode['entry_date'])
    episode_end = pd.to_datetime(episode['exit_date']) if pd.notnull(episode['exit_date']) else datetime.now()
    
    for i in range(n_placements):
        placement_start = current_date
        
        if i == n_placements - 1:
            placement_end = episode_end if episode['episode_status'] == 'closed' else None
        else:
            days_in_placement = random.randint(30, 365)
            placement_end = placement_start + timedelta(days=days_in_placement)
            current_date = placement_end
        
        # Format date or use None
        end_val = placement_end.strftime('%Y-%m-%d') if placement_end else None
        
        placements_list.append({
            'placement_id': placement_id,
            'episode_id': episode['episode_id'],
            'placement_start': placement_start.strftime('%Y-%m-%d'),
            'placement_end': end_val,
            'placement_type': random.choice(['foster_home', 'kinship', 'group_home', 'residential', 'therapeutic_foster_care', 'independent_living']),
            'placement_county': random.choice(['Cook', 'DuPage', 'Lake', 'Will', 'Kane']),
            'provider_id': f'PROV-{random.randint(1000, 9999)}'
        })
        placement_id += 1
placements = pd.DataFrame(placements_list)
save_data(placements, 'placements.csv')

# ============================================
# 6. Allegations
# ============================================
print("Generating allegations data...")
allegations_list = []
for _, link in case_child.iterrows():
    n_allegations = random.randint(1, 2)
    case_date = pd.to_datetime(
        cases[cases['case_id'] == link['case_id']]['referral_date'].values[0]
    )
    for i in range(n_allegations):
        allegations_list.append({
            'case_id': link['case_id'],
            'child_id': link['child_id'],
            'allegation_type': random.choice(['neglect', 'physical_abuse', 'sexual_abuse', 'emotional_abuse', 'medical_neglect', 'educational_neglect']),
            'allegation_date': case_date.strftime('%Y-%m-%d'),
            'finding': np.random.choice(['indicated', 'unfounded', 'pending'], p=[0.30, 0.50, 0.20])
        })
allegations = pd.DataFrame(allegations_list)
save_data(allegations, 'allegations.csv')

# ============================================
# 7. Notes
# ============================================
print("Generating notes data...")
note_templates = [
    "Initial assessment completed.", "Monthly visit conducted.", "Court hearing scheduled.",
    "Parent-child visit supervised.", "Therapeutic services initiated.", "Safety concerns noted.",
    "Child expressed desire to maintain contact with siblings.", "Educational needs assessment.",
    "Medical examination completed.", "Case review meeting held."
]
notes_list = []
for episode_id in range(1, N_EPISODES + 1):
    n_notes = random.randint(3, 10)
    episode_data = episodes[episodes['episode_id'] == episode_id].iloc[0]
    start_date = pd.to_datetime(episode_data['entry_date'])
    end_date = pd.to_datetime(episode_data['exit_date']) if pd.notnull(episode_data['exit_date']) else datetime.now()
    
    for i in range(n_notes):
        days_offset = random.randint(0, (end_date - start_date).days)
        note_date = start_date + timedelta(days=days_offset)
        
        # Find a case_id, use None if not found
        matching_cases = case_child[case_child['child_id'] == episode_data['child_id']]['case_id'].values
        case_id_val = random.choice(matching_cases) if len(matching_cases) > 0 else None
        
        notes_list.append({
            'case_id': case_id_val,            
            'child_id': episode_data['child_id'],
            'episode_id': episode_id,
            'note_date': note_date.strftime('%Y-%m-%d'),
            'note_type': random.choice(['visit', 'assessment', 'court', 'service', 'review']),
            'note_text': random.choice(note_templates),
            'author': random.choice(['J. Smith', 'M. Johnson', 'A. Williams', 'K. Brown', 'R. Davis'])
        })
notes = pd.DataFrame(notes_list)
save_data(notes, 'notes.csv')

# ============================================
# Summary
# ============================================
print("\n" + "="*50)
print("SAMPLE DATA GENERATION COMPLETE")
print("="*50)
print("Ready to load into PostgreSQL!")