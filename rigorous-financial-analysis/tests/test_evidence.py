import unittest
from datetime import date
from financial_skill.evidence import FactEvidence, validate_evidence

class EvidenceTests(unittest.TestCase):
    def test_invalid_unattributed_company(self):
        with self.assertRaisesRegex(ValueError,'Missing source evidence'):
            validate_evidence({'synthetic': False},date(2026,1,1))

    def test_synthetic_can_run_offline(self):
        self.assertEqual(validate_evidence({'synthetic':True},date(2026,1,1)),())

    def test_bad_publication_date(self):
        with self.assertRaises(ValueError):
            FactEvidence('revenue','https://example.org/filing',date(2025,1,1),date(2026,1,1),'filing')

    def test_lookahead(self):
        data={'evidence':[dict(fact_key='starting_revenue_millions',source_url='https://example.org/report',
                               published_on='2026-02-01',period_end='2025-12-31',source_kind='filing')]}
        with self.assertRaisesRegex(ValueError,'Lookahead'):
            validate_evidence(data,date(2026,1,1))
