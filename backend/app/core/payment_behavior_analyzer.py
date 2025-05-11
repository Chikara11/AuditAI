# File: backend/app/core/payment_behavior_analyzer.py
import pandas as pd
from sklearn.ensemble import IsolationForest

class PaymentBehaviorAnalyzer:
    def __init__(self, history_path: str = None):
        # Load historical payments
        self.history_path = history_path or 'app/data/payments_history.csv'
        self.history = pd.read_csv(self.history_path, parse_dates=['timestamp'])
        # Compute per-user stats
        self.user_stats = self._compute_user_stats()
        # IsolationForest for amount anomalies (trained on global history)
        self.iforest = IsolationForest(contamination=0.01, random_state=42)
        self.iforest.fit(self.history[['amount']])

    def _compute_user_stats(self):
        df = self.history.copy()
        df['date'] = df['timestamp'].dt.date
        stats = {}
        for uid, group in df.groupby('employee_id'):
            avg_amt = group['amount'].mean()
            std_amt = group['amount'].std(ddof=0)
            daily_counts = group.groupby('date').size()
            avg_count = daily_counts.mean()
            std_count = daily_counts.std(ddof=0)
            stats[uid] = {
                'avg_amount': avg_amt,
                'std_amount': std_amt,
                'avg_daily_count': avg_count,
                'std_daily_count': std_count
            }
        return stats

    def detect_unusual(self, payment: dict):
        """
        payment: dict with keys employee_id, amount, timestamp
        Returns anomaly info or None
        """
        uid = payment['employee_id']
        amt = payment['amount']
        ts = pd.to_datetime(payment['timestamp'])
        stats = self.user_stats.get(uid)
        if not stats:
            return {'anomaly_type': 'UnknownUser', 'message': 'No history for user'}

        # Amount anomaly
        threshold_amt = stats['avg_amount'] + 3 * stats['std_amount']
        if stats['std_amount'] and amt > threshold_amt:
            return {
                'anomaly_type': 'AmountOutlier',
                'message': f'Amount {amt} exceeds threshold {threshold_amt:.2f}'
            }

        # Frequency anomaly: count existing in same day
        date = ts.date()
        existing = self.history[
            (self.history['employee_id'] == uid) &
            (self.history['timestamp'].dt.date == date)
        ]
        count = len(existing) + 1  # include this
        threshold_count = stats['avg_daily_count'] + 3 * stats['std_daily_count']
        if stats['std_daily_count'] and count > threshold_count:
            return {
                'anomaly_type': 'FrequencySpike',
                'message': f'Day count {count} exceeds threshold {threshold_count:.2f}'
            }

        return None