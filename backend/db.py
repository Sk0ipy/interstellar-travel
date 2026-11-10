"""SQLite-database: schema en voorbeelddata voor Interstellar Travel."""
import sqlite3
from pathlib import Path

import config

DB_PATH = Path(__file__).parent / "interstellar.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    description TEXT NOT NULL,
    distance TEXT NOT NULL,
    status TEXT NOT NULL,
    beacon_signal TEXT
);
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    destination TEXT NOT NULL,
    departs TEXT NOT NULL,
    duration TEXT NOT NULL,
    price INTEGER NOT NULL,
    seats INTEGER NOT NULL,
    kind TEXT NOT NULL,
    bookable INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    reference TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    flight_code TEXT NOT NULL,
    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS old_bookings (
    id INTEGER PRIMARY KEY,
    reference TEXT NOT NULL,
    passenger TEXT NOT NULL,
    flight_code TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS administrators (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS launches (
    id INTEGER PRIMARY KEY,
    rocket TEXT NOT NULL,
    route TEXT NOT NULL,
    launch_window TEXT NOT NULL,
    pad TEXT NOT NULL,
    status TEXT NOT NULL,
    payload TEXT NOT NULL
);
"""

DESTINATIONS = [
    ("aurora", "Aurora Station", "Noordelijk halfrond",
     "Hoofdstad van de planeet met sterrenhemelterrassen en de grootste markt.", "0,4 uur", "open", None),
    ("halcyon", "Halcyon Dome", "Oostelijke vlakte",
     "Rustige woonkoepel met kassen, parken en uitzicht op de kristalvelden.", "0,6 uur", "open", None),
    ("vesper", "Vesper Ridge", "Westelijke bergrug",
     "Observatorium en radiotelescopen, ideaal voor sterrenkijkers.", "0,9 uur", "open", None),
    ("lumen", "Lumen Colony", "Zuidelijk halfrond",
     "Gloeiende ijsvelden en de beste uitzichten bij nacht.", "1,1 uur", "open", None),
    ("cobalt", "Cobalt Mines", "Achterzijde",
     "Mijnbouwpost; alleen toegankelijk met rondleiding.", "1,5 uur", "open", None),
    ("polaris", "Polaris Outpost", "Zuidpool",
     "Tweede lanceerplek en vrachthaven voor lange routes.", "1,8 uur", "open", None),
    ("kepra", "Kepra Relay", "Maan Kepra",
     "Relaisstation op de maan. Tijdelijk gesloten voor passagiers.", "3,2 uur", "gesloten",
     config.FLAG_HIDDEN),
]

FLIGHTS = [
    ("IT-101", "Aurora Station", "Elke dag 08:00", "0,4 uur", 120, 42, "passagier", 1),
    ("IT-102", "Halcyon Dome", "Elke dag 11:30", "0,6 uur", 150, 30, "passagier", 1),
    ("IT-103", "Vesper Ridge", "Ma / Wo / Vr 14:00", "0,9 uur", 190, 18, "passagier", 1),
    ("IT-104", "Lumen Colony", "Di / Do 16:45", "1,1 uur", 240, 24, "passagier", 1),
    ("IT-105", "Polaris Outpost", "Za 06:00", "1,8 uur", 360, 12, "passagier", 1),
    ("IT-999", "Onbekend (gesloten vracht)", "Niet openbaar", "—", 0, 0, "vracht", 0),
]

OLD_BOOKINGS = [
    ("OB-0412", "J. de Vries", "IT-101", "afgerond"),
    ("OB-0413", "M. Okafor", "IT-103", "afgerond"),
    ("OB-0414", "S. Lindqvist", "IT-102", "geannuleerd"),
    ("OB-0415", "R. Haddad", "IT-104", "afgerond"),
    ("OB-0416", "T. Nakamura", "IT-101", "afgerond"),
]

LAUNCHES = [
    ("IT-01 Voyager", "Launch Base → Aurora Station", "dagelijks 08:00", "Pad A", "gepland", "Passagiers"),
    ("IT-02 Halcyon", "Launch Base → Halcyon Dome", "dagelijks 11:30", "Pad A", "gepland", "Passagiers"),
    ("IT-04 Polaris", "Launch Base → Polaris Outpost", "zaterdag 06:00", "Pad B", "gepland", "Vracht + passagiers"),
    ("IT-999 Kepra", "Launch Base → Kepra Relay", "GECLASSIFICEERD", "Pad A (nacht)", "stil gepland",
     f"Gesloten vracht. Missiecode: {config.FLAG_LAUNCH}"),
]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM administrators").fetchone()[0] == 0:
        conn.execute("INSERT INTO administrators (username, password) VALUES (?, ?)",
                     (config.ADMIN_USER, config.ADMIN_PASSWORD))
    if conn.execute("SELECT COUNT(*) FROM destinations").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO destinations (slug, name, region, description, distance, status, beacon_signal)"
            " VALUES (?,?,?,?,?,?,?)", DESTINATIONS)
        conn.executemany(
            "INSERT INTO flights (code, destination, departs, duration, price, seats, kind, bookable)"
            " VALUES (?,?,?,?,?,?,?,?)", FLIGHTS)
        conn.executemany(
            "INSERT INTO old_bookings (reference, passenger, flight_code, status) VALUES (?,?,?,?)",
            OLD_BOOKINGS)
        conn.executemany(
            "INSERT INTO launches (rocket, route, launch_window, pad, status, payload) VALUES (?,?,?,?,?,?)",
            LAUNCHES)
    conn.commit()
    conn.close()
