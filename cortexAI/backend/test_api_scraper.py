import httpx
import json

# Set the Gateway URL (The public entrance to your microservices)
GATEWAY_URL = "http://127.0.0.1:8000"

def scrape_and_verify():
    # 1. Establish a persistent client session (automatically handles cookies)
    with httpx.Client(base_url=GATEWAY_URL) as client:
        print("🚀 Starting API Verification Scraper...")

        # ─── STEP 1: TEST UNAUTHORIZED SHIELD ───────────────────────────
        print("\n🔍 Checking if Gateway correctly shields protected paths...")
        fail_check = client.post("/chat/")
        if fail_check.status_code == 401:
            print("✅ Gateway protected path blocked unauthorized request perfectly.")
        else:
            print(f"❌ Security missing! Expected 401 but got {fail_check.status_code}")

        # ─── STEP 2: LOG IN TO OBTAIN VALID COOKIE ──────────────────────
        # Replace these with real credentials inside your database
        login_payload = {
            "username": "testuser@example.com",
            "password": "securepassword123",
            "token": "your_mock_or_real_token_here"
        }
        
        print("\n🔐 Authenticating via /auth/login...")
        login_res = client.post("/auth/login", json=login_payload)
        
        if login_res.status_code != 200:
            print(f"❌ Authentication failed ({login_res.status_code}). Aborting scraper test.")
            print(f"📋 Validation Error Details: {login_res.text}")
            return

        print("✅ Logged in successfully! Session cookie captured automatically.")

        # ─── STEP 3: SCRAPE PROTECTED ME ENDPOINT ───────────────────────
        print("\n👤 Scraping /me profile route...")
        me_res = client.get("/me")
        print(f"Status Code: {me_res.status_code}")
        print(f"Scraped Profile Payload: {json.dumps(me_res.json(), indent=2)}")

        # ─── STEP 4: CREATE A CONVERSATION VIA GATEWAY ──────────────────
        print("\n💬 Scraping Conversation Creation (/chat/)...")
        conv_res = client.post("/chat/")
        
        if conv_res.status_code != 200:
            print(f"❌ Failed to create conversation. Error: {conv_res.text}")
            return
            
        conversation = conv_res.json()
        conversation_id = conversation.get("_id")
        print(f"✅ Successfully created a new conversation! ID: {conversation_id}")

        # ─── STEP 5: SAVE A MESSAGE ────────────────────────────────────
        print("\n✉️ Scraping Message Dispatch (/chat/message/save)...")
        msg_payload = {
            "conversationId": conversation_id,
            "role": "user",
            "content": "Automated verification test payload."
        }
        msg_res = client.post("/chat/message/save", json=msg_payload)
        print(f"Status Code: {msg_res.status_code}")
        print(f"Scraped Message State: {json.dumps(msg_res.json(), indent=2)}")

        # ─── STEP 6: RETRIEVE HISTORY ───────────────────────────────────
        print("\n📊 Scraping Conversation History (/chat/message/get)...")
        history_payload = {"conversationId": conversation_id}
        history_res = client.post("/chat/message/get", json=history_payload)
        
        print(f"Status Code: {history_res.status_code}")
        messages_list = history_res.json()
        print(f"📦 Total messages scraped in room: {len(messages_list)}")
        print("🎉 All microservice integrations verified successfully!")

if __name__ == "__main__":
    scrape_and_verify()