from wopmars.Base import Base
from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.ddl import DDL
from wopmars.SQLManager import SQLManager

class TableModificationTime(Base):
    """
    The TableModificationTime model contains the table names of the workflow and their mtime_epoch_millis of last modification. The table
    ``wom_modification_table`` contains the following fields:

    - table_name: VARCHAR(255) - primary key - the is_input of the table
    - mtime_epoch_millis: INTEGER - unix mtime_epoch_millis [ms] of last modification of the table
    """

    __tablename__ = "wom_modification_table"

    table_name = Column(String(255), primary_key=True)
    mtime_human = Column(DateTime, nullable=False)
    mtime_epoch_millis = Column(BigInteger, nullable=False)

    tables = relationship("TableInputOutputInformation", back_populates="modification")

    def __repr__(self):
        return "<Modification on " + str(self.table_name) + ": " + str(self.mtime_epoch_millis) + ">"

    @staticmethod
    def create_triggers():
        """
        Create an INSERT, UPDATE, DELETE trigger on the models created by the user in order to store the modifications mtime_epoch_millis.
        """
        stmt = ["INSERT", "UPDATE", "DELETE"]
        for table_name in Base.metadata.tables:
            if table_name[:4] != "wom_":
                for s in stmt:
                    data={"statement": str(s), "table_name": str(table_name)}
                    if SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'sqlite':
                        sql_trigger = "CREATE TRIGGER IF NOT EXISTS {table_name}_{statement} " \
                              "AFTER {statement} ON {table_name} BEGIN UPDATE wom_modification_table " \
                              "SET mtime_epoch_millis = CAST((julianday('now') - 2440587.5)*86400000 AS INTEGER), " \
                              "mtime_human = datetime('now', 'localtime') " \
                                      "WHERE table_name = '{table_name}'; END;".format(**data)
                    # elif SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'mysql':
                    #     sql_trigger = "CREATE TRIGGER IF NOT EXISTS {table_name}_{statement} AFTER {statement} " \
                    #       "ON {table_name} for each row UPDATE wom_table_modification_time SET " \
                    #                   "mtime_epoch_millis = ROUND(UNIX_TIMESTAMP(CURTIME(4)) * 1000) " \
                    #       "WHERE table_name = '{table_name}';".format(**data)
                    #     obj_ddl = DDL(sql_trigger)
                    #     SQLManager.instance().create_trigger(Base.metadata.tables[table_name], obj_ddl)
                    # elif SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'postgresql':
                    #     sql_trigger = """
                    #         CREATE OR REPLACE FUNCTION {table_name}_{statement}() RETURNS TRIGGER AS ${table_name}_{statement}$
                    #         BEGIN
                    #         UPDATE wom_table_modification_time SET mtime_epoch_millis = extract(epoch from now())*1000 WHERE table_name = '{table_name}';
                    #         RETURN NULL; -- result is ignored since this is an AFTER trigger
                    #         END;
                    #         ${table_name}_{statement}$ LANGUAGE plpgsql;
                    #         DROP TRIGGER IF EXISTS {table_name}_{statement} ON "{table_name}";
                    #         CREATE TRIGGER {table_name}_{statement} AFTER INSERT ON "{table_name}"
                    #         FOR EACH ROW EXECUTE PROCEDURE {table_name}_{statement}();
                    #         """.format(**data)
                    obj_ddl = DDL(sql_trigger)
                    SQLManager.instance().create_trigger(Base.metadata.tables[table_name], obj_ddl)
