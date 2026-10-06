import os
import re
import json
from typing import List, Dict, Any
from worker.config import settings
from worker.state import Milestone, StepStatus

class TaskPlanner:
    """
    Decomposes natural language instructions into actionable milestones.
    Supports LLM-based planning with a robust deterministic fallback planner.
    """

    def parse_and_plan(self, prompt: str) -> List[Milestone]:
        # Check if LLM API key is available
        has_api_key = bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)
        
        if has_api_key:
            try:
                import litellm
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a task decomposition engine for an autonomous AI worker. "
                            "Given a user instruction, break it into 3 to 5 logical sequential milestones. "
                            "Output pure JSON list with fields: id (int), title (str), description (str)."
                        )
                    },
                    {"role": "user", "content": f"Instruction: {prompt}"}
                ]
                response = litellm.completion(
                    model=settings.DEFAULT_MODEL,
                    messages=messages,
                    temperature=0.1
                )
                raw_text = response.choices[0].message.content.strip()
                # Clean Markdown fences if present
                clean_json = re.sub(r'^```json\s*|^```\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
                data = json.loads(clean_json)
                if isinstance(data, list) and len(data) > 0:
                    milestones = []
                    for item in data:
                        milestones.append(Milestone(
                            id=item.get("id", len(milestones) + 1),
                            title=item.get("title", f"Milestone {len(milestones) + 1}"),
                            description=item.get("description", ""),
                            status=StepStatus.PENDING
                        ))
                    return milestones
            except Exception:
                # Silently fallback to heuristic planner
                pass

        # Robust Heuristic Decomposition
        vendor_match = re.search(r'(?:from|for)\s+([A-Za-z0-9\s]+?)(?:,|\.|\sand|\sextract|\senter|$)', prompt, re.IGNORECASE)
        vendor = vendor_match.group(1).strip() if vendor_match else "Company X"

        return [
            Milestone(
                id=1,
                title=f"Locate Latest Invoice for {vendor}",
                description=f"Scan local repository and identify the latest valid invoice document for '{vendor}'.",
                status=StepStatus.PENDING
            ),
            Milestone(
                id=2,
                title="Extract Invoice Details",
                description="Parse the document to extract invoice number, total amount, currency, and payment due date.",
                status=StepStatus.PENDING
            ),
            Milestone(
                id=3,
                title="Safety & Risk Assessment",
                description="Evaluate extracted financial data against safety thresholds to determine if human approval is needed.",
                status=StepStatus.PENDING
            ),
            Milestone(
                id=4,
                title="Register Invoice into Internal ERP",
                description="Log into the internal enterprise portal and submit the extracted invoice details into the financial ledger.",
                status=StepStatus.PENDING
            ),
            Milestone(
                id=5,
                title="Outcome Verification & Evidence Generation",
                description="Query the internal system to verify that the record matches the source document and compile audit evidence.",
                status=StepStatus.PENDING
            )
        ]
