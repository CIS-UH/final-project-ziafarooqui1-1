from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

db_config = {
    'host': 'cis3368spring1.cmrcoio4wo0i.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': '123456789..',
    'database': 'cis3368spring1db'
}

def get_db_connection():
    #connection instance
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Connection Error: {e}")
        return None

#mapping membership tiers to numbers to easily handle 'Bronze < Gold' logic
TIER_STRENGTH = {"Bronze": 1, "Silver": 2, "Gold": 3}


#MEMBER MANAGEMENT
@app.route('/members', methods=['GET', 'POST'])
def handle_members():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        #adding a new VIP member to the system
        data = request.json
        query = """
            INSERT INTO member (name, details, title, level)
            VALUES (%s, %s, %s, %s)
        """
        #.get() is used for optional fields like details and title
        cursor.execute(query, (
            data['name'],
            data.get('details'),
            data.get('title'),
            data['level']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Member added successfully"}), 201

    #fetch the full member list for the frontend
    cursor.execute("SELECT * FROM member")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(members), 200


@app.route('/members/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_member(id):
    """Handles operations for a specific member using their unique ID."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM member WHERE id = %s", (id,))
        member = cursor.fetchone()
        cursor.close()
        conn.close()
        if not member:
            return jsonify({"error": "Member not found"}), 404
        return jsonify(member), 200

    if request.method == 'PUT':
        #updating an existing member's profile or membership level
        data = request.json
        query = """
            UPDATE member
            SET name=%s, details=%s, title=%s, level=%s
            WHERE id=%s
        """
        cursor.execute(query, (
            data['name'],
            data.get('details'),
            data.get('title'),
            data['level'],
            id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Member information updated"}), 200

    if request.method == 'DELETE':
        #removing a member foreign key constraints handle related registrations
        cursor.execute("DELETE FROM member WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Member removed from system"}), 200


#EVENT MANAGEMENT
@app.route('/events', methods=['GET', 'POST'])
def handle_events():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.json
        try:
            #creating a new event with a specific level and capacity limit
            query = """
                INSERT INTO event (name, capacity, level, date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['name'],
                data['capacity'],
                data['level'],
                data['date']
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "New event created"}), 201
        except Error:
            #database cannot have two events on the same date
            cursor.close()
            conn.close()
            return jsonify({"error": "An event already exists on this date"}), 400

    cursor.execute("SELECT * FROM event")
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(events), 200


@app.route('/events/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_event(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM event WHERE id=%s", (id,))
        event = cursor.fetchone()
        cursor.close()
        conn.close()
        if not event:
            return jsonify({"error": "Event not found"}), 404
        return jsonify(event), 200

    if request.method == 'PUT':
        data = request.json
        query = """
            UPDATE event
            SET name=%s, capacity=%s, level=%s, date=%s
            WHERE id=%s
        """
        cursor.execute(query, (
            data['name'],
            data['capacity'],
            data['level'],
            data['date'],
            id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Event details updated"}), 200

    if request.method == 'DELETE':
        cursor.execute("DELETE FROM event WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Event has been cancelled"}), 200


#REGISTRATION

@app.route('/registrations', methods=['GET', 'POST'])
def handle_registrations():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.json

        #check if the member has a high enough tier for this event
        cursor.execute("SELECT level FROM member WHERE id=%s", (data['member_id'],))
        member = cursor.fetchone()

        #check current event occupancy vs max capacity
        #subquery counts existing registrations to ensure we don't oversell
        cursor.execute("""
            SELECT level, capacity,
            (SELECT COUNT(*) FROM registration WHERE event_id=%s) as count
            FROM event WHERE id=%s
        """, (data['event_id'], data['event_id']))
        event = cursor.fetchone()

        if not member or not event:
            cursor.close()
            conn.close()
            return jsonify({"error": "Member or Event record missing"}), 404

        #access control based on membership level
        if TIER_STRENGTH[member['level']] < TIER_STRENGTH[event['level']]:
            cursor.close()
            conn.close()
            return jsonify({"error": "Your level is too low for this event"}), 403

        #capacity limit check
        if event['count'] >= event['capacity']:
            cursor.close()
            conn.close()
            return jsonify({"error": "This event is currently full"}), 400

        try:
            #registering the members unique constraint in SQL prevents double-signing
            cursor.execute(
                "INSERT INTO registration (event_id, member_id) VALUES (%s, %s)",
                (data['event_id'], data['member_id'])
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "Successfully registered for the event"}), 201
        except Error:
            #catching duplicate registrations
            cursor.close()
            conn.close()
            return jsonify({"error": "You are already registered for this event"}), 400

    #retrieve all registrations joined with names for better visibility
    cursor.execute("""
        SELECT r.id, m.name as member_name, e.name as event_name
        FROM registration r
        JOIN member m ON r.member_id = m.id
        JOIN event e ON r.event_id = e.id
    """)
    registrations = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(registrations), 200


@app.route('/registrations/<int:id>', methods=['GET', 'DELETE'])
def handle_single_registration(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM registration WHERE id=%s", (id,))
        registration = cursor.fetchone()
        cursor.close()
        conn.close()
        if not registration:
            return jsonify({"error": "Registration record not found"}), 404
        return jsonify(registration), 200

    if request.method == 'DELETE':
        #allow users to unregister from events
        cursor.execute("DELETE FROM registration WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Registration cancelled"}), 200


if __name__ == '__main__':
    #Starting the Flask API service on port 5000
    app.run(debug=True, port=5000)