import datetime
import unittest
from unittest.mock import patch, mock_open

from libs import consts
from libs import utils


class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.jsonData = {
            consts.DATA_WEAPONS_LAST_UPDATE_KEY: 'unknown',
            consts.DATA_MODS_LAST_UPDATE_KEY: 'unknown',
            consts.DATA_WEAPONS_KEY: {

            },
            consts.DATA_MODS_KEY: {

            },
            consts.DATA_MODS_CONFLICTS_KEY: {

            }
        }

        self.jsonDataStr = utils.get_json_dumps(self.jsonData)

    def test_dump_data(self):
        test_filename = 'dump_test.json'

        with patch('libs.utils.open', new=mock_open()) as mocked_file:
            utils.dump_data(self.jsonData, test_filename)

        mocked_file.assert_called_with(test_filename, 'w', encoding='utf-8')
        # mocked_file.return_value.write.assert_called_once_with(self.jsonDataStr)

    def test_load_data(self):
        test_filename = 'dump_test.json'

        with patch('libs.utils.open', new=mock_open(read_data=self.jsonDataStr)) as mocked_file:
            actual = utils.load_data(test_filename)

        mocked_file.assert_called_once_with(test_filename, 'r', encoding='utf-8')
        # mocked_file.return_value.write.assert_called_once_with(self.jsonData)

    def test_date_to_str(self):
        testJson = {
            'rightDate': datetime.datetime.now().isoformat(),
            'unknownDate': 'unknown',
            'wrongDate': 'wrong data',
        }

        actual_Right = utils.date_to_str(testJson['rightDate'], consts.PARTS_DATE_STRFTIME)
        self.assertEqual(datetime.datetime.fromisoformat(testJson['rightDate']).strftime(consts.PARTS_DATE_STRFTIME),
                         actual_Right)

        actual_Wrong = utils.date_to_str(testJson['wrongDate'], consts.PARTS_DATE_STRFTIME)
        self.assertEqual(datetime.datetime.now().strftime(consts.PARTS_DATE_STRFTIME), actual_Wrong)

        actual_Unknown = utils.date_to_str(testJson['unknownDate'], consts.PARTS_DATE_STRFTIME)
        self.assertEqual('неизвестно', actual_Unknown)

    def test_validate_data(self):
        testJSONData = None
        testJSONData = utils.validate_data(testJSONData)

        self.assertDictEqual(self.jsonData, testJSONData)


if __name__ == '__main__':
    unittest.main()
