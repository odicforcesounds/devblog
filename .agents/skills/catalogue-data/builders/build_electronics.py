#!/usr/bin/env python3
"""Build the electronics catalogue JSON from Wikipedia.

Defines the taxonomy (category -> group -> component) and asks the Wikipedia API
for each page's canonical title, first sentence and thumbnail, so nothing in the
data is invented. Writes docs/electronics/data/index.json and one file per
category. Re-runnable: the same input produces the same output.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import re
import sys
import time
import urllib.parse

OUT = "docs/electronics/data"
API = "https://en.wikipedia.org/w/api.php"
UA = "MonkeyBlogElectronicsCatalogue/1.0 (https://blog.odicforcesounds.com; oscar@odicforcesounds.com)"

TAXONOMY = [
    ("passives", "01", "Passive components", "Parts that store, resist or filter energy without amplifying it: the resistors, capacitors, inductors and the protection that keeps the rest alive.", [
        ("Resistors", ["Resistor", "Potentiometer", "Photoresistor", "Varistor", "Thermistor", "Trimmer (electronics)", "Shunt (electrical)", "Resistor–capacitor circuit"]),
        ("Capacitors", ["Capacitor", "Ceramic capacitor", "Electrolytic capacitor", "Tantalum capacitor", "Film capacitor", "Supercapacitor", "Variable capacitor", "Decoupling capacitor"]),
        ("Inductors and transformers", ["Inductor", "Choke (electronics)", "Ferrite bead", "Transformer", "Autotransformer", "Current transformer", "Balun", "Flyback transformer"]),
        ("Timing and frequency", ["Crystal oscillator", "Ceramic resonator", "Electronic oscillator", "Voltage-controlled oscillator", "Surface acoustic wave"]),
        ("Protection", ["Fuse (electrical)", "Resettable fuse", "Gas-discharge tube", "Spark gap", "Circuit breaker", "Transient-voltage-suppression diode", "Thermal cutoff", "Electrostatic discharge"]),
    ]),
    ("semiconductors", "02", "Discrete semiconductors", "One junction, one job: diodes that pass one way, transistors that switch or amplify, thyristors that latch, and the parts that turn light into current and back.", [
        ("Diodes", ["Diode", "Rectifier", "Bridge rectifier", "Schottky diode", "Zener diode", "Tunnel diode", "Varicap", "Avalanche diode", "Gunn diode", "Laser diode"]),
        ("Transistors", ["Transistor", "Bipolar junction transistor", "MOSFET", "JFET", "IGBT", "Unijunction transistor", "Darlington transistor", "Phototransistor", "Heterojunction bipolar transistor", "High-electron-mobility transistor"]),
        ("Thyristors and latching switches", ["Thyristor", "TRIAC", "DIAC", "Gate turn-off thyristor", "Silicon controlled rectifier"]),
        ("Light emitters", ["Light-emitting diode", "OLED", "Liquid-crystal display", "Seven-segment display", "Vacuum fluorescent display", "Laser diode"]),
        ("Detectors and imaging", ["Photodiode", "Avalanche photodiode", "Photodetector", "Photomultiplier tube", "Charge-coupled device", "Active-pixel sensor", "Opto-isolator"]),
    ]),
    ("ics", "03", "Integrated circuits", "Whole circuits on a chip: analog blocks, logic, memory, processing and the interface chips that connect a board to the world.", [
        ("Analog building blocks", ["Operational amplifier", "Comparator", "Voltage reference", "Voltage regulator", "Low-dropout regulator", "555 timer IC", "Phase-locked loop", "Sample and hold", "Switched capacitor"]),
        ("Conversion", ["Analog-to-digital converter", "Digital-to-analog converter", "Time-to-digital converter", "Voltage-controlled oscillator"]),
        ("Logic and digital", ["Logic gate", "Flip-flop (electronics)", "Multiplexer", "Shift register", "Counter (digital)", "Arithmetic logic unit", "Programmable logic device"]),
        ("Processors", ["Microprocessor", "Microcontroller", "Digital signal processor", "Field-programmable gate array", "Complex programmable logic device", "Application-specific integrated circuit", "System on a chip"]),
        ("Memory", ["Read-only memory", "Static random-access memory", "Dynamic random-access memory", "Flash memory", "EEPROM", "EPROM", "Ferroelectric RAM", "Magnetoresistive random-access memory", "3D XPoint"]),
        ("Interface and drivers", ["Transceiver", "Line driver", "Gate driver", "H bridge", "Motor controller", "Ethernet physical layer", "Universal asynchronous receiver-transmitter", "Level shifter"]),
        ("Power management", ["Power management integrated circuit", "Buck converter", "Boost converter", "Buck–boost converter", "Charge pump", "Charge controller", "Battery management system", "DC-to-DC converter"]),
    ]),
    ("electromechanical", "04", "Electromechanical", "The parts that move, click and connect: switches, relays, connectors, motors, speakers and the hardware a circuit is mounted on.", [
        ("Switches", ["Switch", "Push-button", "DIP switch", "Rotary switch", "Reed switch", "Mercury switch", "Limit switch", "Membrane switch", "Toggle switch"]),
        ("Relays and contactors", ["Relay", "Reed relay", "Solid-state relay", "Contactor", "Latching relay", "Overload relay"]),
        ("Connectors", ["Electrical connector", "USB", "HDMI", "Modular connector", "XLR connector", "D-subminiature", "BNC connector", "SMA connector", "JST connector", "Banana connector", "Terminal block", "Insulation-displacement connector", "Edge connector", "Pogo pin", "Phone connector (audio)", "RCA connector", "DIN connector", "Serial ATA", "IEC 60320"]),
        ("Motors and actuators", ["Electric motor", "DC motor", "Brushless DC electric motor", "Stepper motor", "Servomotor", "Solenoid", "Linear actuator", "Ultrasonic motor", "Voice coil"]),
        ("Sound and heat", ["Loudspeaker", "Microphone", "Electret microphone", "Buzzer", "Computer fan", "Heat sink", "Thermal grease", "Thermoelectric cooling"]),
    ]),
    ("power", "05", "Power sources and conversion", "Where the current comes from and how it is changed: cells, batteries, supplies, inverters and the boards that distribute what they make.", [
        ("Cells and batteries", ["Electric battery", "Lithium-ion battery", "Lithium polymer battery", "Nickel–metal hydride battery", "Lead–acid battery", "Button cell", "Alkaline battery", "Fuel cell", "Solar cell"]),
        ("Supplies and conversion", ["Power supply", "Switched-mode power supply", "Linear regulator", "Uninterruptible power supply", "Power inverter", "Voltage multiplier", "Transformer", "Rectifier"]),
        ("Distribution and protection", ["Distribution board", "Busbar", "Residual-current device", "Fuse (electrical)", "Circuit breaker", "Schuko", "NEMA connector", "Battery holder"]),
        ("Thermal and harvesting", ["Thermoelectric generator", "Thermoelectric cooling", "Heat sink", "Photovoltaic system"]),
    ]),
    ("rf", "06", "Radio frequency and wireless", "The parts that work in wavelengths: antennas, filters, mixers, amplifiers and the modules that put a signal in the air.", [
        ("Antennas", ["Antenna (radio)", "Dipole antenna", "Monopole antenna", "Patch antenna", "Yagi–Uda antenna", "Parabolic antenna", "Loop antenna", "Helical antenna"]),
        ("Passive RF parts", ["Circulator", "Directional coupler", "Attenuator (electronics)", "Electronic filter", "Waveguide", "Impedance matching", "Radio frequency"]),
        ("Active RF blocks", ["Frequency mixer", "Low-noise amplifier", "RF power amplifier", "Transceiver", "Electronic oscillator", "Phase-locked loop"]),
        ("Wireless modules", ["Bluetooth", "Wi-Fi", "Near-field communication", "RFID", "Zigbee", "LoRa", "Global Positioning System", "Software-defined radio"]),
    ]),
    ("sensors", "07", "Sensors and transducers", "Devices that turn a physical quantity into a signal: heat, motion, pressure, light, gas, current and touch.", [
        ("Temperature", ["Thermocouple", "Resistance thermometer", "Thermistor", "Silicon bandgap temperature sensor", "Infrared thermometer"]),
        ("Motion and position", ["Accelerometer", "Gyroscope", "Magnetometer", "Hall effect sensor", "Rotary encoder", "Linear variable differential transformer", "Proximity sensor", "Ultrasonic transducer"]),
        ("Environment", ["Pressure sensor", "Load cell", "Strain gauge", "Flow sensor", "Gas detector", "Electrochemical gas sensor", "Humidity", "Anemometer", "Geiger counter"]),
        ("Current and magnetic", ["Current sensor", "Current clamp", "Rogowski coil", "Magnetoresistance", "Reed switch"]),
        ("Touch and sound", ["Touchscreen", "Capacitive sensing", "Piezoelectric sensor", "Microphone", "Piezoelectricity"]),
    ]),
    ("assembly", "08", "Boards, packaging and wiring", "What holds a circuit together: the board itself, the packages, the solder, the cable and the box it lives in.", [
        ("Boards", ["Printed circuit board", "Breadboard", "Perfboard", "Stripboard", "Flexible circuit", "Printed electronics"]),
        ("Packages and mounting", ["Through-hole technology", "Surface-mount technology", "Ball grid array", "Dual in-line package", "Small outline integrated circuit", "Quad Flat Package", "Pin header", "Chip carrier"]),
        ("Soldering and wiring", ["Solder", "Solder paste", "Soldering", "Desoldering", "Wire wrap", "Wire", "Electrical cable", "Ribbon cable", "Coaxial cable", "Twisted pair"]),
        ("Enclosures and hardware", ["Electrical enclosure", "DIN rail", "19-inch rack", "Screw", "Cable tie", "Grommet", "Heat-shrink tubing", "Cable gland"]),
    ]),
    ("instruments", "09", "Test and measurement", "The bench: what measures a signal, what generates one, and what joins the two without melting the board.", [
        ("Measuring", ["Multimeter", "Oscilloscope", "Logic analyzer", "Spectrum analyzer", "Network analyzer (electrical)", "LCR meter", "Wattmeter", "Frequency counter", "Time-domain reflectometer", "Clamp meter"]),
        ("Generating", ["Signal generator", "Function generator", "Power supply", "Electronic load"]),
        ("Workbench", ["Soldering iron", "Reflow soldering", "Soldering station", "Solder sucker", "Microscope", "Magnifying glass", "Antistatic device"]),
        ("Reference and design", ["Circuit diagram", "Electronic symbol", "Schematic", "Datasheet", "Electronic color code", "Preferred number", "Application note"]),
    ]),
]


def api(params):
    params = dict(params)
    params["format"] = "json"
    params["formatversion"] = "2"
    url = API + "?" + urllib.parse.urlencode(params)
    import subprocess
    out = subprocess.run(["curl", "-sS", "-A", UA, url], capture_output=True, text=True)
    if not out.stdout:
        raise RuntimeError(out.stderr[:300])
    return json.loads(out.stdout)


def fetch(titles):
    data = {}
    for start in range(0, len(titles), 20):
        chunk = titles[start:start + 20]
        res = api({
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "extracts|pageimages|info",
            "exintro": 1,
            "explaintext": 1,
            "exsentences": 1,
            "exlimit": "max",
            "redirects": 1,
            "piprop": "thumbnail",
            "pithumbsize": 320,
            "inprop": "url",
        })
        query = res.get("query", {})
        pages = {p.get("title"): p for p in query.get("pages", [])}
        norm = {}
        for item in query.get("normalized", []):
            norm[item.get("from")] = item.get("to")
        redir = {}
        for item in query.get("redirects", []):
            redir[item.get("from")] = item.get("to")
        for title in chunk:
            key = norm.get(title, title)
            key = redir.get(key, key)
            page = pages.get(key)
            if not page or page.get("missing"):
                data[title] = None
                continue
            extract = (page.get("extract") or "").strip()
            extract = re.sub(r"\s+", " ", extract)
            first = extract.split(". ")[0]
            if len(first) > 240:
                first = first[:237].rstrip() + "…"
            elif first and not first.endswith("."):
                first += "."
            thumb = (page.get("thumbnail") or {}).get("source")
            if thumb:
                thumb = thumb.split("?")[0]
            data[title] = {
                "n": page.get("title"),
                "u": page.get("fullurl") or ("https://en.wikipedia.org/wiki/" + urllib.parse.quote(page.get("title", "").replace(" ", "_"))),
                "s": first,
                "t": thumb,
            }
        time.sleep(0.3)
    return data


def main():
    all_titles = []
    for _, _, _, _, groups in TAXONOMY:
        for _, items in groups:
            for title in items:
                if title not in all_titles:
                    all_titles.append(title)
    print("titles:", len(all_titles))
    fetched = fetch(all_titles)
    missing = [t for t, v in fetched.items() if not v]
    print("missing:", len(missing))
    for t in missing:
        print("   ", t)

    os.makedirs(OUT, exist_ok=True)
    index = {"components": 0, "groups": 0, "categories": []}
    taken = set()
    for key, num, title, blurb, groups in TAXONOMY:
        out_groups = []
        total = 0
        for name, items in groups:
            entries = []
            seen = set()
            for t in items:
                page = fetched.get(t)
                if not page or page["u"] in taken:
                    continue
                taken.add(page["u"])
                entries.append(page)
            if not entries:
                continue
            out_groups.append({
                "name": name,
                "items": [dict(e, t=e.get("t")) for e in entries],
            })
            total += len(entries)
        doc = {"key": key, "num": num, "title": title, "blurb": blurb,
               "groups": out_groups}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=0)
        with_images = sum(1 for g in out_groups for i in g["items"] if i.get("t"))
        index["categories"].append({
            "key": key, "num": num, "title": title, "blurb": blurb, "slug": key,
            "components": total, "groups": len(out_groups), "images": with_images,
        })
        index["components"] += total
        index["groups"] += len(out_groups)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    print("categories:", len(index["categories"]), "groups:", index["groups"], "components:", index["components"])
    for c in index["categories"]:
        print("   %s %-22s %3d components in %2d groups (%d with an image)" %
              (c["num"], c["title"], c["components"], c["groups"], c["images"]))
    return 0 if not missing else 0


if __name__ == "__main__":
    sys.exit(main())
