import os
import unittest
from unittest import TestCase

from test.resource.wrapper.FooWrapper10 import FooWrapper10
from test.resource.wrapper.FooWrapper4 import FooWrapper4
from test.resource.wrapper.FooWrapper5 import FooWrapper5
from test.resource.wrapper.FooWrapper6 import FooWrapper6
from test.resource.wrapper.FooWrapper7 import FooWrapper7
from test.resource.wrapper.FooWrapper8 import FooWrapper8
from test.resource.wrapper.FooWrapper9 import FooWrapper9
from test.resource.wrapper.fooPackage.FooWrapperPackaged import FooWrapperPackaged
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.Reader import Reader
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.SetUtils import SetUtils
from wopmars.utils.WopMarsException import WopMarsException


class TestReader(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        session = SQLManager.instance().get_session()
        session.get_or_create(TypeInputOrOutput, defaults={"is_input": True}, is_input=True)
        session.get_or_create(TypeInputOrOutput, defaults={"is_input": False}, is_input=False)
        session.commit()
        self.__session = SQLManager.instance().get_session()
        self.__reader = Reader()

        self.__s_root_path = PathFinder.get_module_path()

        # The good -------------------------------:

        self.__s_example_definition_file = os.path.join(self.__s_root_path, "test/resource/wopfile/example_def_file1.yml")
        self.__s_example_definition_file2 = os.path.join(self.__s_root_path, "test/resource/wopfile/example_def_file3.yml")

        # The ugly (malformed file) --------------------:

        self.__s_example_definition_file_duplicate_rule = os.path.join(self.__s_root_path, "test/resource/wopfile/example_def_file_duplicate_rule.yml")

        self.__list_f_to_exception_init = [
            os.path.join(self.__s_root_path, s_path) for s_path in [
                "test/resource/wopfile/example_def_file_wrong_yaml.yml",
                "test/resource/wopfile/example_def_file_duplicate_rule.yml",
                "test/resource/wopfile/example_def_file_wrong_grammar.yml",
                "test/resource/wopfile/example_def_file_wrong_grammar2.yml",
                "test/resource/wopfile/example_def_file_wrong_grammar3.yml",
                "test/resource/wopfile/example_def_file_wrong_grammar4.yml"
                ]
        ]

        # The bad (invalid file) ----------------------:

        self.__list_s_to_exception_read = [
            os.path.join(self.__s_root_path, s_path) for s_path in [
                "test/resource/wopfile/example_def_file1.yml",
                "test/resource/wopfile/example_def_file_wrong_content2.yml",
                "test/resource/wopfile/example_def_file_wrong_content3.yml",
                "test/resource/wopfile/example_def_file_wrong_content4.yml",
                "test/resource/wopfile/example_def_file_wrong_content5.yml",
                "test/resource/wopfile/example_def_file_wrong_class_name.yml",
                "test/resource/wopfile/example_def_file_wrong_rule.yml",
            ]
        ]

    # Fix this test for Travis
    # def test_load_definition_file(self):
    #     for file in self.__list_f_to_exception_init:
    #         with self.assertRaises(WopMarsException):
    #             self.__reader.load_definition_file(file)
    #     # Not existing file
    #     with self.assertRaises(WopMarsException):
    #         self.__reader.load_definition_file("Not existing file.")

    def test_check_duplicate_rule(self):
        with open(self.__s_example_definition_file_duplicate_rule) as file_duplicate_rule:
            with self.assertRaises(WopMarsException):
                Reader.check_duplicate_rules(file_duplicate_rule.read())

        with open(self.__s_example_definition_file) as file:
            try:
                Reader.check_duplicate_rules(file.read())
            except Exception as e:
                raise AssertionError("Should not raise an exception " + str(e))

    def test_read2(self):
        try:
            self.__reader.read(self.__s_example_definition_file2)
            result = self.__session.query(ToolWrapper).one()
        except:
            raise AssertionError("Packaged wrappers should not raise an exception")

        input_entry = TypeInputOrOutput(is_input=True)
        output_entry = TypeInputOrOutput(is_input=False)

        f1 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = input_entry

        f2 = FileInputOutputInformation(name="output1", path="test/output/output_file1.txt")
        f2.relation_file_or_tableioinfo_to_typeio = output_entry

        t1 = TableInputOutputInformation(model_py_path="test.resource.model.fooPackage.FooBasePackaged", table_name="FooBasePackaged")
        t1.relation_file_or_tableioinfo_to_typeio = input_entry

        tw1 = FooWrapperPackaged(rule_name="rule1")
        tw1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        tw1.relation_toolwrapper_to_tableioinfo.append(t1)

        self.assertEqual(result, tw1)

    def test_read(self):

        self.__reader.read(self.__s_example_definition_file)
        result = set(self.__session.query(ToolWrapper).all())

        input_entry = TypeInputOrOutput(is_input=True)
        output_entry = TypeInputOrOutput(is_input=False)

        f1 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = input_entry

        f2 = FileInputOutputInformation(name="output1", path="test/output/output_file1.txt")
        f2.relation_file_or_tableioinfo_to_typeio = output_entry

        f3 = FileInputOutputInformation(name="input1", path="test/output/output_file1.txt")
        f3.relation_file_or_tableioinfo_to_typeio = input_entry

        f3bis = FileInputOutputInformation(name="input1", path="test/output/output_file1.txt")
        f3bis.relation_file_or_tableioinfo_to_typeio = input_entry

        f4 = FileInputOutputInformation(name="output1", path="test/output/output_file2.txt")
        f4.relation_file_or_tableioinfo_to_typeio = output_entry

        f5 = FileInputOutputInformation(name="output1", path="test/output/output_file3.txt")
        f5.relation_file_or_tableioinfo_to_typeio = output_entry

        f6 = FileInputOutputInformation(name="output2", path="test/output/output_file4.txt")
        f6.relation_file_or_tableioinfo_to_typeio = output_entry

        f7 = FileInputOutputInformation(name="input1", path="test/output/output_file3.txt")
        f7.relation_file_or_tableioinfo_to_typeio = input_entry

        f8 = FileInputOutputInformation(name="input2", path="test/output/output_file2.txt")
        f8.relation_file_or_tableioinfo_to_typeio = input_entry

        f9 = FileInputOutputInformation(name="output1", path="test/output/output_file5.txt")
        f9.relation_file_or_tableioinfo_to_typeio = output_entry

        f10 = FileInputOutputInformation(name="input1", path="test/output/output_file4.txt")
        f10.relation_file_or_tableioinfo_to_typeio = input_entry

        f11 = FileInputOutputInformation(name="output1", path="test/output/output_file6.txt")
        f11.relation_file_or_tableioinfo_to_typeio = output_entry

        f12 = FileInputOutputInformation(name="input1", path="test/output/output_file1.txt")
        f12.relation_file_or_tableioinfo_to_typeio = input_entry

        f13 = FileInputOutputInformation(name="input2", path="test/output/output_file5.txt")
        f13.relation_file_or_tableioinfo_to_typeio = input_entry

        f14 = FileInputOutputInformation(name="input3", path="test/output/output_file6.txt")
        f14.relation_file_or_tableioinfo_to_typeio = input_entry

        f15 = FileInputOutputInformation(name="output1", path="test/output/output_file7.txt")
        f15.relation_file_or_tableioinfo_to_typeio = output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
        t1.relation_file_or_tableioinfo_to_typeio = output_entry

        t1bis = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
        t1bis.relation_file_or_tableioinfo_to_typeio = input_entry

        t2 = TableInputOutputInformation(model_py_path="FooBase2", table_name="FooBase2")
        t2.relation_file_or_tableioinfo_to_typeio = output_entry

        t2bis = TableInputOutputInformation(model_py_path="FooBase2", table_name="FooBase2")
        t2bis.relation_file_or_tableioinfo_to_typeio = input_entry

        tw1 = FooWrapper4(rule_name="rule1")
        tw1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        tw2 = FooWrapper5(rule_name="rule2")
        tw2.relation_toolwrapper_to_fileioinfo.extend([f3, f4])
        tw2.relation_toolwrapper_to_tableioinfo.extend([t1])
        tw3 = FooWrapper6(rule_name="rule3")
        tw3.relation_toolwrapper_to_fileioinfo.extend([f3bis, f5, f6])
        tw4 = FooWrapper7(rule_name="rule4")
        tw4.relation_toolwrapper_to_tableioinfo.extend([t1bis, t2])
        tw5 = FooWrapper8(rule_name="rule5")
        tw5.relation_toolwrapper_to_fileioinfo.extend([f8, f7, f9])
        tw6 = FooWrapper9(rule_name="rule6")
        tw6.relation_toolwrapper_to_fileioinfo.extend([f10, f11])
        tw6.relation_toolwrapper_to_tableioinfo.extend([t2bis])
        tw7 = FooWrapper10(rule_name="rule7")
        tw7.relation_toolwrapper_to_fileioinfo.extend([f12, f13, f14, f15])

        expected = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])

        # The good ------------------------------------:

        self.assertTrue((SetUtils.all_elm_of_one_set_in_one_other(result, expected) and
                         SetUtils.all_elm_of_one_set_in_one_other(expected, result)))

        # The bad -------------------------------------:

        # [self.assertRaises(WopMarsException, self.__reader.read, file) for file in self.__list_s_to_exception_read]

        SQLManager.instance().get_session().rollback()

    def tearDown(self):
        SQLManager.instance().get_session().close()
        s_root_path = PathFinder.get_module_path()
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove(os.path.join(s_root_path, "test/output"))
        OptionManager._drop()
        SQLManager._drop()


if __name__ == "__main__":
    unittest.main()