import mysql.connector

# ---------- DATABASE CONNECTION ----------
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password",
            database="medisync"
        )
        print("Connected to MediSync+ Clinic Database.")
        return connection
    except Exception as err:
        print(f"Database connection error: {err}")
        return None

def execute_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        if cursor.with_rows:
            return cursor.fetchall()
        else:
            connection.commit()
    except Exception as err:
        print(f"Query execution error: {err}")
    finally:
        cursor.close()

# ---------- LOGIN & REGISTRATION ----------
def register_user(connection):
    print("\n--- Register New User ---")
    name = input("Name: ")
    email = input("Email: ")
    username = input("Username: ")
    password = input("Password: ")
    role = input("Role (patient/doctor/admin): ").strip().lower()
    contact_info = input("Contact Info: ")

    query = """
    INSERT INTO User (name, email, username, password, role, contact_info)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    execute_query(connection, query, (name, email, username, password, role, contact_info))
    print("User registered successfully.")

    if role == 'patient':
        user_id = get_user_id_by_username(connection, username)
        query = "INSERT INTO Patient (patient_id) VALUES (%s)"
        execute_query(connection, query, (user_id,))
    elif role == 'doctor':
        specialization = input("Enter your specialization ID: ")
        experience = int(input("Years of experience: "))
        user_id = get_user_id_by_username(connection, username)
        query = "INSERT INTO Doctor (doctor_id, specialization_id, years_of_experience) VALUES (%s, %s, %s)"
        execute_query(connection, query, (user_id, specialization, experience))

def get_user_id_by_username(connection, username):
    query = "SELECT user_id FROM User WHERE username = %s"
    result = execute_query(connection, query, (username,))
    return result[0][0] if result else None

def login_user(connection):
    username = input("Username: ")
    password = input("Password: ")
    query = "SELECT * FROM User WHERE username = %s AND password = %s"
    result = execute_query(connection, query, (username, password))
    if result:
        print(f"Welcome, {result[0][1]} ({result[0][5]})")
        return result[0]
    else:
        print("Invalid credentials.")
        return None

# ---------- PATIENT FUNCTIONALITY ----------
def book_appointment(connection, patient_id):
    print("\n--- Book Appointment ---")
    doctor_id = input("Doctor ID: ")
    date = input("Date (YYYY-MM-DD): ")
    time = input("Time (HH:MM:SS): ")
    query = """
    INSERT INTO Appointment (doctor_id, patient_id, appointment_date, appointment_time, status)
    VALUES (%s, %s, %s, %s, 'scheduled')
    """
    execute_query(connection, query, (doctor_id, patient_id, date, time))
    print("Appointment booked.")

def cancel_appointment(connection, patient_id):
    print("\n--- Cancel Appointment ---")
    appt_id = input("Appointment ID: ")
    query = """
    UPDATE Appointment SET status = 'cancelled' WHERE appointment_id = %s AND patient_id = %s
    """
    execute_query(connection, query, (appt_id, patient_id))
    print("Appointment cancelled.")

def view_patient_appointments(connection, patient_id):
    print("\n--- Your Appointments ---")
    query = """
    SELECT a.appointment_id, u.name AS doctor_name, a.appointment_date, a.appointment_time, a.status
    FROM Appointment a
    JOIN Doctor d ON a.doctor_id = d.doctor_id
    JOIN User u ON d.doctor_id = u.user_id
    WHERE a.patient_id = %s
    """
    results = execute_query(connection, query, (patient_id,))
    for row in results:
        print(row)

# ---------- DOCTOR FUNCTIONALITY ----------
def view_doctor_appointments(connection, doctor_id):
    print("\n--- Doctor Appointments ---")
    query = """
    SELECT a.appointment_id, u.name AS patient_name, a.appointment_date, a.appointment_time, a.status
    FROM Appointment a
    JOIN Patient p ON a.patient_id = p.patient_id
    JOIN User u ON p.patient_id = u.user_id
    WHERE a.doctor_id = %s
    """
    results = execute_query(connection, query, (doctor_id,))
    for row in results:
        print(row)

def add_medical_record(connection, doctor_id):
    print("\n--- Add Medical Record ---")
    appt_id = input("Appointment ID: ")
    patient_id = input("Patient ID: ")
    diagnosis = input("Diagnosis: ")
    notes = input("Notes: ")
    query = """
    INSERT INTO MedicalRecord (appointment_id, patient_id, diagnosis, notes)
    VALUES (%s, %s, %s, %s)
    """
    execute_query(connection, query, (appt_id, patient_id, diagnosis, notes))
    print("Medical record added.")

def issue_prescription(connection, doctor_id):
    print("\n--- Issue Prescription ---")
    patient_id = input("Patient ID: ")
    medication = input("Medication: ")
    dosage = input("Dosage: ")
    duration = input("Duration: ")
    query = """
    INSERT INTO Prescription (doctor_id, patient_id, medication_name, dosage, duration)
    VALUES (%s, %s, %s, %s, %s)
    """
    execute_query(connection, query, (doctor_id, patient_id, medication, dosage, duration))
    print("Prescription added.")

# ---------- ADMIN FUNCTIONALITY ----------
def admin_menu(connection):
    while True:
        print("\n--- Admin Menu ---")
        print("1. View Tables")
        print("2. View Table Content")
        print("3. Delete Record")
        print("4. Alter Record")
        print("5. Exit Admin Menu")
        choice = input("Choice: ")

        if choice == "1":
            tables = execute_query(connection, "SHOW TABLES")
            for t in tables:
                print(t[0])
        elif choice == "2":
            table = input("Table name: ")
            rows = execute_query(connection, f"SELECT * FROM {table}")
            for r in rows:
                print(r)
        elif choice == "3":
            table = input("Table name: ")
            id_col = input("ID Column name: ")
            record_id = input("ID to delete: ")
            execute_query(connection, f"DELETE FROM {table} WHERE {id_col} = %s", (record_id,))
            print("Record deleted.")
        elif choice == "4":
            table = input("Table: ")
            id_col = input("ID Column name: ")
            record_id = input("ID: ")
            column = input("Column to update: ")
            value = input("New value: ")
            query = f"UPDATE {table} SET {column} = %s WHERE {id_col} = %s"
            execute_query(connection, query, (value, record_id))
            print("Record updated.")
        elif choice == "5":
            break
        else:
            print("Invalid option.")

# ---------- MAIN MENU ----------
def main():
    connection = create_db_connection()
    if not connection:
        return

    user = None
    while True:
        if not user:
            print("\n--- MediSync+ Login ---")
            print("1. Login\n2. Register\n3. Exit")
            choice = input("Choice: ")
            if choice == "1":
                user = login_user(connection)
            elif choice == "2":
                register_user(connection)
            elif choice == "3":
                break
            else:
                print("Invalid choice.")
        else:
            role = user[5]
            if role == "patient":
                print("\n--- Patient Menu ---")
                print("1. Book Appointment\n2. Cancel Appointment\n3. View Appointments\n4. Logout")
                choice = input("Choice: ")
                if choice == "1":
                    book_appointment(connection, user[0])
                elif choice == "2":
                    cancel_appointment(connection, user[0])
                elif choice == "3":
                    view_patient_appointments(connection, user[0])
                elif choice == "4":
                    user = None
            elif role == "doctor":
                print("\n--- Doctor Menu ---")
                print("1. View Appointments\n2. Add Medical Record\n3. Issue Prescription\n4. Logout")
                choice = input("Choice: ")
                if choice == "1":
                    view_doctor_appointments(connection, user[0])
                elif choice == "2":
                    add_medical_record(connection, user[0])
                elif choice == "3":
                    issue_prescription(connection, user[0])
                elif choice == "4":
                    user = None
            elif role == "admin":
                password = input("Enter Admin Passcode: ")
                if password == "1337":
                    admin_menu(connection)
                else:
                    print("Access Denied.")
                user = None

    connection.close()

if __name__ == "__main__":
    main()
