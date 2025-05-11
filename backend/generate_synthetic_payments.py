import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Synthetic data config
users = ['user1','user2','user3','user4','user5']
records_per_user = 50
start_date = datetime.now() - timedelta(days=30)

rows = []
for uid in users:
    for i in range(records_per_user):
        ts = start_date + timedelta(
            days=np.random.randint(0,30),
            hours=np.random.randint(0,24),
            minutes=np.random.randint(0,60)
        )
        amount = abs(np.random.normal(loc=100, scale=20))
        rows.append({
            'payment_id': f'{uid}_{i}',
            'employee_id': uid,
            'timestamp': ts.isoformat(),
            'amount': round(amount,2),
            'vendor': 'Vendor'+str(np.random.randint(1,5)),
            'method': np.random.choice(['card','transfer','wallet']),
            'category': np.random.choice(['travel','office','supplies']),
            'status': 'approved'
        })

df = pd.DataFrame(rows)
out_path = os.path.join('app','data','payments_history.csv')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
df.to_csv(out_path, index=False)
print(f'Generated synthetic payments history at {out_path}')
