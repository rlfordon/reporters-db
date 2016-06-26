import datetime
from reporters_db import REPORTERS, VARIATIONS_ONLY, EDITIONS
from unittest import TestCase

VALID_CITE_TYPES = (
    'federal',
    'neutral',
    'scotus_early',
    'specialty',
    'specialty_west',
    'specialty_lexis',
    'state',
    'state_regional',
)


class ConstantsTest(TestCase):
    def test_any_keys_missing_editions(self):
        """Have we added any new reporters that lack a matching edition?"""
        for r_name, r_items in REPORTERS.items():
            # For each reporter
            for item in r_items:
                # and each book in each reporter
                self.assertIn(
                    r_name, item['editions'],
                    msg="Could not find edition for key: %s" % r_name
                )

    def test_for_variations_mapping_to_bad_keys(self):
        """Do we have a variation that maps to a key that doesn't exist in the
        first place?
        """
        for variations in VARIATIONS_ONLY.values():
            for variation in variations:
                self.assertIn(
                    EDITIONS[variation],
                    REPORTERS.keys(),
                    msg="Could not map variation to a valid reporter: %s" %
                        variation
                )

    def test_that_all_dates_are_converted_to_dates_not_strings(self):
        """Do we properly make the ISO-8601 date strings into Python dates?"""
        for reporter_name, reporter_list in REPORTERS.iteritems():
            # reporter_name == "A."
            # reporter_list == [
            # {'name': 'Atlantic Reporter', 'editions': ...},
            # {'name': 'Aldo's Reporter', 'editions': ...}
            # ]
            for reporter_dict in reporter_list:
                # reporter_dict == {'name': 'Atlantic Reporter'}
                for e_name, e_dates in reporter_dict['editions'].iteritems():
                    # e_name == "A. 2d"
                    # e_dates == {
                    #     "end": "1938-12-31T00:00:00",
                    #     "start": "1885-01-01T00:00:00"
                    # }
                    for key in ['start', 'end']:
                        is_date_or_none = (
                            isinstance(e_dates[key], datetime.datetime) or
                            e_dates[key] is None
                        )
                        self.assertTrue(
                            is_date_or_none,
                            msg=("%s dates in the reporter '%s' appear to be "
                                 "coming through as '%s'" %
                                 (key, e_name, type(e_dates[key])))
                        )

    def test_all_reporters_have_valid_cite_type(self):
        """Do all reporters have valid cite_type values?"""
        for reporter_abbv, reporter_list in REPORTERS.items():
            for reporter_data in reporter_list:
                self.assertIn(
                    reporter_data['cite_type'],
                    VALID_CITE_TYPES,
                    "%s did not have a valid cite_type value" % reporter_abbv,
                )

    def test_all_required_keys_no_extra_keys(self):
        """Are all required keys present? Are there any keys present that
        shouldn't be?
        """
        required_fields = ['cite_type', 'editions', 'mlz_jurisdiction', 'name',
                           'variations']
        optional_fields = ['publisher', 'notes', 'href']
        all_fields = required_fields + optional_fields
        for reporter_abbv, reporter_list in REPORTERS.items():
            for reporter_data in reporter_list:

                # All required fields present?
                for required_field in required_fields:
                    try:
                        reporter_data[required_field]
                    except KeyError:
                        self.fail("Reporter '%s' lacks required field '%s'" % (
                            reporter_abbv, required_field
                        ))

                # No extra fields?
                for k in reporter_data.keys():
                    self.assertIn(
                        k,
                        all_fields,
                        "Reporter '%s' has an unknown field '%s'" % (
                            reporter_abbv, k
                        )
                    )

    def test_no_variation_is_same_as_key(self):
        """Are any variations identical to the keys they're supposed to be
        variations of?
        """
        for variation, keys in VARIATIONS_ONLY.items():
            for key in keys:
                self.assertNotEqual(
                    variation,
                    key,
                    "The variation '%s' is identical to the key it's supposed "
                    "to be a variation of." % variation
                )

    def test_nothing_ends_before_it_starts(self):
        """Do any editions have end dates before their start dates?"""
        for reporter_dicts in REPORTERS.values():
            # Each value is a list of reporter dictionaries
            for reporter in reporter_dicts:
                # Each edition is a dict of keys that go to more dicts!
                for k, edition in reporter['editions'].items():
                    if edition['start'] and edition['end']:
                        self.assertLessEqual(
                            edition['start'],
                            edition['end'],
                            msg="It appears that edition %s ends before it "
                                "starts." % k
                        )
