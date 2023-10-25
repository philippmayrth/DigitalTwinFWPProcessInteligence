from typing import *
import pandas as pd
import datetime


OpeningHours = NewType("OpeningHours", pd.DataFrame)
PreparedData = NewType("PreparedData", pd.DataFrame)


def getHoursFor8760Model(year: int=2023) -> List[datetime.datetime]:
    # Source: P. Mayr, Codebase of https://pvrechner.avalonsoft.de (Accessed: 2023-10-25)
    """Returns the datetime for every hour in the year

    Args:
        startYear (int, optional): _description_. Defaults to 2023.

    Returns:
        List[datetime.datetime]: _description_
    """
    assert len(str(year)) == 4, "invalid year"
    dates = []
    iDay = datetime.datetime.strptime(f'{year}-01-01','%Y-%m-%d')
    for _ in range(365 * 24):
        dates.append(iDay)
        iDay = iDay + datetime.timedelta(hours=1)
    return dates

def getOpeningHours() -> OpeningHours:
    openWeekdays: Callable = lambda h: True if h >= 17 and h <= 22 else False
    openWeekends: Callable = lambda h: True if h >= 12 and h <= 24 else False
    df = pd.DataFrame()
    hours = [hour+1 for hour in range(24)]
    df["hour"] = hours
    df["monday"] = df["hour"].apply(openWeekdays)
    df["tuesday"] = df["hour"].apply(openWeekdays)
    df["wednesday"] = df["hour"].apply(openWeekdays)
    df["thursday"] = df["hour"].apply(openWeekdays)
    df["friday"] = df["hour"].apply(openWeekdays)
    df["saturday"] = df["hour"].apply(openWeekends)
    df["sunday"] = df["hour"].apply(openWeekends)
    return df

def getPreparedDF(hoursOfYear: List[datetime.datetime], openingHours: OpeningHours) -> PreparedData:
    df = pd.DataFrame(hoursOfYear, columns=["date"])
    df["weekday"] = df["date"].apply(lambda d: d.weekday())
    df["isWeekend"] = df["weekday"].apply(lambda d: True if d >= 5 else False)
    weeknames = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    df["isOpen"] = df["date"].apply(lambda date: openingHours.loc[date.hour, weeknames[date.weekday()]])
    return df


def addOrders(df: PreparedData) -> pd.DataFrame:
    def dummyOrders(df) -> int:
        # TODO: Replace this function with one that takes into account a normal distribution of orders per hour on a given day
        isOpen = df["isOpen"]
        if df["isWeekend"]:
            return 30 if isOpen else 0 # more traffic on weekends
        return 10 if isOpen else 0
    df["ordersPhone"] = df.apply(dummyOrders, axis=1)
    df["ordersCounter"] = df.apply(dummyOrders, axis=1)
    df["ordersWebsite"] = df.apply(dummyOrders, axis=1)
    return df


if __name__ == "__main__":
    # TODO: Figure out the actual opening hours based on the data
    hours = getHoursFor8760Model()
    df = getPreparedDF(hours, getOpeningHours())
    df = addOrders(df)

    print(df)

