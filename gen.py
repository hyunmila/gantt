import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

csv_path = "notion export gantt"
output_path = "gantt.drawio"

df = pd.read_csv(csv_path)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y")
    except Exception:
        return None

tasks = []
for _, row in df.iterrows():
    date_str = str(row["Date"])
    if "→" in date_str:
        start_str, end_str = date_str.split("→")
        start_date, end_date = parse_date(start_str), parse_date(end_str)
    else:
        start_date = end_date = parse_date(date_str)
    if start_date and end_date:
        duration = (end_date - start_date).days + 1
        tasks.append({
            "Project": row["Project"],
            "Start": start_date,
            "End": end_date,
            "Duration": duration,
            "Status": row["Status"]
        })

min_date = min(t["Start"] for t in tasks) - timedelta(days=2)
max_date = max(t["End"] for t in tasks) + timedelta(days=2)
days_total = (max_date - min_date).days + 1

weeks_per_col = 4
days_per_week = 7
days_per_major = weeks_per_col * days_per_week
max_major_width = 240
minor_cols_per_major = days_per_major // 4
minor_width = max_major_width / minor_cols_per_major

cols_4weeks = list(range(0, days_total, days_per_major))
cols_4days = list(range(0, days_total, 4))
x_timeline = 590
y_start = 60
header_height = 20
row_height = 20

root = ET.Element("mxfile", host="app.diagrams.net", modified=datetime.now().isoformat(), version="20.6.3")
diagram = ET.SubElement(root, "diagram", name="Gantt Chart (4w/4d aligned)")
graph_model = ET.SubElement(diagram, "mxGraphModel")
root_cell = ET.SubElement(graph_model, "root")
ET.SubElement(root_cell, "mxCell", id="0")
ET.SubElement(root_cell, "mxCell", id="1", parent="0")

static_cols = [("No.", 40), ("Project", 250), ("Duration", 80), ("Start", 80), ("ETA", 100)]
x_cursor = 40
for name, width in static_cols:
    cell = ET.SubElement(root_cell, "mxCell", id=f"col_{name}", value=name,
                         style="shape=rectangle;align=center;verticalAlign=middle;fillColor=#CCE5FF;strokeColor=#333;fontStyle=1;",
                         vertex="1", parent="1")
    geom = ET.SubElement(cell, "mxGeometry", x=str(x_cursor), y=str(y_start), width=str(width), height=str(header_height))
    geom.set("as", "geometry")
    x_cursor += width

for i, offset in enumerate(cols_4weeks):
    start = min_date + timedelta(days=offset)
    end = start + timedelta(days=27)
    label = f"{start.strftime('%d %b %y')} - {end.strftime('%d %b %y')}"
    x = x_timeline + (i * max_major_width)
    cell = ET.SubElement(root_cell, "mxCell", id=f"h1_{i}", value=label,
                         style="shape=rectangle;align=center;verticalAlign=middle;fillColor=#DDEEFF;strokeColor=#333;fontSize=10;",
                         vertex="1", parent="1")
    geom = ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y_start), width=str(max_major_width), height=str(header_height))
    geom.set("as", "geometry")

for i, offset in enumerate(cols_4days):
    start = min_date + timedelta(days=offset)
    label = start.strftime("%d %b")

    major_group_index = offset // days_per_major
    within_group_offset = (offset % days_per_major) // 4
    x = x_timeline + major_group_index * max_major_width + within_group_offset * minor_width
    cell = ET.SubElement(root_cell, "mxCell", id=f"h2_{i}", value=label,
                         style="shape=rectangle;align=center;verticalAlign=middle;fillColor=#EEF5FF;strokeColor=#AAA;fontSize=9;",
                         vertex="1", parent="1")
    geom = ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y_start + header_height), width=str(minor_width), height=str(header_height))
    geom.set("as", "geometry")


y_cursor = y_start + 2 * header_height
for i, task in enumerate(tasks, start=1):
    y = y_cursor + (i - 1) * row_height
    vals = [str(i), task["Project"], f"{task['Duration']} d", task["Start"].strftime("%d.%m.%y"), task["End"].strftime("%d.%m.%y")]
    xs = [40, 80, 330, 410, 490]
    ws = [40, 250, 80, 80, 100]
    for j, v in enumerate(vals):
        cell = ET.SubElement(root_cell, "mxCell", id=f"cell_{i}_{j}", value=v,
                             style="shape=rectangle;align=center;verticalAlign=middle;strokeColor=#AAA;fontSize=9;",
                             vertex="1", parent="1")
        geom = ET.SubElement(cell, "mxGeometry", x=str(xs[j]), y=str(y), width=str(ws[j]), height=str(row_height))
        geom.set("as", "geometry")

    total_days_from_start = (task["Start"] - min_date).days
    start_major = total_days_from_start // days_per_major
    day_within_major = total_days_from_start % days_per_major
    x_bar = x_timeline + start_major * max_major_width + (day_within_major / 4) * minor_width
    duration_days = max((task["End"] - task["Start"]).days + 1, 1)
    width_bar = (duration_days / 4) * minor_width
    bar = ET.SubElement(root_cell, "mxCell", id=f"bar_{i}", value="",
                        style="shape=rectangle;rounded=1;fillColor=#89CFF0;strokeColor=#333;",
                        vertex="1", parent="1")
    geom = ET.SubElement(bar, "mxGeometry", x=str(x_bar), y=str(y + 4), width=str(width_bar), height="12")
    geom.set("as", "geometry")

tree = ET.ElementTree(root)
tree.write(output_path, encoding="utf-8", xml_declaration=True)
print(f"Saved to: {output_path}")
