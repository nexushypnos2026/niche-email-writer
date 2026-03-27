"""
niche-email-writer — FastAPI Backend
Nexus AI Product Line
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Niche Email Writer API", version="0.1.0")

# CORS — allow Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenerateRequest(BaseModel):
    niche: str
    tone: str
    email_type: str
    subject_line: str = ""
    context: str
    cta: str = ""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate_email(req: GenerateRequest):
    """Generate a niche-tailored email using GPT-4o-mini."""

    tone_instruction = {
        "Professional": "polished, business-appropriate",
        "Friendly": "warm, conversational, approachable",
        "Urgent": "compelling, time-sensitive",
        "Casual": "relaxed, informal",
    }.get(req.tone, "professional")

    email_type_instruction = {
        "Cold Outreach": "cold outreach email that grabs attention",
        "Follow-up": "follow-up to a previous email",
        "Newsletter": "engaging newsletter email",
        "Promotional": "promotional email with clear offer",
        "Support Response": "helpful customer support reply",
    }.get(req.email_type, "professional email")

    prompt = f"""You are an expert copywriter specializing in niche email marketing.

Write a {tone_instruction} {email_type_instruction} for someone in the "{req.niche}" niche.

Context: {req.context}
{f"Subject line hint: {req.subject_line}" if req.subject_line else ""}
{f"Call to action: {req.cta}" if req.cta else ""}

Requirements:
- Compelling subject line (if not provided)
- Body max 150 words
- Clear, actionable CTA if applicable
- No spam trigger words
- Professional sign-off (generic "Best regards")

Respond ONLY with JSON in this format:
{{"subject": "...", "body": "..."}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert email copywriter. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        import json
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
