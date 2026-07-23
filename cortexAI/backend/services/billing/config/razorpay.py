import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

# Initialize Razorpay Client instance
razorpay_client = razorpay.Client(
    auth = (
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_SECRET_KEY")
    )
)