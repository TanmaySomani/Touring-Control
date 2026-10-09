import unittest
from pipeline import forecast, month_add

class ForecastTests(unittest.TestCase):
 def test_prediction_does_not_read_target_or_future(self):
  s={month_add('2023-01',i):100+i for i in range(30)}
  train={k:v for k,v in s.items() if k<'2025-01'}
  expected=forecast(train,'2025-01')
  s['2025-01']=999999999
  self.assertEqual(forecast(s,'2025-01'),expected)
 def test_missing_seasonal_month_raises(self):
  with self.assertRaises(ValueError):forecast({'2024-02':100},'2025-01')
 def test_seasonal_baseline_and_year_boundary(self):
  self.assertEqual(month_add('2026-12',1),'2027-01')
  self.assertEqual(forecast({'2024-01':100},'2025-01',False),100)

if __name__=='__main__':unittest.main()
