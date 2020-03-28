import csv
import os
import re
from datetime import date, datetime, timedelta
from typing import List, Dict, Union

from pydantic import BaseModel


class DataPoint(BaseModel):
    day: date
    value: int

    def __init__(self, day: date, value: Union[int, str]):
        super().__init__(day=day, value=value if value else 0)


class CountryData(BaseModel):
    country: str
    province: str
    death_time_series: List[DataPoint]
    recovered_time_series: List[DataPoint]
    confirmed_time_series: List[DataPoint]

    def __init__(self, country: str, province: str):
        super().__init__(
            country=country,
            province=province,
            death_time_series=[],
            recovered_time_series=[],
            confirmed_time_series=[],
        )

    def clean_data(self):
        def ensure_positive_trend(data: List[DataPoint]):
            if len(data) < 3:
                return data
            data = sorted(data, key=lambda d: d.day)

            # Combine entries of same day
            previous_data = data
            data = []
            entry = previous_data.pop(0)
            while next_entry := previous_data.pop(0):
                if entry.day == next_entry.day:
                    entry.value += next_entry.value
                    if len(previous_data) == 0:
                        break
                else:
                    data.append(entry)
                    entry = next_entry

                    if len(previous_data) == 0:
                        data.append(next_entry)
                        break

            for it in range(len(data) - 1):
                if data[it + 1].value < data[it].value:
                    data[it + 1].value = data[it].value
            return data
        self.death_time_series = ensure_positive_trend(self.death_time_series)
        self.confirmed_time_series = ensure_positive_trend(self.confirmed_time_series)
        self.recovered_time_series = ensure_positive_trend(self.recovered_time_series)


def csv_to_dict(data) -> List[Dict]:
    output = []
    headers = next(data)
    for row in data:
        output.append({header.strip(): column for header, column in zip(headers, row)})
    return output


def parse_all_daily_reports():
    folder = os.path.join(os.path.dirname(__file__), "./csse_covid_19_data/csse_covid_19_daily_reports")
    output_country_data = {}
    for filename in sorted(os.listdir(folder)):
        if not re.match(r"\d{2}-\d{2}-\d{4}.csv", filename):
            continue
        print(f"Parsing {filename}")
        with open(os.path.join(folder, filename), "r",) as fh:
            date_str = filename.rsplit(".", 1)[0]
            date_match = re.match(r"(\d+)-(\d+)-(\d+)", date_str)
            day = date(year=int(date_match.group(3)), month=int(date_match.group(1)), day=int(date_match.group(2)))
            if day < (datetime.now().date() - timedelta(days=30)):
                continue
            csv_data = csv_to_dict(csv.reader(fh))
            for row in csv_data:
                try:
                    country_name = row["Country/Region"]
                    if country_name not in output_country_data:
                        output_country_data[country_name] = CountryData(
                            country=country_name, province=row.get("Province/State", "")
                        )
                    country_data = output_country_data[country_name]
                    country_data.confirmed_time_series.append(DataPoint(day=day, value=row["Confirmed"]))
                    country_data.death_time_series.append(DataPoint(day=day, value=row["Deaths"]))
                    country_data.recovered_time_series.append(DataPoint(day=day, value=row["Recovered"]))
                except Exception as exc:
                    print(exc, type(exc))

    for cd in output_country_data.values():
        cd.clean_data()

    return output_country_data
