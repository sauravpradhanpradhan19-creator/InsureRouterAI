"""
Seed the knowledge base with demo policy data.
Run once on startup if no KB exists.
"""
from app.rag.knowledge_base import ingest_text
import logging

logger = logging.getLogger(__name__)

HDFC_POLICY = """
HDFC ERGO Health Suraksha Plus — Policy Wording

SECTION 1: COVERAGE

1.1 Hospitalization Benefits
The policy covers expenses incurred for hospitalization exceeding 24 hours.
Covered expenses include: room rent, ICU charges, surgeon fees, anesthesia, blood, oxygen,
operation theatre charges, medicines, diagnostic tests.

Room rent limit: Single private AC room up to Rs. 5,000 per day.
ICU limit: Up to Rs. 10,000 per day.

1.2 Pre-hospitalization
Medical expenses incurred 30 days before hospitalization are covered.

1.3 Post-hospitalization
Medical expenses incurred 60 days after discharge are covered, up to 10% of hospitalization expenses.

1.4 Day Care Procedures
161 day care procedures covered that do not require 24-hour hospitalization including
cataract surgery, dialysis, chemotherapy, radiotherapy.

1.5 Ambulance Cover
Emergency road ambulance charges covered up to Rs. 2,000 per hospitalization.

SECTION 2: EXCLUSIONS

2.1 Pre-existing Diseases
Pre-existing diseases not covered for first 48 months of continuous coverage.
After 48 months, pre-existing diseases are fully covered.

2.2 Waiting Period
30-day initial waiting period for all illnesses except accidents.
Specific diseases (hernia, cataract, joint replacement) have 2-year waiting period.

2.3 Not Covered
- Cosmetic or aesthetic treatments
- Dental treatment unless due to accident
- Spectacles, contact lenses, hearing aids
- Pregnancy and childbirth (unless opted for maternity add-on)
- Self-inflicted injuries
- Injuries under influence of alcohol or drugs
- Experimental treatments

SECTION 3: CLAIM PROCESS

3.1 Cashless Claims
For network hospitals: Inform insurer 48 hours before planned hospitalization,
3 hours before emergency hospitalization.
Pre-authorization required for planned procedures.

3.2 Reimbursement Claims
Submit claim within 30 days of discharge.
Required documents: Original bills, discharge summary, doctor prescription,
diagnostic reports, claim form, policy copy, ID proof.

3.3 Documents Required for Health Claims
- Completed claim form
- Original hospital bills and receipts
- Discharge certificate / summary
- Doctor's prescription and reports
- Pharmacy bills
- Lab and diagnostic reports
- Policy document copy
- Photo ID of patient

SECTION 4: SUM INSURED AND PREMIUMS

Coverage options: Rs. 3 lakh, 5 lakh, 10 lakh, 15 lakh, 25 lakh, 50 lakh.
Lifelong renewability guaranteed.
No-claim bonus: 10% increase in sum insured for each claim-free year, up to 50%.

SECTION 5: NETWORK HOSPITALS
Over 10,000 network hospitals across India for cashless treatment.
Hospital list available at hdfcergo.com or customer care 1800-2-700-700.
"""

HDFC_MOTOR = """
HDFC ERGO Motor Insurance — Private Car Package Policy

SECTION 1: OWN DAMAGE COVER

1.1 What is Covered
Loss or damage to the insured vehicle due to:
- Accident, fire, explosion, self-ignition, lightning
- Theft, burglary, housebreaking
- Earthquake, flood, cyclone, inundation, tempest
- Riot, strike, malicious act
- Transit by road, rail, inland waterway, air

1.2 Claim Settlement
Insured Declared Value (IDV) is the maximum liability.
IDV = Manufacturer's listed price minus depreciation.

Depreciation schedule:
- Not exceeding 6 months: 5%
- 6 months to 1 year: 15%
- 1 to 2 years: 20%
- 2 to 3 years: 30%
- 3 to 4 years: 40%
- 4 to 5 years: 50%

1.3 Add-on Covers Available
- Zero depreciation (bumper to bumper)
- Engine protection
- Roadside assistance
- Return to invoice
- No claim bonus protection

SECTION 2: THIRD PARTY LIABILITY

Compulsory under Motor Vehicles Act 1988.
Covers legal liability to third parties for:
- Death or bodily injury
- Property damage up to Rs. 7.5 lakh

SECTION 3: EXCLUSIONS — MOTOR

Not covered:
- Wear and tear, mechanical/electrical breakdown
- Damage when driving without valid license
- Driving under influence of alcohol or drugs
- Use of vehicle outside geographical limits
- Consequential loss
- Depreciation (unless zero dep add-on purchased)
- Tyres and tubes (unless vehicle is also damaged)

SECTION 4: MOTOR CLAIM PROCESS

Step 1: Inform HDFC ERGO immediately, call 1800-2-700-700
Step 2: Do not move vehicle before survey (for large damages)
Step 3: File FIR for theft or third-party claims
Step 4: Survey by company's authorized surveyor
Step 5: Submit documents and get repair authorization

Documents Required for Motor Claims:
- Duly filled claim form
- Copy of Registration Certificate (RC)
- Copy of Driving License
- Copy of Insurance Policy
- FIR copy (for theft / third party cases)
- Original repair estimates
- Original bills and payment receipts
- Photos of damaged vehicle

Cashless Repair: Available at 6,800+ network garages across India.
"""

STAR_HEALTH_POLICY = """
Star Health and Allied Insurance — Star Comprehensive Policy

SECTION 1: HEALTH COVERAGE

1.1 In-Patient Hospitalization
Covered for illness and accidents requiring hospitalization more than 24 hours.
Room rent: 1% of sum insured per day for normal room.
ICU: 2% of sum insured per day.

1.2 Coverage Includes
- All medical expenses during hospitalization
- Pre-hospitalization: 60 days before admission
- Post-hospitalization: 90 days after discharge
- Daycare treatments: All daycare procedures covered
- AYUSH treatments: Covered in government hospitals
- Organ donor expenses: Covered for harvesting

1.3 Unique Features
- Automatic restoration of sum insured (100% once per year)
- Health check up covered after 3 claim-free years
- Second medical opinion covered
- Telemedicine consultations covered

SECTION 2: STAR EXCLUSIONS

Not covered under Star Comprehensive:
- Pre-existing diseases for first 36 months
- Initial 30-day waiting period (except accidents)
- Maternity expenses (available as add-on)
- Obesity treatment
- Gender change treatment
- Hazardous activity injuries
- War or nuclear perils

SECTION 3: STAR CLAIM PROCEDURE

3.1 Cashless Facility
Available at 14,000+ network hospitals.
Contact Star Health 24x7 at 044-69006900.
Submit pre-authorization form 4 hours before planned admission.

3.2 Reimbursement Process
Claims must be submitted within 15 days of discharge.
Late submission may result in 25% deduction.

Documents for Star Health Claims:
- Claim form (original)
- Hospital discharge summary (original)
- All original bills and receipts
- Pharmacy bills with doctor's prescription
- Diagnostic test reports
- MLC / FIR (for accident cases)
- Cancelled cheque for NEFT payment

SECTION 4: SUM INSURED OPTIONS
Rs. 5 lakh to Rs. 1 crore.
Family floater available.
Senior citizen plans available up to age 75.
"""

SHARED_REGULATIONS = """
IRDAI INSURANCE REGULATIONS — APPLICABLE TO ALL INSURERS

Claim Settlement Timelines (IRDAI Circular 2024):
- Acknowledgement of claim: Within 3 days
- Survey/assessment completion: Within 30 days of receiving all documents
- Settlement or rejection: Within 45 days of receiving complete documents
- If investigation required: Within 6 months

Consumer Rights:
- Right to receive policy document within 15 days of payment
- Free look period: 15 days to return policy for full refund
- Grievance redressal: Company must respond within 15 days
- IRDAI Ombudsman available for disputes

Standard Claim Definitions:
- Pre-existing disease: Any condition diagnosed before policy inception
- Cashless: Direct payment to hospital by insurer
- Reimbursement: Customer pays and claims back
- Sum insured: Maximum coverage amount
- Premium: Amount paid to keep policy active
- Deductible/Co-pay: Amount customer pays before insurer pays

Documents Always Required (Universal):
- Duly filled and signed claim form
- Copy of valid insurance policy
- Valid government photo ID of insured
- Original bills and receipts
- Doctor's certificate / prescription

Fraud Warning:
- Providing false information is a criminal offence under IPC Section 420
- Fraudulent claims result in policy cancellation and legal action
- Insurer has right to investigate any claim

Customer Helpline: IRDAI toll-free 155255
Ombudsman: www.cioins.co.in
"""


async def seed_demo_kb():
    """Seed demo knowledge base if not already populated."""
    from pathlib import Path
    from app.config import settings

    kb_base = Path(settings.KB_BASE_PATH)
    hdfc_index = kb_base / "demo_hdfc" / "index.faiss"

    if hdfc_index.exists():
        logger.info("Demo KB already seeded — skipping")
        return

    logger.info("Seeding demo knowledge base...")

    # HDFC policies
    ingest_text(HDFC_POLICY, "demo_hdfc", "hdfc_health_suraksha_plus.txt")
    ingest_text(HDFC_MOTOR, "demo_hdfc", "hdfc_motor_package_policy.txt")
    logger.info("✅ HDFC demo KB seeded")

    # Star Health policies
    ingest_text(STAR_HEALTH_POLICY, "demo_star", "star_comprehensive_policy.txt")
    logger.info("✅ Star Health demo KB seeded")

    # Shared regulations
    ingest_text(SHARED_REGULATIONS, "shared", "irdai_regulations.txt")
    logger.info("✅ Shared IRDAI regulations KB seeded")
