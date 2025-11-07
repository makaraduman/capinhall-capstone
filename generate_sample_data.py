"""
Generate synthetic sample data for Chapin Hall capstone project
This creates realistic-looking (but fake) child welfare data
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
        ['Black', 'White', 'Hispanic', 'Asian', 'Other'], 
        N_CHILDREN, 
        p=[0.35, 0.30, 0.25, 0.05, 0.05]
    ),
    'ethnicity': np.random.choice(['Hispanic', 'Non-Hispanic'], N_CHILDREN, p=[0.25, 0.75]),
    'initial_county': np.random.choice(
        ['Cook', 'DuPage', 'Lake', 'Will', 'Kane'], 
        N_CHILDREN, 
        p=[0.40, 0.20, 0.15, 0.15, 0.10]
    )
})

children.to_csv('data/raw/children.csv', index=False)
print(f"✓ Created children.csv ({len(children)} rows)")

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
    'case_type': np.random.choice(
        ['investigation', 'assessment', 'services'], 
        N_CASES, 
        p=[0.50, 0.30, 0.20]
    ),
    'intake_county': np.random.choice(
        ['Cook', 'DuPage', 'Lake', 'Will', 'Kane'], 
        N_CASES, 
        p=[0.40, 0.20, 0.15, 0.15, 0.10]
    ),
    'case_status': np.random.choice(
        ['open', 'closed'], 
        N_CASES, 
        p=[0.30, 0.70]
    )
})

# Add closure dates for closed cases
cases['closure_date'] = cases.apply(
    lambda row: (
        pd.to_datetime(row['referral_date']) + timedelta(days=random.randint(30, 365))
    ).strftime('%Y-%m-%d') if row['case_status'] == 'closed' else None,
    axis=1
)

cases.to_csv('data/raw/cases.csv', index=False)
print(f"✓ Created cases.csv ({len(cases)} rows)")

# ============================================
# 3. Case-Child linking
# ============================================
print("Generating case-child links...")

case_child_links = []
for case_id in range(1, N_CASES + 1):
    # Each case has 1-3 children
    n_children_in_case = random.randint(1, 3)
    child_ids = random.sample(range(1, N_CHILDREN + 1), n_children_in_case)
    
    for child_id in child_ids:
        case_child_links.append({
            'case_id': case_id,
            'child_id': child_id,
            'role_in_case': random.choice(['victim', 'sibling', 'witness'])
        })

case_child = pd.DataFrame(case_child_links)
case_child.to_csv('data/raw/case_child.csv', index=False)
print(f"✓ Created case_child.csv ({len(case_child)} rows)")

# ============================================
# 4. Episodes
# ============================================
print("Generating episodes data...")

episodes_list = []
for ep_id in range(1, N_EPISODES + 1):
    child_id = random.randint(1, N_CHILDREN)
    entry_date = datetime.now() - timedelta(days=random.randint(30, 1460))
    
    # 70% of episodes are still active
    is_active = random.random() < 0.70
    exit_date = None if is_active else (entry_date + timedelta(days=random.randint(30, 1095)))
    
    # Calculate age at entry
    child_dob = pd.to_datetime(children[children['child_id'] == child_id]['date_of_birth'].values[0])
    age_at_entry_days = (entry_date - child_dob).days
    
    episodes_list.append({
        'episode_id': ep_id,
        'child_id': child_id,
        'entry_date': entry_date.strftime('%Y-%m-%d'),
        'exit_date': exit_date.strftime('%Y-%m-%d') if exit_date else None,
        'removal_reason': random.choice([
            'neglect', 'physical_abuse', 'sexual_abuse', 
            'parental_substance_abuse', 'domestic_violence', 'abandonment'
        ]),
        'entry_age_days': age_at_entry_days,
        'episode_status': 'active' if is_active else 'closed',
        'goal': random.choice([
            'reunification', 'adoption', 'guardianship', 
            'independent_living', 'relative_placement'
        ])
    })

episodes = pd.DataFrame(episodes_list)
episodes.to_csv('data/raw/episodes.csv', index=False)
print(f"✓ Created episodes.csv ({len(episodes)} rows)")

# ============================================
# 5. Placements
# ============================================
print("Generating placements data...")

placements_list = []
placement_id = 1

for _, episode in episodes.iterrows():
    # Each episode has 1-5 placements
    n_placements = random.randint(1, 5)
    
    current_date = pd.to_datetime(episode['entry_date'])
    episode_end = pd.to_datetime(episode['exit_date']) if episode['exit_date'] else datetime.now()
    
    for i in range(n_placements):
        placement_start = current_date
        
        # Last placement ends with episode
        if i == n_placements - 1:
            placement_end = episode_end if episode['episode_status'] == 'closed' else None
        else:
            days_in_placement = random.randint(30, 365)
            placement_end = placement_start + timedelta(days=days_in_placement)
            current_date = placement_end
        
        placements_list.append({
            'placement_id': placement_id,
            'episode_id': episode['episode_id'],
            'placement_start': placement_start.strftime('%Y-%m-%d'),
            'placement_end': placement_end.strftime('%Y-%m-%d') if placement_end and isinstance(placement_end, datetime) else None,
            'placement_type': random.choice([
                'foster_home', 'kinship', 'group_home', 
                'residential', 'therapeutic_foster_care', 'independent_living'
            ]),
            'placement_county': random.choice(['Cook', 'DuPage', 'Lake', 'Will', 'Kane']),
            'provider_id': f'PROV-{random.randint(1000, 9999)}'
        })
        placement_id += 1

placements = pd.DataFrame(placements_list)
placements.to_csv('data/raw/placements.csv', index=False)
print(f"✓ Created placements.csv ({len(placements)} rows)")

# ============================================
# 6. Allegations
# ============================================
print("Generating allegations data...")

allegations_list = []
for _, link in case_child.iterrows():
    # Each case-child link has 1-2 allegations
    n_allegations = random.randint(1, 2)
    
    case_date = pd.to_datetime(
        cases[cases['case_id'] == link['case_id']]['referral_date'].values[0]
    )
    
    for i in range(n_allegations):
        allegations_list.append({
            'case_id': link['case_id'],
            'child_id': link['child_id'],
            'allegation_type': random.choice([
                'neglect', 'physical_abuse', 'sexual_abuse',
                'emotional_abuse', 'medical_neglect', 'educational_neglect'
            ]),
            'allegation_date': case_date.strftime('%Y-%m-%d'),
            'finding': np.random.choice(['indicated', 'unfounded', 'pending'], p=[0.30, 0.50, 0.20])
        })

allegations = pd.DataFrame(allegations_list)
allegations.to_csv('data/raw/allegations.csv', index=False)
print(f"✓ Created allegations.csv ({len(allegations)} rows)")

# ============================================
# 7. Notes
# ============================================
print("Generating notes data...")

note_templates = [
    "Initial assessment completed. Child appears safe in current placement.",
    "Monthly visit conducted. Child is adjusting well to school.",
    "Court hearing scheduled for next month regarding permanency.",
    "Parent-child visit supervised. Positive interaction observed.",
    "Therapeutic services initiated. Child responding well to counseling.",
    "Safety concerns noted during home visit. Follow-up required.",
    "Child expressed desire to maintain contact with siblings.",
    "Educational needs assessment conducted. IEP recommended.",
    "Medical examination completed. All immunizations up to date.",
    "Case review meeting held with team. Progress toward goals noted."
]

notes_list = []
for episode_id in range(1, N_EPISODES + 1):
    # 3-10 notes per episode
    n_notes = random.randint(3, 10)
    episode_data = episodes[episodes['episode_id'] == episode_id].iloc[0]
    
    start_date = pd.to_datetime(episode_data['entry_date'])
    end_date = pd.to_datetime(episode_data['exit_date']) if episode_data['exit_date'] else datetime.now()
    
    for i in range(n_notes):
        days_offset = random.randint(0, (end_date - start_date).days)
        note_date = start_date + timedelta(days=days_offset)
        
        notes_list.append({
'case_id': random.choice(case_child[case_child['child_id'] == episode_data['child_id']]['case_id'].values) \
                if len(case_child[case_child['child_id'] == episode_data['child_id']]) > 0 else None,            
            'child_id': episode_data['child_id'],
            'episode_id': episode_id,
            'note_date': note_date.strftime('%Y-%m-%d'),
            'note_type': random.choice(['visit', 'assessment', 'court', 'service', 'review']),
            'note_text': random.choice(note_templates),
            'author': random.choice(['J. Smith', 'M. Johnson', 'A. Williams', 'K. Brown', 'R. Davis'])
        })

notes = pd.DataFrame(notes_list)
notes.to_csv('data/raw/notes.csv', index=False)
print(f"✓ Created notes.csv ({len(notes)} rows)")

# ============================================
# Summary
# ============================================
print("\n" + "="*50)
print("SAMPLE DATA GENERATION COMPLETE")
print("="*50)
print(f"Children:     {len(children):>6} rows")
print(f"Cases:        {len(cases):>6} rows")
print(f"Case-Child:   {len(case_child):>6} rows")
print(f"Episodes:     {len(episodes):>6} rows")
print(f"Placements:   {len(placements):>6} rows")
print(f"Allegations:  {len(allegations):>6} rows")
print(f"Notes:        {len(notes):>6} rows")
print("="*50)
print("\nAll CSV files created in data/raw/")
print("Ready to load into PostgreSQL!")
