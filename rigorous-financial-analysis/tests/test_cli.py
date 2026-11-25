import json
import tempfile
import unittest
from pathlib import Path

from financial_skill.cli import parse_input, generate_report
from financial_skill.valuation import value_case


class EndToEndTests(unittest.TestCase):
    def test_synthetic_inputs_generate_all_required_sections(self):
        root = Path(__file__).resolve().parents[1]
        d, capital, market, cases = parse_input(root/'examples'/'synthetic_company.json')
        self.assertTrue(d['synthetic'])
        self.assertEqual(set(cases), {'bear', 'base', 'bull'})
        report = generate_report(d, capital, market, cases)
        for name in ('## Scenarios', '## Reverse DCF', '## Fragility:',
                     '## Sensitivity:', '## Investor return', '## Historical diagnostics'):
            self.assertIn(name, report)
        self.assertIn('Synthetic educational example', report)
        self.assertIn('No fixed 30% target', report)
        self.assertIn('first minimum-cash breach year', report)

    def test_incomplete_nonsynthetic_input_rejected(self):
        root = Path(__file__).resolve().parents[1]
        d = json.loads((root/'examples'/'synthetic_company.json').read_text())
        d['synthetic'] = False
        with tempfile.TemporaryDirectory() as t:
            path = Path(t)/'unattributed.json'
            path.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError, 'Missing source evidence'):
                parse_input(path)

    def test_economic_scenario_order_not_hardcoded(self):
        root = Path(__file__).resolve().parents[1]
        _, cap, _, cases = parse_input(root/'examples'/'synthetic_company.json')
        prices = [value_case(cases[n],cap).fair_price for n in ('bear','base','bull')]
        self.assertEqual(prices,sorted(prices))


if __name__ == '__main__':
    unittest.main()
