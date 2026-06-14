#agents.py

def search_agent(state):
    """Retrieves available seats and updates the state history."""
    available = search_available_seats()
    return {"history": [f"Available seats: {available}"]}

def booking_agent(state):
    """Attempts an atomic booking and returns the status."""
    seat_id = state.get("seat_id")
    user_id = state.get("user_id", "default_user")
    
    # Perform the atomic operation
    result = book_seat_atomic(seat_id, user_id)
    
    # Format the message based on result
    if result is True:
        msg = "Success! Seat booked."
    else:
        msg = f"Failed: {result}"
        
    return {"history": [f"Booking status for seat {seat_id}: {msg}"]}

def cancellation_agent(state):
    """Cancels a booking if the user ID matches."""
    seat_id = state.get("seat_id")
    user_id = state.get("user_id")
    
    success = cancel_booking(seat_id, user_id)
    msg = "Cancellation successful." if success else "Cancellation failed: Not your ticket or seat not booked."
    return {"history": [msg]}
