from datetime import datetime
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

RATING_BANDS = [
    (0, 1200, "#dddddd"),
    (1200, 1400, "#aaffaa"),
    (1400, 1600, "#aaffff"),
    (1600, 1900, "#aaaaff"),
    (1900, 2100, "#ffaaff"),
    (2100, 2300, "#ffcc88"),
    (2300, 2400, "#ffbb55"),
    (2400, 5000, "#ff8888"),
]

LINE_COLOR = "#337ab7"


def render_perf_chart(
    handle: str,
    rating: int | None,
    points: list[tuple[datetime, int]],
) -> BytesIO:
    dates = [point[0] for point in points]
    ratings = [point[1] for point in points]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#eef2f7")
    ax.set_facecolor("#eef2f7")

    y_min = max(500, min(ratings) - 200)
    y_max = min(3500, max(ratings) + 200)
    for low, high, color in RATING_BANDS:
        band_low = max(low, y_min)
        band_high = min(high, y_max)
        if band_low < band_high:
            ax.axhspan(band_low, band_high, color=color, zorder=0)

    ax.plot(
        dates,
        ratings,
        color=LINE_COLOR,
        linewidth=1.5,
        marker="o",
        markersize=5,
        markerfacecolor="white",
        markeredgecolor=LINE_COLOR,
        markeredgewidth=1.2,
        zorder=2,
    )

    ax.set_ylim(y_min, y_max)
    ax.set_xlim(dates[0], dates[-1])
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.yaxis.set_major_locator(plt.MultipleLocator(500))
    ax.grid(True, color="white", linewidth=1.2, zorder=1)
    ax.tick_params(colors="#444444")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    rating_label = rating if rating is not None else "unrated"
    ax.legend(
        [f"{handle} ({rating_label})"],
        loc="upper left",
        frameon=False,
        fontsize=10,
    )

    for spine in ax.spines.values():
        spine.set_color("#cccccc")

    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf
