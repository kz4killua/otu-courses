from django.test import TestCase
from django.core.management import call_command

from courses.scheduling.time_bitmap import TimeBitmap
from courses.scheduling.scheduling import get_valid_section_combinations, generate_schedules
from courses.models import Section
from courses.scheduling.filtering import is_section_downtown, is_section_before, is_section_after, is_section_closed


class TestTimeBitmap(TestCase):

    def setUp(self) -> None:
        call_command("updatesections", "202309", "--usecache")


    def test_overlaps(self):

        tb1 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'monday')
        tb2 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'tuesday')
        self.assertFalse(TimeBitmap.overlaps(tb1, tb2))

        tb1 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'monday')
        tb2 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'monday')
        self.assertTrue(TimeBitmap.overlaps(tb1, tb2))

        tb1 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'monday')
        tb2 = TimeBitmap.from_begin_and_end_time('0940', '1100', 'monday')
        self.assertFalse(TimeBitmap.overlaps(tb1, tb2))

        tb1 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'monday')
        tb1 |= TimeBitmap.from_begin_and_end_time('0810', '0930', 'wednesday')
        tb2 = TimeBitmap.from_begin_and_end_time('0840', '0930', 'tuesday')
        tb2 |= TimeBitmap.from_begin_and_end_time('0840', '0930', 'wednesday')
        self.assertTrue(TimeBitmap.overlaps(tb1, tb2))

        tb1 = TimeBitmap.from_begin_and_end_time('0810', '0930', 'monday')
        tb1 |= TimeBitmap.from_begin_and_end_time('0810', '0930', 'wednesday')
        tb2 = TimeBitmap.from_begin_and_end_time('0840', '0930', 'tuesday')
        tb2 |= TimeBitmap.from_begin_and_end_time('0840', '0930', 'thursday')
        self.assertFalse(TimeBitmap.overlaps(tb1, tb2))


class TestScheduling(TestCase):

    def setUp(self) -> None:
        call_command("updatesections", "202309", "--usecache")
    

    def test_generate_schedules(self):

        schedules = generate_schedules("202309", ["BIOL1000U", "EAP1000E"], time_limit=3, max_solutions=5, solver="random")
        self.assertEqual(len(schedules), 0)

        schedules = generate_schedules("202309", ["BIOL1000U", "EAP1000E"], time_limit=3, max_solutions=5, solver="cp")
        self.assertEqual(len(schedules), 0)

        schedules = generate_schedules("202309", ["BIOL1000U", "CRMN1000U"], time_limit=3, max_solutions=5, solver="random")
        self.assertEqual(len(schedules), 2)
        for schedule in schedules:
            self.assertEqual(len(schedule.keys()), 2)

        schedules = generate_schedules("202309", ["BIOL1000U", "CRMN1000U"], time_limit=3, max_solutions=5, solver="cp")
        self.assertEqual(len(schedules), 2)
        for schedule in schedules:
            self.assertEqual(len(schedule.keys()), 2)


    def test_get_valid_section_combinations(self):

        combinations = get_valid_section_combinations("202309", "BIOL1000U")
        self.assertEqual(len(combinations), 1)

        combinations = get_valid_section_combinations("202309", "CRMN1000U")
        self.assertEqual(len(combinations), 2)

        combinations = get_valid_section_combinations("202309", "CSCI2000U")
        self.assertEqual(len(combinations), 7)



class TestFiltering(TestCase):

    def setUp(self) -> None:
        call_command("updatesections", "202309", "--usecache")


    def test_is_section_downtown(self):
            
        section = Section.objects.get(term="202309", course_reference_number="40424")
        self.assertTrue(is_section_downtown(section))
    
        section = Section.objects.get(term="202309", course_reference_number="43546")
        self.assertFalse(is_section_downtown(section))


    def test_is_section_before(self):

        section = Section.objects.get(term="202309", course_reference_number="40291")
        self.assertTrue(is_section_before(section, "0900"))
    
        section = Section.objects.get(term="202309", course_reference_number="40288")
        self.assertFalse(is_section_before(section, "0900"))


    def test_is_section_after(self):

        section = Section.objects.get(term="202309", course_reference_number="40291")
        self.assertFalse(is_section_after(section, "0940"))

        section = Section.objects.get(term="202309", course_reference_number="40288")
        self.assertTrue(is_section_after(section, "1210"))


    def test_is_section_closed(self):

        section = Section.objects.get(term="202309", course_reference_number="40372")
        self.assertFalse(is_section_closed(section))
    
        section = Section.objects.get(term="202309", course_reference_number="40371")
        self.assertTrue(is_section_closed(section))