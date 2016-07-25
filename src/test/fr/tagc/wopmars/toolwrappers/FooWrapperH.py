"""
Module containing the FooWrapper1 class
"""
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapperH(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {
        "polymorphic_identity": "FooWrapperH"
    }

    def get_input_table(self):
        return ["FooBaseH"]

    def get_output_table(self):
        return ["FooBaseH2"]

    def run(self):
        q = self.session().query(self.input_table("FooBaseH")).all()
        for r in q:
            r.name2="FooBaseH2 - " + str(r.id)
            self.session().add(r)
        self.session().commit()
