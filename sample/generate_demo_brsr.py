"""Generate the synthetic BRSR-style PDF used for local VeriGreen demos."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path(__file__).with_name("sample_brsr_demo.pdf")
INK = colors.HexColor("#17352B")
GREEN = colors.HexColor("#237A57")
PALE = colors.HexColor("#EAF3EE")
MUTED = colors.HexColor("#61736B")
GOLD = colors.HexColor("#D8A64C")
GRID = colors.HexColor("#D9E3DD")


def build_pdf(output_path: Path = OUTPUT) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Kicker", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=8, leading=11, textColor=GREEN, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=29, leading=34, textColor=INK, alignment=TA_LEFT, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, textColor=INK, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="Subhead", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, textColor=GREEN, spaceBefore=8, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodySmall", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9, leading=13, textColor=INK, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Note", parent=styles["BodyText"], fontName="Helvetica-Oblique",
        fontSize=8, leading=11, textColor=MUTED, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=8, leading=10, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="TableCell", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8, leading=10, textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=9, leading=13, textColor=INK,
    ))

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=19 * mm, leftMargin=19 * mm,
        topMargin=19 * mm, bottomMargin=20 * mm,
        title="Synthetic BRSR-Style Demo Disclosure - VanaWeave Textiles",
        author="VeriGreen AI Demo Fixture",
        subject="Fictional ESG disclosure for local audit pipeline testing",
    )

    def p(text: str, style: str = "BodySmall") -> Paragraph:
        return Paragraph(text, styles[style])

    def make_table(headers: list[str], rows: list[list[str]], widths: list[float]) -> Table:
        data = [[p(value, "TableHead") for value in headers]]
        data.extend([[p(value, "TableCell") for value in row] for row in rows])
        table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ("GRID", (0, 0), (-1, -1), 0.45, GRID),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table

    def callout(text: str) -> Table:
        box = Table([[p(text, "Callout")]], colWidths=[172 * mm])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PALE),
            ("BOX", (0, 0), (-1, -1), 0.7, GREEN),
            ("LINEBEFORE", (0, 0), (0, -1), 3, GOLD),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return box

    story = []

    # Cover and reporting profile
    story += [
        Spacer(1, 17 * mm),
        p("SYNTHETIC DEMO DISCLOSURE  /  INDIA", "Kicker"),
        p("Business Responsibility<br/>and Sustainability Report", "CoverTitle"),
        p("BRSR-style ESG disclosure for claim extraction and evidence review", "BodyText"),
        Spacer(1, 7 * mm),
        HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=8 * mm),
        p("VANAWEAVE TEXTILES PRIVATE LIMITED", "SectionTitle"),
        p("Reporting period: 1 April 2025 to 31 March 2026  |  Sector: Textiles and apparel  |  Headquarters: Pune, Maharashtra", "BodySmall"),
        callout("This is a fictional test document created for VeriGreen AI. The company, people, facilities and figures are invented. It is not an actual SEBI filing or investment advice."),
        Spacer(1, 7 * mm),
        p("Reporting profile", "Subhead"),
        p("VanaWeave Textiles Private Limited is a fictional mid-sized manufacturer of cotton and blended fabrics. This disclosure covers its two owned weaving and finishing facilities in Maharashtra. It excludes contract farms, upstream fiber production and downstream product use. The company has not obtained external assurance for the figures in this document unless a row says otherwise.", "BodySmall"),
        p("At a glance", "Subhead"),
        make_table(
            ["Indicator", "FY 2025-26", "FY 2024-25", "Basis / note"],
            [
                ["Employees", "486", "462", "Payroll records at year end"],
                ["Contract workers", "218", "203", "Monthly contractor declarations"],
                ["Electricity from renewable sources", "42%", "27%", "Renewable units divided by purchased units"],
                ["Fresh water withdrawal", "126,000 kL", "139,000 kL", "Facility meter readings"],
                ["Lost-time injuries", "3", "2", "Internal safety register"],
            ],
            [48 * mm, 27 * mm, 27 * mm, 70 * mm],
        ),
        Spacer(1, 5 * mm),
        p("How to use this sample", "Subhead"),
        p("Upload this PDF through the VeriGreen dashboard. It includes specific claims, tables, internal evidence, reporting limitations and a few deliberate inconsistencies so the demo can exercise claim detection and evidence-based scoring. Citations should refer to the printed page numbers.", "BodySmall"),
        PageBreak(),
    ]

    # Environmental disclosures
    story += [
        p("PRINCIPLES 2, 6  /  PAGE 2", "Kicker"),
        p("Environmental performance", "SectionTitle"),
        p("Energy, emissions, water and effluent metrics for the two facilities inside the reporting boundary.", "BodySmall"),
        p("Energy and greenhouse gas emissions", "Subhead"),
        p("The company states that renewable electricity supplied 42% of its purchased electricity in FY 2025-26, up from 27% in the prior year. The underlying energy register records 4.28 GWh of renewable electricity out of 10.20 GWh purchased. The company says rooftop solar meters and utility invoices were reconciled monthly. No third-party assurance was commissioned.", "BodySmall"),
        p("Management also reports an 18% reduction in Scope 1 emissions compared with FY 2024-25. The inventory lists 1,240 tCO2e for FY 2025-26 and 1,510 tCO2e for FY 2024-25. Scope 2 emissions were 6,410 tCO2e and 6,080 tCO2e respectively, using the location-based method. The stated reduction applies to Scope 1 only and does not represent a reduction in total Scope 1 plus Scope 2 emissions.", "BodySmall"),
        make_table(
            ["Environmental metric", "FY 2025-26", "FY 2024-25", "Evidence reference"],
            [
                ["Renewable electricity", "4.28 GWh", "2.91 GWh", "Meter reconciliation log E-04"],
                ["Total purchased electricity", "10.20 GWh", "10.78 GWh", "Utility invoices E-05"],
                ["Scope 1 emissions", "1,240 tCO2e", "1,510 tCO2e", "Fuel register E-11"],
                ["Scope 2 emissions", "6,410 tCO2e", "6,080 tCO2e", "Location-based calculation E-12"],
            ],
            [48 * mm, 30 * mm, 30 * mm, 64 * mm],
        ),
        p("Water stewardship and discharge", "Subhead"),
        p("The sustainability statement says 75% of freshwater withdrawn was reused or recycled. Facility logs record 126,000 kL withdrawn and 86,000 kL reused or recycled, equivalent to approximately 68%. The water balance includes process water only and excludes domestic use. One facility had zero liquid discharge in 11 of 12 months; a maintenance bypass was recorded in September 2025.", "BodySmall"),
        make_table(
            ["Water measure", "Reported value", "Record"],
            [
                ["Freshwater withdrawn", "126,000 kL", "Combined meter ledger E-20"],
                ["Reused / recycled", "86,000 kL", "Treatment plant log E-22"],
                ["Zero-discharge months", "11 of 12", "Effluent register E-24"],
            ],
            [55 * mm, 38 * mm, 79 * mm],
        ),
        Spacer(1, 4 * mm),
        p("Energy and emissions calculations are management estimates. The company has not published a base-year recalculation policy or obtained independent assurance for the water balance.", "Note"),
        PageBreak(),
    ]

    # Social disclosures
    story += [
        p("PRINCIPLES 3, 5  /  PAGE 3", "Kicker"),
        p("People and workplace", "SectionTitle"),
        p("Workforce composition, safety, training and grievance handling for employees and contract workers.", "BodySmall"),
        p("Workforce and inclusion", "Subhead"),
        p("The company employed 486 people at 31 March 2026: 352 permanent employees and 134 fixed-term employees. Women represented 31% of the workforce, compared with 29% in FY 2024-25. There were 218 contract workers engaged during the year. The company says all permanent employees received wages at or above the applicable minimum wage. Contractor wage compliance was checked using a sample of 12 contractors, covering 74% of contract workers.", "BodySmall"),
        make_table(
            ["Workforce indicator", "FY 2025-26", "FY 2024-25", "Evidence reference"],
            [
                ["Permanent employees", "352", "337", "HRIS headcount S-02"],
                ["Fixed-term employees", "134", "125", "HRIS headcount S-02"],
                ["Women in workforce", "31%", "29%", "HRIS demographic report S-04"],
                ["Contract workers", "218", "203", "Contractor returns S-08"],
            ],
            [49 * mm, 28 * mm, 28 * mm, 67 * mm],
        ),
        p("Occupational health and safety", "Subhead"),
        p("Management's opening statement says the company operated a zero lost-time injury workplace during FY 2025-26. The incident register records three lost-time injuries and 41,200,000 hours worked, giving an LTIFR of 0.073 injuries per 1,000,000 hours. No work-related fatalities were recorded. All three incidents were investigated internally; corrective actions were closed for two cases by year end.", "BodySmall"),
        make_table(
            ["Safety indicator", "FY 2025-26", "FY 2024-25", "Evidence reference"],
            [
                ["Work-related fatalities", "0", "0", "Incident register S-12"],
                ["Lost-time injuries", "3", "2", "Incident register S-12"],
                ["Hours worked", "41.2 million", "39.8 million", "Timekeeping summary S-13"],
                ["Employees receiving safety training", "91%", "86%", "Training attendance S-15"],
            ],
            [54 * mm, 25 * mm, 25 * mm, 68 * mm],
        ),
        p("Grievances and training", "Subhead"),
        p("During the year, 34 employee and worker grievances were logged. The grievance register shows 31 closed and three open at 31 March 2026. The annual narrative describes a 97% closure rate. The company does not publish a separate closure rate for contract workers. Safety training attendance covers employees and excludes contractor toolbox talks.", "BodySmall"),
        Spacer(1, 3 * mm),
        p("Worker records are maintained by HR and site safety teams. No independent review of incident classification or grievance closure status was performed.", "Note"),
        PageBreak(),
    ]

    # Governance, limitations, conclusion
    story += [
        p("PRINCIPLES 1, 4, 8  /  PAGE 4", "Kicker"),
        p("Governance and accountability", "SectionTitle"),
        p("Board oversight, business conduct, supplier screening and the limits of this disclosure.", "BodySmall"),
        p("Board oversight", "Subhead"),
        p("The chief executive's message describes the five-member board as fully independent. The board register lists two executive directors, two non-executive promoter directors and one independent non-executive director. One of the five directors is a woman. The board register is maintained by the company secretary and was not externally verified.", "BodySmall"),
        make_table(
            ["Board composition", "Number", "Evidence reference"],
            [
                ["Executive directors", "2", "Board register G-01"],
                ["Non-executive promoter directors", "2", "Board register G-01"],
                ["Independent non-executive directors", "1", "Board register G-01"],
                ["Women directors", "1", "Board register G-01"],
            ],
            [67 * mm, 29 * mm, 76 * mm],
        ),
        p("Ethics and supply chain", "Subhead"),
        p("The company received 34 grievances during FY 2025-26, of which 31 were closed by year end. The annual narrative reports a 97% resolution rate. The register contains three matters marked open as of 31 March 2026. The whistleblower channel received six reports; five were investigated and closed, and one remained under review.", "BodySmall"),
        p("The procurement team screened 78% of active suppliers against its environmental and labor checklist. The chair's message says all suppliers were screened during the reporting year. Screening covered 312 of 400 active suppliers. The company has not completed a human-rights impact assessment across its full supply chain.", "BodySmall"),
        make_table(
            ["Governance / value-chain measure", "Narrative claim", "Underlying record"],
            [
                ["Supplier screening", "100% screened", "312 of 400 suppliers (78%), G-08"],
                ["Grievances closed", "97% resolution", "31 of 34 closed; 3 open, G-11"],
                ["Whistleblower reports", "All handled", "5 closed; 1 under review, G-13"],
            ],
            [54 * mm, 47 * mm, 71 * mm],
        ),
        p("Reporting boundary and limitations", "Subhead"),
        p("This synthetic disclosure covers two owned facilities only. It excludes upstream agricultural production, indirect suppliers beyond the screening sample, product use and end-of-life impacts. Figures are illustrative internal management data, rounded where appropriate, and have not been independently assured. Reported percentages may not reconcile because the sample intentionally contains inconsistencies for audit-pipeline testing.", "BodySmall"),
        Spacer(1, 4 * mm),
        callout("End of synthetic disclosure. All names, records and figures are fictional and intended only for software testing."),
    ]

    def footer(canvas, _doc):
        canvas.saveState()
        page = canvas.getPageNumber()
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.5)
        canvas.line(19 * mm, 15 * mm, A4[0] - 19 * mm, 15 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(19 * mm, 10 * mm, "VANAWEAVE TEXTILES  |  SYNTHETIC DATA FOR TESTING ONLY")
        canvas.drawRightString(A4[0] - 19 * mm, 10 * mm, f"Page {page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
