import json
import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        await websocket.send_json({"type": "error", "content": "GEMINI_API_KEY not set in backend environment."})
        await websocket.close()
        return

    # Define tools inside the websocket handler to capture the websocket closure
    # === AMENDED TOOL 1: Added a fallback with clear messaging ===
    async def fetch_ward_allocation(county: str, ward: str) -> str:
        """Simulates pulling granular row details for a ward allocation."""
        await websocket.send_json({
            "type": "tool_call", 
            "tool": "fetch_ward_allocation", 
            "args": {"county": county, "ward": ward}
        })
        
        await asyncio.sleep(1.5)
        
        mock_data = {
            "Nairobi": {
                "Westlands": "Ksh 150,000,000 for road infrastructure and Ksh 50,000,000 for public health.",
                "Kibera": "Ksh 200,000,000 for sanitation and water projects."
            },
            "Mombasa": {
                "Nyali": "Ksh 100,000,000 for street lighting and beach cleaning."
            }
        }
        details = mock_data.get(county, {}).get(ward, f"No specific allocation data found for {ward} in {county}.")
        result = f"Source Document: Approved {county} County Budget Estimate Book. Allocation Details for {ward}: {details}"
        
        await websocket.send_json({
            "type": "tool_result", 
            "tool": "fetch_ward_allocation", 
            "result": result
        })
        return result

    # === AMENDED TOOL 2: Hardcoded explicit dates and tracking metadata ===
    async def check_gazette_amendments(county: str) -> str:
        """Returns recent mock text amendments with explicit publication dates from the Kenya Gazette."""
        await websocket.send_json({
            "type": "tool_call", 
            "tool": "check_gazette_amendments", 
            "args": {"county": county}
        })
        
        await asyncio.sleep(1.0)
        
        # We explicitly bake the Notice Number and exact Date into the string payload
        amendments = {
            "Nairobi": "Kenya Gazette Notice No. 4421 (Published: May 12, 2026): Amendment 24B reallocates Ksh 10,000,000 from transport development to county emergency health services due to recent infrastructure damage from heavy rainfall.",
            "Mombasa": "Kenya Gazette Notice No. 3910 (Published: April 28, 2026): Amendment 12A introduces a budget increase of 5% specifically targeting coastal tourism promotion initiatives."
        }
        result = amendments.get(county, f"No recent gazette amendments or fiscal adjustments found for {county} up to May 2026.")
        
        await websocket.send_json({
            "type": "tool_result", 
            "tool": "check_gazette_amendments", 
            "result": result
        })
        return result

    async def trigger_sms_alert(phone_number: str, message: str) -> str:
        """Formats and prints out a webhook payload designed for an SMS gateway like Africa's Talking."""
        await websocket.send_json({
            "type": "tool_call", 
            "tool": "trigger_sms_alert", 
            "args": {"phone_number": phone_number, "message": message}
        })
        
        await asyncio.sleep(1.0)
        
        payload = {
            "username": "county_watchdog",
            "to": phone_number,
            "message": message,
            "from": "BUDGET_ALERT"
        }
        print(f"--- SIMULATED SMS WEBHOOK PAYLOAD ---")
        print(json.dumps(payload, indent=2))
        print(f"-------------------------------------")
        
        result = f"SMS alert triggered successfully. Payload queued for delivery to mobile sub-terminal {phone_number}."
        
        await websocket.send_json({
            "type": "tool_result", 
            "tool": "trigger_sms_alert", 
            "result": result
        })
        return result

    tools = [fetch_ward_allocation, check_gazette_amendments, trigger_sms_alert]

    client = genai.Client()
    
    # === AMENDED SYSTEM INSTRUCTION: Strict enforcement of citation formatting ===
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction="""You are the 'County Budget Watchdog', an autonomous public finance tracking agent for Kenyan citizens. 
Your core task is to break down technical budgets and legislative adjustments into accessible plain language.

STRICT CRITERIA:
1. When summarizing modifications using your 'check_gazette_amendments' tool, you MUST explicitly cite the exact Gazette Notice number and the specific publication date provided in the raw tool response. 
2. If the data does not specify a timeline, explicitly note that the amendment timeline is unverified. Never skip the citation details.
3. Keep summaries engaging, blending simple English and clear localized context."""
    )
    
    # Use async chat
    chat = client.aio.chats.create(model="gemini-2.5-flash", config=config)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                continue

            await websocket.send_json({"type": "status", "content": "Agent is thinking..."})
            
            response = await chat.send_message(user_message)
            
            await websocket.send_json({
                "type": "message",
                "role": "agent",
                "content": response.text
            })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
