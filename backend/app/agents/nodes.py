"""
All agent nodes for the claim routing pipeline.
Each agent takes ClaimState, does one job, returns updated state.
"""
import json
import time
import logging
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from app.config import settings
from app.graph.state import ClaimState
from app.rag.knowledge_base import query_kb

logger = logging.getLogger(__name__)


# ── Shared LLM instances ──────────────────────────────────────────────────────

def get_llm(large: bool = False):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_LARGE if large else settings.GROQ_MODEL,
        temperature=0,
    )


def _trace(state: ClaimState, agent_name: str, status: str,
           input_summary: str, output_summary: str, elapsed_ms: int,
           error: str = None) -> ClaimState:
    """Append an agent trace entry to the state."""
    trace = {
        "agent_name": agent_name,
        "status": status,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "time_ms": elapsed_ms,
        "error": error,
        "timestamp": datetime.utcnow().isoformat(),
    }
    traces = list(state.get("agent_traces", []))
    traces.append(trace)
    return {**state, "agent_traces": traces}


# ── Agent 1: Intake Validator ─────────────────────────────────────────────────

def intake_validator(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "IntakeValidator"
    desc = state["description"]

    issues = []
    if len(desc.strip()) < 20:
        issues.append("Description too short — needs more detail")
    if len(desc) > 3000:
        issues.append("Description too long — will be truncated")
        state = {**state, "description": desc[:3000]}

    critical_keywords = ["death", "died", "fatal", "critical", "emergency", "accident", "fire", "theft"]
    is_urgent = any(kw in desc.lower() for kw in critical_keywords)

    status = "complete"
    output = f"Valid input. Urgent keywords detected: {is_urgent}. Issues: {issues or 'none'}"

    if issues:
        errors = list(state.get("errors", []))
        errors.extend(issues)
        state = {**state, "errors": errors}

    elapsed = int((time.time() - t0) * 1000)
    return _trace(state, agent, status, f"Description length: {len(desc)}", output, elapsed)


# ── Agent 2: Claim Classifier ─────────────────────────────────────────────────

def claim_classifier(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "ClaimClassifier"

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an insurance claim classifier. 
Classify the claim into exactly one type and provide a confidence score.

Claim types:
- health: medical expenses, hospitalization, treatment, medicines
- motor: car/bike accidents, vehicle damage, theft of vehicle  
- property: house/shop damage, fire, flood, burglary of premises
- life: death benefit, term insurance, maturity payment
- travel: flight delays, lost baggage, trip cancellation, medical abroad
- liability: third-party injury or property damage claims

Respond in JSON only:
{{"claim_type": "health|motor|property|life|travel|liability", "confidence": 0.0-1.0, "reason": "brief reason"}}"""),
        ("human", "Claim description: {description}"),
    ])

    llm = get_llm()
    chain = prompt | llm
    result = chain.invoke({"description": state["description"]})

    try:
        data = json.loads(result.content.strip())
        claim_type = data.get("claim_type", "health")
        confidence = float(data.get("confidence", 0.8))
        reason = data.get("reason", "")
    except Exception:
        claim_type = "health"
        confidence = 0.5
        reason = "fallback classification"

    elapsed = int((time.time() - t0) * 1000)
    updated = {**state, "claim_type": claim_type, "claim_type_confidence": confidence}
    return _trace(updated, agent, "complete",
                  state["description"][:100],
                  f"Type: {claim_type} ({confidence:.0%}) — {reason}",
                  elapsed)


# ── Agent 3: Policy Validator ─────────────────────────────────────────────────

def policy_validator(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "PolicyValidator"

    company_slug = state["company_slug"]
    query = f"{state['claim_type']} claim: {state['description']}"

    # RAG retrieval
    docs = query_kb(company_slug, query, k=4)

    if not docs:
        context = "No policy documents found for this company."
        references = []
    else:
        context = "\n\n".join([d.page_content for d in docs])
        references = list(set([d.metadata.get("source", "policy doc") for d in docs]))

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an insurance policy analyst. 
Based on the policy documents provided, determine if the claim is covered.

Policy documents:
{context}

Respond in JSON only:
{{"is_covered": true|false, "coverage_details": "explanation of coverage or why not covered", "conditions": "any conditions or waiting periods that apply", "relevant_clause": "policy section if applicable"}}"""),
        ("human", "Claim type: {claim_type}\nClaim description: {description}"),
    ])

    llm = get_llm()
    chain = prompt | llm
    result = chain.invoke({
        "context": context,
        "claim_type": state.get("claim_type", "health"),
        "description": state["description"],
    })

    try:
        data = json.loads(result.content.strip())
        is_covered = data.get("is_covered", True)
        coverage_details = data.get("coverage_details", "") + " " + data.get("conditions", "")
    except Exception:
        is_covered = True
        coverage_details = "Coverage determination pending manual review."

    elapsed = int((time.time() - t0) * 1000)
    updated = {
        **state,
        "is_covered": is_covered,
        "coverage_details": coverage_details.strip(),
        "policy_references": references,
    }
    return _trace(updated, agent, "complete",
                  f"Query: {query[:80]}",
                  f"Covered: {is_covered}. {coverage_details[:100]}",
                  elapsed)


# ── Agent 4: Fraud Scorer ─────────────────────────────────────────────────────

def fraud_scorer(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "FraudScorer"

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an insurance fraud detection specialist.
Analyze the claim for fraud risk indicators and score 1-5.

Scoring guide:
1 = Very low risk (routine, clear documentation implied, consistent details)
2 = Low risk (minor inconsistencies, common claim type)
3 = Medium risk (some red flags, needs document verification)
4 = High risk (multiple red flags, recommend investigation)
5 = Critical risk (likely fraudulent, escalate immediately)

Red flags to check:
- Vague or inconsistent details
- Very large claim amounts mentioned
- Recent policy purchase before major claim
- Accident described without witnesses or FIR
- Multiple claims pattern (can't detect from description alone but note if mentioned)
- Claim just after policy renewal

Respond in JSON only:
{{"fraud_score": 1-5, "flags": ["list of specific flags found"], "recommendation": "brief recommendation"}}"""),
        ("human", "Policy number: {policy_number}\nClaim type: {claim_type}\nDescription: {description}"),
    ])

    llm = get_llm()
    chain = prompt | llm
    result = chain.invoke({
        "policy_number": state.get("policy_number", "not provided"),
        "claim_type": state.get("claim_type", "unknown"),
        "description": state["description"],
    })

    try:
        data = json.loads(result.content.strip())
        fraud_score = int(data.get("fraud_score", 2))
        flags = data.get("flags", [])
    except Exception:
        fraud_score = 2
        flags = []

    elapsed = int((time.time() - t0) * 1000)
    updated = {**state, "fraud_score": fraud_score, "fraud_flags": flags}
    return _trace(updated, agent, "complete",
                  f"Claim type: {state.get('claim_type')}",
                  f"Fraud score: {fraud_score}/5. Flags: {flags}",
                  elapsed)


# ── Agent 5: Priority Scorer ──────────────────────────────────────────────────

def priority_scorer(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "PriorityScorer"

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an insurance claim priority specialist.
Assign a priority score 1-5 based on urgency.

Scoring:
1 = Low (routine query, no time sensitivity)
2 = Normal (standard claim, process in normal queue)
3 = Medium (customer facing hardship, process within 3 days)
4 = High (significant financial impact, hospitalized customer, process within 24 hours)
5 = Critical (life threatening, emergency, large loss, process immediately)

Consider:
- Life/health implications
- Financial hardship signals
- Whether customer is still in hospital
- Size of likely claim
- Motor accident with injuries = high priority

Respond in JSON only:
{{"priority_score": 1-5, "reason": "explanation"}}"""),
        ("human", "Claim type: {claim_type}\nCovered: {is_covered}\nDescription: {description}"),
    ])

    llm = get_llm()
    chain = prompt | llm
    result = chain.invoke({
        "claim_type": state.get("claim_type", "unknown"),
        "is_covered": state.get("is_covered", True),
        "description": state["description"],
    })

    try:
        data = json.loads(result.content.strip())
        priority_score = int(data.get("priority_score", 2))
        reason = data.get("reason", "Standard priority")
    except Exception:
        priority_score = 2
        reason = "Default priority assigned"

    elapsed = int((time.time() - t0) * 1000)
    updated = {**state, "priority_score": priority_score, "priority_reason": reason}
    return _trace(updated, agent, "complete",
                  f"Type: {state.get('claim_type')}, Covered: {state.get('is_covered')}",
                  f"Priority: {priority_score}/5 — {reason}",
                  elapsed)


# ── Agent 6: Department Router ────────────────────────────────────────────────

DEPARTMENT_MAP = {
    "health": {1: "General Health Desk", 2: "Health Claims Team", 3: "Health Claims Team",
               4: "Senior Health Adjuster", 5: "Emergency Health Response"},
    "motor": {1: "Motor Self-Service", 2: "Motor Claims Team", 3: "Motor Claims Team",
              4: "Senior Motor Adjuster", 5: "Major Accident Response"},
    "property": {1: "Property Desk", 2: "Property Claims Team", 3: "Property Claims Team",
                 4: "Senior Property Adjuster", 5: "Major Loss Response"},
    "life": {1: "Life Claims Desk", 2: "Life Claims Team", 3: "Life Claims Team",
             4: "Senior Life Adjuster", 5: "Life Claims Director"},
    "travel": {1: "Travel Self-Service", 2: "Travel Claims Team", 3: "Travel Claims Team",
               4: "Senior Travel Adjuster", 5: "Emergency Travel Desk"},
    "liability": {1: "Liability Desk", 2: "Liability Claims Team", 3: "Liability Claims Team",
                  4: "Senior Liability Adjuster", 5: "Legal & Liability Director"},
}


def department_router(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "DepartmentRouter"

    claim_type = state.get("claim_type", "health")
    priority = state.get("priority_score", 2)
    fraud_score = state.get("fraud_score", 1)

    if fraud_score >= 4:
        department = "Fraud Investigation Unit"
        status = "flagged"
    elif not state.get("is_covered", True):
        department = "Claims Review Board"
        status = "routed"
    else:
        dept_map = DEPARTMENT_MAP.get(claim_type, DEPARTMENT_MAP["health"])
        department = dept_map.get(min(priority, 5), "General Claims Team")
        status = "routed"

    elapsed = int((time.time() - t0) * 1000)
    updated = {**state, "assigned_department": department, "status": status}
    return _trace(updated, agent, "complete",
                  f"Type: {claim_type}, Priority: {priority}, Fraud: {fraud_score}",
                  f"Routed to: {department} | Status: {status}",
                  elapsed)


# ── Agent 7: Response Composer ────────────────────────────────────────────────

DOCS_BY_TYPE = {
    "health": ["Completed claim form", "Original hospital bills", "Discharge summary",
               "Doctor's prescription", "Lab reports", "Photo ID"],
    "motor": ["Completed claim form", "RC copy", "Driving license copy",
              "FIR copy (if theft/accident)", "Original repair estimates", "Photo ID"],
    "property": ["Completed claim form", "FIR copy", "Photos of damage",
                 "Purchase invoices for damaged items", "Repair estimates", "Photo ID"],
    "life": ["Completed claim form", "Death certificate (original)", "Policy document",
             "Nominee ID proof", "Bank account details", "Medical records"],
    "travel": ["Completed claim form", "Ticket/booking confirmation", "Boarding pass",
               "Delay certificate from airline", "Bills for expenses", "Photo ID"],
    "liability": ["Completed claim form", "FIR / legal notice", "Photos of incident",
                  "Witness statements", "Third-party details", "Photo ID"],
}


def response_composer(state: ClaimState) -> ClaimState:
    t0 = time.time()
    agent = "ResponseComposer"

    claim_type = state.get("claim_type", "health")
    priority = state.get("priority_score", 2)
    fraud_score = state.get("fraud_score", 1)
    department = state.get("assigned_department", "Claims Team")
    is_covered = state.get("is_covered", True)
    coverage_details = state.get("coverage_details", "")

    timelines = {1: "10-15 business days", 2: "7-10 business days",
                 3: "3-5 business days", 4: "24-48 hours", 5: "Immediate — within 4 hours"}
    timeline = timelines.get(priority, "7-10 business days")

    documents = DOCS_BY_TYPE.get(claim_type, DOCS_BY_TYPE["health"])

    if fraud_score >= 4:
        response = f"""Dear {state.get('customer_name') or 'Valued Customer'},

Thank you for submitting your claim (ID: {state['claim_id']}).

Your claim has been received and is currently under additional review by our Fraud Investigation Unit. This is a standard procedure for certain claim types and does not necessarily mean there is an issue.

Our team will contact you within 48 hours to discuss the next steps.

Please keep all original documents and evidence related to your claim.

Reference Number: {state['claim_id']}
Assigned Team: {department}

If you have any questions, please contact our helpline.

Regards,
Claims Processing Team"""
    elif not is_covered:
        response = f"""Dear {state.get('customer_name') or 'Valued Customer'},

Thank you for submitting your claim (ID: {state['claim_id']}).

After reviewing your claim against your policy terms, we have noted the following:

{coverage_details}

Your claim has been forwarded to our Claims Review Board who will conduct a thorough assessment and reach out within {timeline}.

Reference Number: {state['claim_id']}
Assigned Team: {department}

You have the right to appeal this decision. Please contact us if you would like to proceed.

Regards,
Claims Processing Team"""
    else:
        response = f"""Dear {state.get('customer_name') or 'Valued Customer'},

Thank you for submitting your {claim_type} insurance claim (ID: {state['claim_id']}).

We have received your claim and it has been assigned to our {department}.

Coverage Assessment: {coverage_details or 'Your claim appears to be within policy coverage.'}

Expected Timeline: {timeline}

To process your claim, please submit the following documents:
{chr(10).join(f'• {doc}' for doc in documents)}

{"⚠️  This is a high-priority claim. Our team will contact you within 4 hours." if priority >= 4 else ""}

Reference Number: {state['claim_id']}
Track your claim at our portal or call our 24x7 helpline.

Regards,
Claims Processing Team"""

    elapsed = int((time.time() - t0) * 1000)
    updated = {
        **state,
        "customer_response": response,
        "documents_required": documents,
        "estimated_timeline": timeline,
    }
    return _trace(updated, agent, "complete",
                  f"Priority: {priority}, Fraud: {fraud_score}, Covered: {is_covered}",
                  f"Response drafted. Timeline: {timeline}",
                  elapsed)
