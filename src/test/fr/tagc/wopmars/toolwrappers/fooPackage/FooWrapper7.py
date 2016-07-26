"""
Module containing the FooWrapper1 class
"""
import os
import time

from FooBase2 import FooBase2
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper

class FooWrapper7(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "fooPackage.FooWrapper7"}
    def specify_input_table(self):
        return ["FooBaseP"]

    def specify_output_table(self):
        return ["FooBase2P"]

    def run(self):
        print(self.__class__.__name__ + " en cours d'exécution.")
        inputs = self.session().query(self.input_table("FooBaseP")).all()
        self.session().delete_content(self.output_table("FooBase2P"))
        for i in inputs:
            entry = self.output_table("FooBase2P")(name=i.name)
            self.session().add(entry)
        print(self.session().query(FooBase2).all())
        time.sleep(1)
