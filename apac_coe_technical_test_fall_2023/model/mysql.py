import datetime as dt
from decimal import Decimal

from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import class_mapper, declarative_base, relationship

Base = declarative_base()


def to_dict_common(self, result):
    for key, value in result.items():
        # convert datetime to yyyy-mm-dd
        if isinstance(value, dt.datetime):
            result[key] = value.strftime("%Y-%m-%d")

        # convert decimal to string
        if isinstance(value, Decimal):
            result[key] = str(value)

    return result


class Orders(Base):
    __tablename__ = "Orders"

    Order_State = Column(Enum("I", "C"))
    Executing_Entity = Column(String(50))
    Contracting_Entity = Column(String(50))
    Instrument_Code = Column(String(50))
    Instrument_Description = Column(String(500))
    ISIN_Code = Column(String(50))
    Sedol_Code = Column(String(50))
    Market_Id = Column(String(50))
    Counterparty_Code = Column(String(50))
    Counterparty_Description = Column(String(500))
    Top_Level = Column(Enum("Y", "N"))
    Order_Id = Column(String(50), primary_key=True)
    Version = Column(Integer, primary_key=True)
    Buy_Sell = Column(Enum("B", "S"))
    Total_Quantity = Column(DECIMAL(28, 14))
    Limit_Price = Column(DECIMAL(28, 14))
    Gross_Fill_Price = Column(DECIMAL(28, 14))
    Settlement_Ccy = Column(String(50))
    Amended_Datetime = Column(DateTime)
    Trader = Column(String(50))
    Num_Fills = Column(String(50))
    Entered_Datetime = Column(DateTime)
    Settlement_Datetime = Column(DateTime)
    Commission_Type = Column(String(50))
    Commission_Value = Column(DECIMAL(28, 14))
    Root_Order_Id = Column(String(50))
    Quantity_Available = Column(DECIMAL(28, 14))
    Quantity_Filled_Today = Column(DECIMAL(28, 14))
    Last_Complete_Datetime = Column(DateTime)
    Account_Code = Column(String(50))
    Order_Notes = Column(String(300))

    # relationship
    trades = relationship("Trades", back_populates="order")

    def to_dict(self):
        result = {
            c.name: getattr(self, c.name) for c in class_mapper(self.__class__).columns
        }
        return to_dict_common(self, result)


class Trades(Base):
    __tablename__ = "Trades"

    Record_Type = Column(Enum("A", "B", "H", "M"), nullable=False)
    State = Column(Enum("C", "I"))
    Buy_Sell = Column(Enum("B", "S"))
    Quantity = Column(DECIMAL(28, 14))
    Instrument_Code = Column(String(50))
    Isin_Code = Column(String(50))
    Sedol_Code = Column(String(50))
    Exchange_Id = Column(String(50))
    Gross_Price = Column(DECIMAL(28, 14))
    Gross_Consideration = Column(DECIMAL(28, 14))
    Counterparty_Code = Column(String(50))
    Counterparty = Column(String(50))
    Trade_Datetime = Column(DateTime)
    Trade_Id = Column(String(50), primary_key=True)
    Version_Number = Column(Integer, primary_key=True)
    Settlement_Datetime = Column(DateTime)
    Dealt_Ccy = Column(String(50))
    Order_Id = Column(String(50), ForeignKey("Orders.Order_Id"))
    Entered_By = Column(String(50))
    Exchange_Trade_Code = Column(String(50))
    Trader = Column(String(50))
    Sub_Account = Column(String(50))
    Notes = Column(String(500))
    Instrument_Id = Column(String(50))
    Entered_Datetime = Column(DateTime)
    Commission_Type = Column(String(50))
    Commission_Value = Column(DECIMAL(28, 14))
    Trading_Entity_Id = Column(String(50))
    Amended_Datetime = Column(DateTime)
    Execution_Venue = Column(String(50))
    Order_Price_Type = Column(String(50))
    Root_Order_Id = Column(String(50))

    # relationship
    order = relationship("Orders", back_populates="trades")

    def to_dict(self):
        result = {
            c.name: getattr(self, c.name) for c in class_mapper(self.__class__).columns
        }
        return to_dict_common(self, result)
