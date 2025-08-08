from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models import Payment, PaymentCreate, PaymentUpdate
from app.auth import get_current_active_user
import razorpay
import os
from fastapi import Header
from app.database import get_database
from app.utils.jwt_handler import verify_access_token

router = APIRouter()

# Mock database - replace with actual database
payments_db = []

razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

@router.post("/", response_model=Payment)
async def create_payment(
    payment: PaymentCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new payment."""
    payment_dict = payment.dict()
    payment_dict["id"] = len(payments_db) + 1
    payment_dict["status"] = "pending"
    payment_dict["created_at"] = "2024-01-01T00:00:00"
    payment_dict["updated_at"] = "2024-01-01T00:00:00"
    
    payments_db.append(payment_dict)
    return payment_dict

@router.post("/create-payment")
async def create_payment(amount: int, current_user=Depends(get_current_active_user)):
    db = get_database()
    # Use current_user info for user_id, fallback to username if id is not present
    user_id = getattr(current_user, 'id', None) or getattr(current_user, 'username', None)
    if not user_id:
        return {"error": "Invalid user token"}
    order = razorpay_client.order.create({"amount": amount*100, "currency": "INR"})
    await db["payments"].insert_one({
        "order_id": order["id"], "user_id": user_id, "amount": amount, "status": "created"
    })
    return order

@router.post("/verify-payment")
async def verify_payment(order_id: str, payment_id: str, signature: str, current_user=Depends(get_current_active_user)):
    db = get_database()
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        await db["payments"].update_one({"order_id": order_id}, {"$set": {"status": "paid"}})
        return {"status": "Payment Verified"}
    except Exception:
        return {"status": "Verification Failed"}

@router.get("/", response_model=List[Payment])
async def get_payments(current_user = Depends(get_current_active_user)):
    """Get all payments for the current user."""
    # In a real app, you'd filter by user_id
    return payments_db

@router.get("/{payment_id}", response_model=Payment)
async def get_payment(
    payment_id: int,
    current_user = Depends(get_current_active_user)
):
    """Get a specific payment by ID."""
    for payment in payments_db:
        if payment["id"] == payment_id:
            return payment
    raise HTTPException(status_code=404, detail="Payment not found")

@router.put("/{payment_id}", response_model=Payment)
async def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update a payment."""
    for payment in payments_db:
        if payment["id"] == payment_id:
            update_data = payment_update.dict(exclude_unset=True)
            payment.update(update_data)
            payment["updated_at"] = "2024-01-01T00:00:00"
            return payment
    raise HTTPException(status_code=404, detail="Payment not found")

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    current_user = Depends(get_current_active_user)
):
    """Delete a payment."""
    for i, payment in enumerate(payments_db):
        if payment["id"] == payment_id:
            del payments_db[i]
            return {"message": "Payment deleted successfully"}
    raise HTTPException(status_code=404, detail="Payment not found")

@router.post("/{payment_id}/process")
async def process_payment(
    payment_id: int,
    current_user = Depends(get_current_active_user)
):
    """Process a payment (mock implementation)."""
    for payment in payments_db:
        if payment["id"] == payment_id:
            if payment["status"] == "pending":
                payment["status"] = "completed"
                payment["updated_at"] = "2024-01-01T00:00:00"
                return {"message": "Payment processed successfully", "payment": payment}
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Payment is not in pending status"
                )
    raise HTTPException(status_code=404, detail="Payment not found") 