import unittest
from api import Dataset

class APITester(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = Dataset()
    def test_date_range_length(self):
        # checks that the bounding works so that it doesn't use a closed range
        self.assertEqual(len(self.dataset.sharkAttacksInDateRange((1,1,2023), (1,1,2023))), 1)
        # should be 7, but one of the entries is formatted as 3022, so actually is 6
        # checks that code works on more than 1 day, as well as over multiple years and different months
        self.assertEqual(len(self.dataset.sharkAttacksInDateRange((12,1,2022), (1,1,2023))), 6)
        
    def test_illegal_dates(self):
        # tests that days after the end of months or years don't succeed. Also negative days/months.
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(1,32,2022)))
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(2,29,2022)))
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(4,31,2022)))
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(13,1,2022)))
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(-1,1,2022)))
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(1,-1,2022)))
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((12,31,2022),(1,1,1)))
    
    def test_future_date(self):
        # tests that future dates are rejected
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(12,31,9999)))
        
    def test_leap_year(self):
        # make sure it works on centuries
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(2,29,1900)))
        self.assertIsNotNone(self.dataset.sharkAttacksInDateRange((1,1,1),(2,29,2000)))
        # test with a non-leap year
        self.assertIsNone(self.dataset.sharkAttacksInDateRange((1,1,1),(2,29,2001)))
        # test on multiples of 4
        self.assertIsNotNone(self.dataset.sharkAttacksInDateRange((1,1,1),(2,29,1904)))
    
    def test_get_species(self):
        # not counting badly formatted date entries, there should be 29 zambesi attacks
        # if it works for one species, it should work for all, so I don't test more species.
        self.assertEqual(self.dataset.getSpecies()['zambesi'], 29)
    
    def test_get_species_with_common_words(self):
        # make sure common words aren't picked up if they aren't species
        self.assertFalse('shark' in self.dataset.getSpecies().keys())
    
    def test_get_body_parts(self):
        # not counting badly formatted date entries, there should be 34 shin attacks
        # if it works for one part, it should work for all, so I don't test more body parts.
        self.assertEqual(self.dataset.getBodyParts()['shin'], 34)
        
    def teset_get_body_parts_with_common_words(self):
        # make sure common words aren't picked up if they aren't body parts
        self.assertFalse('fatal' in self.dataset.getBodyParts().keys())
    
    def test_get_attack_by_id(self):
        # this is a truly unique entry, so great for testing that it grabs attacks by ID well
        self.assertEqual(self.dataset.getAttackByID('2021.11.15')[1], '15-Nox-2021')
        
    def test_get_attack_with_nonexistent_id(self):
        # verify that non-existent IDs don't give results
        self.assertIsNone(self.dataset.getAttackByID('-1'))
        
    def test_getSharkSpecies(self):
        self.assertEqual(self.dataset.getSharkSpecies('2022.10.07'), 'Bull shark')

    def test_getSharkSpeciesWithFakeID(self):
        self.assertEqual(self.dataset.getSharkSpecies('2100.00.00'), None)
        self.assertEqual(self.dataset.getSharkSpecies('abcd'), None)

    def test_getUnknownSharkSpecies(self):
        self.assertEqual(self.dataset.getSharkSpecies('2022.11.03'), 'Unknown')

    def test_activityAtTimeOfSharkAttack(self):
        self.assertEqual(self.dataset.activityAtTimeOfSharkAttack('2022.11.27'), 'Swimming')

    def test_activityAtTimeOfSharkAttackWithFakeID(self):
        self.assertEqual(self.dataset.activityAtTimeOfSharkAttack('2100.00.00'), None)
        self.assertEqual(self.dataset.activityAtTimeOfSharkAttack('abcd'), None)

    def test_unknownActivityAtTimeOfSharkAttack(self):
        self.assertEqual(self.dataset.activityAtTimeOfSharkAttack('2022.05.07'), 'Undisclosed')

    def test_getInjury(self):
        self.assertEqual(self.dataset.getInjury('2022.11.27'), 'Foot bitten')

    def test_getInjuryWithFakeID(self):
        self.assertEqual(self.dataset.getInjury('2100.00.00'), None)
        self.assertEqual(self.dataset.getInjury('abcd'), None)

    def test_getUnknownInjury(self):
        self.assertEqual(self.dataset.getInjury('2022.06.21'), 'Undisclosed')
    
    def test_compareAttacks(self):
        self.assertEqual(self.dataset.compareAttacks("2022.04.07", "2018.11.11.b"), ['Attack ID: 2022.04.07 vs 2018.11.11.b', 'Date: 7-Apr-22 vs 11-Nov-18', 'Country: United States of America vs South Africa','Species: Unknown vs White shark, 3m', 'Activity: Kayaking vs Fishing', 'Injury: No injury to occupants. Kayak bitten vs Surf-ski bitten but no injury to occupant'])
        self.assertEqual(self.dataset.compareAttacks("2022.12.08", "2017.11.30.a"), ['Attack ID: 2022.12.08 vs 2017.11.30.a', 'Date: 8-Dec-22 vs 30-Nov-17','Country: United States of America vs Costa Rica','Species: Tiger shark vs Tiger shark, female', 'Activity: Snorkeling vs Scuba diving', 'Injury: Fatal attack vs FATAL'])

    def test_compareAttacksWithFakeIDs(self): 
        self.assertEqual(self.dataset.compareAttacks('2100.00.00', "3432.12.12"), None)
        self.assertEqual(self.dataset.compareAttacks('abcd', 'wrongInput'), None)
        self.assertEqual(self.dataset.compareAttacks('2022.12.08', "3432.12.12"), None) 
        self.assertEqual(self.dataset.compareAttacks('2100.00.00', "2022.11.27"), None)
    
    def test_ValidCountry(self):
        self.assertTrue(self.dataset.checkValidCountry('US'))
        self.assertTrue(self.dataset.checkValidCountry('USA'))
        self.assertTrue(self.dataset.checkValidCountry('United States of America'))

    def test_InvalidCountry(self):
        self.assertRaises(Exception, self.dataset.checkValidCountry, 'West Korea')
    
    
    def test_MostCommonSharkArea(self):
        self.assertEqual(self.dataset.mostCommonSharkArea('USA')[0], 'Florida')
        self.assertEqual(len(self.dataset.mostCommonSharkArea('USA')), 1)
   
    def test_MostCommonSharkAreaInvalidCountry(self):
        self.assertRaises(Exception, self.dataset.mostCommonSharkArea, 'West Korea')

    
    def test_LeastCommonSharkArea(self):
        self.assertEqual(self.dataset.leastCommonSharkArea('USA')[0], 'Bahamas')
        self.assertEqual(len(self.dataset.leastCommonSharkArea('USA')), 23)
    
    def test_LeastCommonSharkAreaInvalidCountry(self):
        self.assertRaises(Exception, self.dataset.leastCommonSharkArea, 'West Korea')

    def test_WhatCountry(self):
        location = self.dataset.whatCountry((52.509669, 13.376294))
        self.assertEqual(location, 277)
    
    def test_WhatCountryMiddleOcean(self):
        location = self.dataset.whatCountry((49.439557, -31.287717))
        self.assertEqual(location, 621)
    
    
    def test_SafestBeachFromCountry(self):
        self.assertEqual(len(self.dataset.safestBeachFromCountry('USA')), 18)
    
    def test_SafestBeachFromInvalidCountry(self):
        self.assertRaises(Exception, self.dataset.safestBeachFromCountry, 'West Korea')
    
    def test_SafestBeachFromCoordinates(self):
        self.assertEqual(len(self.dataset.safestBeachFromCoordinates((38.6270, -90.1994))), 18)
    
    def test_SafestBeachFromCoordinatesInMiddleOfOCean(self):
        self.assertEqual(len(self.dataset.safestBeachFromCoordinates((49.439557, -31.287717))), 2)

if __name__ == '__main__':
    unittest.main()