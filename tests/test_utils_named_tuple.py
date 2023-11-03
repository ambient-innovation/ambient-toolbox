from collections import OrderedDict

from django.test import TestCase

from ambient_toolbox.utils import get_key_from_tuple_by_value, get_namedtuple_choices, get_value_from_tuple_by_key


class UtilsNamedTupleTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.MY_CHOICE_ONE = 1
        cls.MY_CHOICE_TWO = 2
        cls.MY_CHOICE_THREE = 3

        cls.MY_CHOICE_LIST = (
            (cls.MY_CHOICE_ONE, "Choice 1"),
            (cls.MY_CHOICE_TWO, "Choice 2"),
            (cls.MY_CHOICE_THREE, "Choice 3"),
        )

        cls.colors_choices = get_namedtuple_choices(
            "COLORS",
            (
                (1, "black", "Black"),
                (2, "white", "White"),
            ),
        )

    def test_get_namedtuple_choices_regular(self):
        self.assertEqual(self.colors_choices.black, 1)
        self.assertEqual(self.colors_choices.white, 2)

    def test_get_namedtuple_choices_get_choices_regular(self):
        self.assertEqual(self.colors_choices.get_choices(), [(1, "Black"), (2, "White")])

    def test_get_namedtuple_choices_get_choices_dict_regular(self):
        self.assertEqual(self.colors_choices.get_choices_dict(), OrderedDict([(1, "Black"), (2, "White")]))

    def test_get_namedtuple_choices_get_all_regular(self):
        for index, color in enumerate(self.colors_choices.get_all()):
            expected_tuple = "invalid_data"
            if index == 0:
                expected_tuple = (1, "black", "Black")
            elif index == 1:
                expected_tuple = (2, "white", "White")
            self.assertEqual(color, expected_tuple)

    def test_get_namedtuple_choices_get_choices_tuple_regular(self):
        self.assertEqual(self.colors_choices.get_choices_tuple(), ((1, "black", "Black"), (2, "white", "White")))

    def test_get_namedtuple_choices_get_values_regular(self):
        self.assertEqual(self.colors_choices.get_values(), [1, 2])

    def test_get_namedtuple_choices_get_value_by_name_regular(self):
        self.assertEqual(self.colors_choices.get_value_by_name("black"), 1)
        self.assertEqual(self.colors_choices.get_value_by_name("white"), 2)
        self.assertFalse(self.colors_choices.get_value_by_name("no-existing"))

    def test_get_namedtuple_choices_get_desc_by_value_regular(self):
        self.assertEqual(self.colors_choices.get_desc_by_value(1), "Black")
        self.assertEqual(self.colors_choices.get_desc_by_value(2), "White")
        self.assertFalse(self.colors_choices.get_desc_by_value(-1))

    def test_get_namedtuple_choices_get_name_by_value_regular(self):
        self.assertEqual(self.colors_choices.get_name_by_value(1), "black")
        self.assertEqual(self.colors_choices.get_name_by_value(2), "white")
        self.assertFalse(self.colors_choices.get_name_by_value(-1))

    def test_get_namedtuple_choices_is_valid_regular(self):
        self.assertTrue(self.colors_choices.is_valid(1))
        self.assertTrue(self.colors_choices.is_valid(2))
        self.assertFalse(self.colors_choices.is_valid(-1))

    def test_get_value_from_tuple_by_key_found(self):
        self.assertEqual(get_value_from_tuple_by_key(self.MY_CHOICE_LIST, self.MY_CHOICE_TWO), "Choice 2")

    def test_get_value_from_tuple_by_key_not_found(self):
        self.assertEqual(get_value_from_tuple_by_key(self.MY_CHOICE_LIST, 99), "-")

    def test_get_key_from_tuple_by_value_found(self):
        self.assertEqual(get_key_from_tuple_by_value(self.MY_CHOICE_LIST, "Choice 2"), self.MY_CHOICE_TWO)

    def test_get_key_from_tuple_by_value_not_found(self):
        self.assertEqual(get_key_from_tuple_by_value(self.MY_CHOICE_LIST, "Something odd"), "-")

    def test_get_values_case_is_instance(self):
        choices = get_namedtuple_choices(
            "TestChoices",
            (
                (0, "zero", "Zero"),
                (1, "one", "One"),
                ([2, 3], "two_three", "Two Three"),
            ),
        )

        # Überprüfen, ob die Methode get_values korrekt funktioniert
        self.assertEqual(choices.get_values(), [0, 1, 2, 3])
