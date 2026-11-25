"""Point-in-time evidence ledger. This validates provenance fields, NOT truth of a source."""
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse


@dataclass(frozen=True)
class FactEvidence:
    fact_key: str
    source_url: str
    published_on: date
    period_end: date
    source_kind: str  # filing, earnings_release, market_data, other

    def __post_init__(self) -> None:
        if not self.fact_key or not self.source_url:
            raise ValueError('Evidence fact key and source link required')
        if self.source_kind not in {'filing','earnings_release','market_data','other'}:
            raise ValueError('Unknown provenance source kind')
        if self.period_end > self.published_on:
            raise ValueError('Source cannot publish a completed period ending in the future')
        u = urlparse(self.source_url)
        if u.scheme != 'https' or not u.netloc:
            raise ValueError('Non-synthetic evidence requires an https source URL')


def validate_evidence(data: dict, valuation_date: date) -> tuple[FactEvidence, ...]:
    """Fail closed when core reported quantities lack as-of documentation.
    Every required fact must be sourced. Does NOT fetch/check the links.
    """
    if data.get('synthetic', False):
        return ()
    mandatory = {'starting_revenue_millions', 'capital_structure.cash',
                 'capital_structure.debt', 'capital_structure.diluted_shares_millions',
                 'price_snapshot.price'}
    for section in ('revenue_millions', 'fcf_millions'):
        if section in data.get('historical', {}):
            mandatory.update(f'historical.{section}.{k}' for k in
                             ('five_years_ago','three_years_ago','last_year','latest'))
    ledger = []
    keys = set()
    for e in data.get('evidence', []):
        item = FactEvidence(e['fact_key'], e['source_url'],
                            date.fromisoformat(e['published_on']),
                            date.fromisoformat(e['period_end']), e['source_kind'])
        if item.fact_key in keys:
            raise ValueError(f'Duplicate source for fact key {item.fact_key}; choose canonical source')
        if item.published_on > valuation_date:
            raise ValueError(f'Lookahead: {item.fact_key} published after valuation date')
        keys.add(item.fact_key)
        ledger.append(item)
    missing = mandatory - keys
    if missing:
        raise ValueError('Missing source evidence: ' + ', '.join(sorted(missing)))
    return tuple(ledger)
