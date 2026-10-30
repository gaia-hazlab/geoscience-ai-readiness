"""Sourcing-rule checks for the complexity tables in docs/complexity_2026-10-30."""

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("complexity_tables", ROOT / "scripts" / "complexity_tables.py")
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)

GOOD = {
    "id": "pl-01", "item": "earthquake magnitudes", "quantity": "b-value", "value": 1.0, "value_min": 0.8,
    "value_max": 1.2, "value_text": "b close to 1", "units": "dimensionless", "source": "Example (2000)",
    "doi": "10.1000/xyz", "url": None, "as_of": "2000", "quote": "b is close to 1", "where_read": "abstract",
    "checked_in_text": True, "notes": "", "domain": "geoscience", "relation": "frequency-size distribution",
    "symbol": "b", "convention": "cumulative", "tested_vs_alternatives": "not tested in this source",
}
PREFIX, EXTRA = ct.TABLES["power_laws.json"]


class ComplexityTableTests(unittest.TestCase):
    def errors(self, **changes):
        row = copy.deepcopy(GOOD)
        row.update(changes)
        return ct.row_errors(row, PREFIX, EXTRA)

    def test_tracked_tables_pass(self):
        tables = ct.load()
        self.assertEqual(set(tables), set(ct.TABLES))

    def test_good_row_passes(self):
        self.assertEqual(self.errors(), [])

    def test_missing_value_must_say_not_found(self):
        self.assertTrue(self.errors(value=None, value_min=None, value_max=None, value_text="about 1"))
        self.assertEqual(self.errors(value=None, value_min=None, value_max=None, value_text="not found",
                                     checked_in_text=False, quote=None), [])

    def test_read_flag_requires_quote_and_fetched_source(self):
        self.assertTrue(self.errors(quote=None))
        self.assertTrue(self.errors(where_read="search snippet"))

    def test_value_must_sit_inside_range(self):
        self.assertTrue(self.errors(value=1.5))
        self.assertTrue(self.errors(value_min=2.0))

    def test_rejects_unsourced_value_and_bad_doi(self):
        self.assertTrue(self.errors(doi=None, url=None))
        self.assertTrue(self.errors(doi="doi.org/10.1000/xyz"))
        self.assertTrue(self.errors(as_of=""))

    def test_rejects_unknown_test_verdict_and_duplicates(self):
        self.assertTrue(self.errors(tested_vs_alternatives="probably"))
        table = {"retrieved": "2026-10-30", "rows": [copy.deepcopy(GOOD), copy.deepcopy(GOOD)]}
        self.assertIn("pl-01: duplicate id", ct.validate_table(table, PREFIX, EXTRA))

    def test_pde_counts_are_consistent(self):
        prefix, extra = ct.TABLES["coupled_pdes.json"]
        row = {k: GOOD[k] for k in ct.COMMON}
        row.update(id="pde-01", value=4, value_min=None, value_max=None, units="scalar PDEs",
                   balance_equations_vector=2, balance_equations_scalar_3d=4, ode_state_variables=0,
                   field_unknowns=["u", "p"], constitutive_closures=["Darcy"], count_derived_by="read from source")
        self.assertEqual(ct.row_errors(row, prefix, extra), [])
        row.update(balance_equations_scalar_3d=1)
        self.assertTrue(ct.row_errors(row, prefix, extra))


if __name__ == "__main__":
    unittest.main()
