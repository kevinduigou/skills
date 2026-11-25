import json
import tempfile
import unittest
from pathlib import Path

from financial_skill.cli import parse_input
from financial_skill.html_report import render_html_report
from financial_skill.recommendation import RUBRIC, calculate_rating, category_for_score

ROOT=Path(__file__).resolve().parents[1]


class HtmlReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.cap, cls.market, cls.cases=parse_input(ROOT/'examples'/'synthetic_company.json')

    def test_fixed_100_point_weights(self):
        self.assertEqual(sum(entry[2] for entry in RUBRIC), 100)

    def test_correct_band_edges(self):
        for num,category in ((1,'Strong Sell'),(20,'Strong Sell'),(21,'Sell'),(40,'Sell'),
                             (41,'Hold'),(60,'Hold'),(61,'Buy'),(80,'Buy'),
                             (81,'Strong Buy'),(100,'Strong Buy')):
            self.assertEqual(category_for_score(num),category)
        for x in (0,101,False,50.5):
            with self.assertRaises(ValueError): category_for_score(x)

    def test_sample_score_and_html(self):
        rat=calculate_rating(self.data)
        self.assertEqual((rat.score,rat.category),(34,'Sell'))
        result=render_html_report(self.data,self.cap,self.market,self.cases)
        for marker in ('Investment recommendation Sell, score 34 out of 100',
                       'STRONG SELL','STRONG BUY','34<span> / 100',
                       'Three-scenario valuation','Financial fundamentals',
                       'Reverse DCF','Sensitivity map','Fragility & downside stress',
                       'Forecast detail','Evidence & decision tests',
                       'Free cash flow','Terminal share','SYNTHETIC EXAMPLE'):
            self.assertIn(marker,result)
        self.assertNotIn('<script',result)
        self.assertNotIn('https://fonts.',result)
        self.assertIn('<style>',result)
        self.assertIn('</html>',result)

    def test_missing_scoring_shows_unrated_not_fabricated(self):
        d=dict(self.data)
        d.pop('investment_assessment')
        self.assertIsNone(calculate_rating(d))
        html=render_html_report(d,self.cap,self.market,self.cases)
        self.assertIn('Not rated',html)
        self.assertIn('No numerical rating:',html)
        self.assertNotIn('Investment recommendation Sell, score',html)

    def test_scores_validated_and_thesis_required(self):
        d=json.loads(json.dumps(self.data))
        d['investment_assessment']['components']['quality']['score']=1000
        with self.assertRaises(ValueError): calculate_rating(d)
        d['investment_assessment']['components']['quality']['score']=80
        d['investment_assessment']['components']['quality']['rationale']=''
        with self.assertRaises(ValueError): calculate_rating(d)
        d['investment_assessment']['components'].pop('evidence')
        with self.assertRaises(ValueError): calculate_rating(d)

    def test_render_escapes_untrusted_content(self):
        d=json.loads(json.dumps(self.data))
        d['investment_assessment']['thesis']='<script>alert("xss")</script>'
        d['ticker']='<img src=x onerror=alert(1)>'
        html=render_html_report(d,self.cap,self.market,self.cases)
        self.assertNotIn('<script',html)
        self.assertNotIn('<img src=x',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('&lt;img src=x',html)

    def test_cli_generates_both_reports(self):
        from financial_skill.cli import main
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            name=Path(tmp)/'study.md'
            with patch('sys.argv',['financial_skill.cli','--input',str(ROOT/'examples'/'synthetic_company.json'),'--output',str(name)]):
                main()
            self.assertTrue(name.exists())
            self.assertTrue(name.with_suffix('.html').exists())
            self.assertIn('34/100',name.read_text())
            self.assertIn('<!doctype html>',name.with_suffix('.html').read_text())


if __name__=='__main__': unittest.main()
