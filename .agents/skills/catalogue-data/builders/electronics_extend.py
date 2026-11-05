#!/usr/bin/env python3
"""Add the electronic parts the catalogue lacks.

build_electronics.py writes the whole catalogue from its taxonomy; this pass
reads the finished shelves, asks Wikipedia only for the titles below, files each
under its category and group, and recomputes the counts. A page already present
is skipped, so a second run changes nothing.

    python3 .agents/skills/catalogue-data/builders/electronics_extend.py
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import sys
import time

import build_electronics as be

OUT = be.OUT

# category key | group name | article title
EXTRA = [
    ("passives", "Resistors", "Metal-film resistor"),
    ("passives", "Resistors", "Wirewound resistor"),
    ("passives", "Resistors", "Current sense resistor"),
    ("passives", "Capacitors", "Feedthrough capacitor"),
    ("passives", "Inductors and transformers", "Magnetic core"),
    ("passives", "Inductors and transformers", "Litz wire"),
    ("passives", "Timing and frequency", "Crystal filter"),
    ("semiconductors", "Diodes", "PIN diode"),
    ("semiconductors", "Diodes", "Step recovery diode"),
    ("semiconductors", "Diodes", "IMPATT diode"),
    ("semiconductors", "Transistors", "Power MOSFET"),
    ("semiconductors", "Transistors", "Silicon carbide"),
    ("semiconductors", "Transistors", "Gallium nitride"),
    ("semiconductors", "Detectors and imaging", "Image sensor"),
    ("ics", "Logic and digital", "Watchdog timer"),
    ("ics", "Logic and digital", "Real-time clock"),
    ("ics", "Logic and digital", "Digital potentiometer"),
    ("ics", "Processors", "Graphics processing unit"),
    ("ics", "Processors", "Tensor processing unit"),
    ("ics", "Processors", "Network processor"),
    ("ics", "Processors", "Digital signal controller"),
    ("ics", "Memory", "Memory controller"),
    ("electromechanical", "Motors and actuators", "Solenoid valve"),
    ("electromechanical", "Motors and actuators", "Piezoelectric motor"),
    ("electromechanical", "Motors and actuators", "Linear motor"),
    ("electromechanical", "Connectors", "RF connector"),
    ("electromechanical", "Connectors", "Crimp connector"),
    ("power", "Cells and batteries", "Battery charger"),
    ("power", "Supplies and conversion", "Variac"),
    ("power", "Supplies and conversion", "Isolation transformer"),
    ("power", "Supplies and conversion", "Solar inverter"),
    ("power", "Distribution and protection", "Power over Ethernet"),
    ("rf", "Passive RF parts", "Cavity resonator"),
    ("rf", "Active RF blocks", "RF switch"),
    ("rf", "Wireless modules", "Beamforming"),
    ("rf", "Wireless modules", "MIMO"),
    ("sensors", "Environment", "Lidar"),
    ("sensors", "Environment", "Rain sensor"),
    ("sensors", "Environment", "Soil moisture sensor"),
    ("sensors", "Motion and position", "Time-of-flight camera"),
    ("assembly", "Boards", "Solder mask"),
    ("assembly", "Boards", "Silkscreen"),
    ("assembly", "Boards", "Conformal coating"),
    ("assembly", "Enclosures and hardware", "Cable harness"),
    ("instruments", "Measuring", "Power analyzer"),
    ("instruments", "Measuring", "Test probe"),
    ("instruments", "Generating", "Frequency response analyzer"),
    ("microelectronics", "Fabrication", "Photomask"),
    ("microelectronics", "Fabrication", "Wafer bonding"),
    ("microelectronics", "Die and packaging", "Through-silicon via"),
    ("industrial", "Control and drives", "Distributed control system"),
    ("industrial", "Control and drives", "SCADA"),
    ("industrial", "Process sensing", "PID controller"),
    ("industrial", "Process sensing", "Safety instrumented system"),
]


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    categories = {}
    for entry in index["categories"]:
        doc = json.load(open(os.path.join(OUT, entry["key"] + ".json"), encoding="utf-8"))
        categories[entry["key"]] = {
            "entry": entry, "doc": doc,
            "groups": {group["name"]: group["items"] for group in doc["groups"]},
        }

    existing = {item["u"] for state in categories.values()
                for items in state["groups"].values() for item in items}
    titles = []
    for _key, _group, title in EXTRA:
        if title not in titles:
            titles.append(title)
    fetched = be.fetch(titles)
    missing = [title for title in titles if not fetched.get(title)]
    for title in missing:
        print("  !", title, "not found")
    time.sleep(0.3)

    added = 0
    for key, group_name, title in EXTRA:
        page = fetched.get(title)
        if not page:
            continue
        if page["u"] in existing:
            print("  =", title, "already shelved")
            continue
        existing.add(page["u"])
        state = categories[key]
        state["groups"].setdefault(group_name, []).append(
            {"n": page["n"], "u": page["u"], "s": page["s"], "t": page.get("t")})
        added += 1
        print("  +", page["n"], "->", state["entry"]["title"], "/", group_name)

    for key, state in categories.items():
        doc = state["doc"]
        doc["groups"] = [
            {"name": name, "items": sorted(items, key=lambda item: item["n"])}
            for name, items in state["groups"].items() if items
        ]
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=0)
        components = sum(len(group["items"]) for group in doc["groups"])
        state["entry"]["components"] = components
        state["entry"]["groups"] = len(doc["groups"])
        state["entry"]["images"] = sum(1 for group in doc["groups"]
                                       for item in group["items"] if item.get("t"))

    index["categories"].sort(key=lambda entry: entry["num"])
    index["components"] = sum(entry["components"] for entry in index["categories"])
    index["groups"] = sum(entry["groups"] for entry in index["categories"])
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    print("added:", added)
    print("index:", {k: index[k] for k in ("components", "groups")},
          "categories:", len(index["categories"]))


if __name__ == "__main__":
    sys.exit(main())
