def search_available_seats():
    conn = sqlite3.connect("railway.db")
    cursor = conn.cursor()
    # Query only seats that are currently available
    cursor.execute("SELECT seat_id FROM seats WHERE status = 'available'")
    available_seats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return available_seats


def search_agent(state):
    print("Agent: Searching for available seats...")
    available = search_available_seats()  # Logic from database_manager
    return {"history": [f"Available seats are: {available}"]}

# Define the Agent Node for Booking
def booking_agent(state):
    seat_id = state.get("seat_id")
    user_id = state.get("user_id", "default_user")

    # Basic validation for user_id
    if not user_id or not isinstance(user_id, str) or user_id.strip() == "":
        print(f"Agent: Invalid user ID '{user_id}'. Booking failed.")
        return {"history": [f"Booking status for seat {seat_id}: Failed: Invalid user ID."]}

    print(f"Agent: Attempting to book seat {seat_id}...")
    success = book_seat_atomic(seat_id, user_id)

    msg = "Success! Seat booked." if success else "Failed: Seat taken."
    return {"history": [f"Booking status for seat {seat_id}: {msg}"]}

# Define the Agent Node for Cancellations
def cancellation_agent(state):
    seat_id = state.get("seat_id")
    user_id = state.get("user_id")
    
    success = cancel_booking(seat_id, user_id)
    msg = "Cancellation successful." if success else "Cancellation failed: Not your ticket."
    return {"history": [msg]}
