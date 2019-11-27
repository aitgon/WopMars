"""
Module containing the FooWrapper1 class
"""
from wopmars.models.Rule import Rule

from sqlalchemy.sql import select


class FooWrapperCore(Rule):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapperCore"}

    def specify_output_table(self):
        return ["FooBase7"]

    def run(self):
        foobase = self.output_table("FooBase7").__table__
        inserted_list = []
        for i in range(10000):
            inserted_list.append({'id': i, 'name': "FooWrapperCore " + str(i)})
        ins = foobase.insert()
        self.session().execute(ins, inserted_list)

        s = select([foobase])
        result = self.session().execute(s)
        for row in result:
            print(row)
