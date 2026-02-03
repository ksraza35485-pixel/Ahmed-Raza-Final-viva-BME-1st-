import sqlite3
import hashlib

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

conn = sqlite3.connect("biomed_study.db")
cursor = conn.cursor()

print("Database connected")

cursor.execute("DROP TABLE IF EXISTS Samples")
cursor.execute("DROP TABLE IF EXISTS Clinical_Visits")
cursor.execute("DROP TABLE IF EXISTS Patients")
conn.commit()

print("Old tables dropped (if existed)")

cursor.execute("""
CREATE TABLE Patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name_hash TEXT NOT NULL,
    age INTEGER CHECK(age >= 18 AND age <= 90),
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    enrollment_date TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE Clinical_Visits (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    visit_date TEXT NOT NULL,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    blood_glucose_mmol_L REAL,
    notes TEXT,
    FOREIGN KEY (patient_id)
        REFERENCES Patients(patient_id)
        ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE Samples (
    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    collection_date TEXT NOT NULL,
    sample_type TEXT CHECK(sample_type IN ('Blood', 'Serum', 'Plasma', 'Urine')),
    storage_location TEXT
    FOREIGN KEY (patient_id)
        REFERENCES Patients(patient_id)
        ON DELETE CASCADE
)
""")

conn.commit()
print("Tables created successfully\n")

patients = [
    (hash_text("Ali Khan"), 45, "Male", "2025-01-10"),
    (hash_text("Sara Ahmed"), 38, "Female", "2025-01-15"),
    (hash_text("Usman Raza"), 60, "Male", "2025-01-20")
]

cursor.executemany("""
INSERT INTO Patients (full_name_hash, age, gender, enrollment_date)
VALUES (?, ?, ?, ?)
""", patients)

visits = [
    (1, "2025-02-01", 150, 95, 8.2, "High BP observed"),
    (1, "2025-03-01", 142, 90, 7.9, "BP improving"),
    (2, "2025-02-10", 130, 85, 6.5, "Normal"),
    (3, "2025-02-15", 160, 100, 9.1, "Critical BP")
]

cursor.executemany("""
INSERT INTO Clinical_Visits
(patient_id, visit_date, systolic_bp, diastolic_bp, blood_glucose_mmol_L, notes)
VALUES (?, ?, ?, ?, ?, ?)
""", visits)

samples = [
    (1, "2025-02-01", "Blood", "Fridge A-03"),
    (1, "2025-03-01", "Serum", "Biobank Rack 5"),
    (2, "2025-02-10", "Urine", "Fridge B-02"),
    (3, "2025-02-15", "Plasma", "Biobank Rack 2"),
    (3, "2025-03-10", "Blood", "Fridge C-01")
]

cursor.executemany("""
INSERT INTO Samples
(patient_id, collection_date, sample_type, storage_location)
VALUES (?, ?, ?, ?)
""", samples)

conn.commit()
print("Data inserted successfully\n")

print("All Patients:")
cursor.execute("""
SELECT patient_id, full_name_hash, age, enrollment_date
FROM Patients
""")
for row in cursor.fetchall():
    print(row)

print("\n--------------------------\n")

print("Visits for Patient ID = 1:")
cursor.execute("""
SELECT Patients.patient_id,
       Clinical_Visits.visit_date,
       Clinical_Visits.systolic_bp
FROM Patients
JOIN Clinical_Visits
ON Patients.patient_id = Clinical_Visits.patient_id
WHERE Patients.patient_id = ?
""", (1,))
for row in cursor.fetchall():
    print(row)

print("\n--------------------------\n")

print("Patients with Systolic BP > 140:")
cursor.execute("""
SELECT DISTINCT Patients.patient_id,
                Patients.full_name_hash,
                Clinical_Visits.systolic_bp
FROM Patients
JOIN Clinical_Visits
ON Patients.patient_id = Clinical_Visits.patient_id
WHERE Clinical_Visits.systolic_bp > 140
""")
for row in cursor.fetchall():
    print(row)

print("\n--------------------------\n")

cursor.execute("""
UPDATE Samples
SET storage_location = ?
WHERE sample_id = ?
""", ("Biobank Rack 7", 1))
conn.commit()
print("Sample storage location updated\n")

cursor.execute("""
DELETE FROM Patients WHERE patient_id = ?
""", (2,))
conn.commit()
print("Patient deleted (cascade applied)\n")

print("Remaining Patients:")
cursor.execute("SELECT * FROM Patients")
for row in cursor.fetchall():
    print(row)

conn.close()
print("\nDatabase closed successfully")
