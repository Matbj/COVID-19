from typing import List

import matplotlib.pyplot as plt

from parse_daily_reports import parse_all_daily_reports, DataPoint

all_data = parse_all_daily_reports()


def get_plot_data(data: List[DataPoint]):
    days = [ts.day for ts in data]
    values = [ts.value for ts in data]
    deltas = [0, *[values[it + 1] - values[it] for it in range(len(values) - 1)]]
    deltas = [delta if delta > 0 else 0 for delta in deltas]
    return days, values, deltas


fig, ax1 = plt.subplots()  # Create a figure containing a single axes.

# sweden_cases = get_plot_data(acc_cases, country_filter=lambda c: c == 'Sweden')
# ax1.plot(sweden_cases[0], sweden_cases[1], "-b")
# ax1.bar(sweden_cases[0], sweden_cases[2], color="b")

country = "US"
cases = get_plot_data(all_data[country].confirmed_time_series)
ax1.plot(cases[0], cases[1], "-go", label="# cases")
ax1.bar(cases[0], cases[2], color="g")
# ax1.set_yscale('log')
ax1.tick_params(axis="y", labelcolor="green")
# ax1.legend(loc="upper left")

ax2 = ax1.twinx()
deaths = get_plot_data(all_data[country].death_time_series)
ax2.plot(deaths[0], deaths[1], "-ro", label="# deaths")
ax2.bar(deaths[0], deaths[2], color="r")
# ax2.set_yscale('log')
ax2.tick_params(axis="y", labelcolor="red")
ax2.legend(loc="center right")

# ax1 = ax1.twinx()
recovered = get_plot_data(all_data[country].recovered_time_series)
ax1.plot(recovered[0], recovered[1], "-bo", label="# recovered")
# ax1.bar(recovered[0], recovered[2], color="b")
# ax1.set_yscale('log')
ax1.tick_params(axis="y", labelcolor="blue")
ax1.legend(loc="center left")


for tick in [*ax1.xaxis.get_major_ticks()]:
    tick.label.set_fontsize(8)
    # specify integer or one of preset strings, e.g.
    # tick.label.set_fontsize('x-small')
    tick.label.set_rotation("vertical")
ax1.grid()

plt.title(f"{country}")
plt.show()
