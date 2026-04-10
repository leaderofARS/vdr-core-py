from typing import List, Dict, Any, Optional
from datetime import datetime
from fpdf import FPDF
from ..anchor.solana import get_explorer_url

class ReportOptions:
    """
    Configuration for generating a cryptographic integrity report.
    """
    def __init__(self,
                 anchors: List[Dict[str, Any]],
                 solana_network: str,
                 program_id: str,
                 organization_name: str = 'Organization',
                 date_range_str: str = ''):
        self.anchors = anchors
        self.solana_network = solana_network
        self.program_id = program_id
        self.organization_name = organization_name
        self.date_range_str = date_range_str

class VDRReport(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, 'SipHeron VDR Cryptographic Integrity Report', border=0, align='R')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

async def generate_pdf_report(options: ReportOptions) -> bytes:
    """
    Generates a full PDF integrity report for a set of anchors.
    """
    anchors = options.anchors
    org_name = options.organization_name
    date_range = options.date_range_str
    network = options.solana_network
    program_id = options.program_id

    pdf = VDRReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Cover Page ---
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 24)
    pdf.cell(0, 20, 'Cryptographic Integrity Report', ln=True)
    pdf.ln(10)
    
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, f"Organization: {org_name}", ln=True)
    
    pdf.set_font('helvetica', '', 12)
    if date_range:
        pdf.cell(0, 8, f"Date Range: {date_range}", ln=True)
    pdf.cell(0, 8, f"Total Documents: {len(anchors)}", ln=True)
    pdf.ln(20)

    # --- Executive Summary ---
    anchored_count = len([a for a in anchors if a.get('status') == 'confirmed'])
    revoked_count = len([a for a in anchors if a.get('status') == 'revoked'])
    total_count = len(anchors)

    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(0, 10, 'Executive Summary', ln=True)
    pdf.ln(5)
    
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 8, f"{total_count} documents verified", ln=True)
    
    pdf.set_text_color(0, 128, 0) # Green
    pdf.cell(0, 8, f"{anchored_count} anchored to Solana", ln=True)
    
    if revoked_count > 0:
        pdf.set_text_color(200, 0, 0) # Red
        pdf.cell(0, 8, f"{revoked_count} revoked", ln=True)
    
    pdf.set_text_color(0, 0, 0) # Black
    pdf.ln(20)

    # --- Blockchain Proof Summary ---
    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(0, 10, 'Blockchain Proof Summary', ln=True)
    pdf.ln(5)
    
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 8, f"Solana Network: {network}", ln=True)
    pdf.cell(0, 8, f"Program ID: {program_id}", ln=True)
    pdf.cell(0, 8, f"Total Transactions: {anchored_count}", ln=True)
    pdf.ln(20)

    # --- Instructions ---
    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(0, 10, 'Independent Verification Instructions', ln=True)
    pdf.ln(5)
    pdf.set_font('helvetica', '', 10)
    pdf.multi_cell(180, 5, 'Any independent auditor may verify these documents using the open-source SipHeron CLI or the public Solana explorer by checking the transaction data for the listed SHA-256 hashes.')
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 5, '  sipheron verify --hash <document_hash>', ln=True)
    pdf.ln(10)

    # --- Document Inventory Table ---
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(0, 15, 'Document Inventory Table', ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_font('helvetica', 'B', 10)
    col_width = [35, 45, 25, 25, 50] # Total = 180 (A4 with 15mm margins)
    headers = ['Name', 'Hash', 'Date', 'Status', 'Verify URL']
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], border=1)
    pdf.ln()

    # Table Rows
    pdf.set_font('helvetica', '', 9)
    for a in anchors:
        name = a.get('name', 'Untitled')
        if len(name) > 18: name = name[:15] + '...'
        
        h = a.get('hash', '')
        short_hash = (h[:14] + '...') if len(h) > 17 else h
        
        ts = a.get('timestamp')
        date_str = datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime('%Y-%m-%d') if ts else 'Unknown'
        
        status = str(a.get('status', 'unknown')).upper()
        url = a.get('verificationUrl', '')
        short_url = (url[:22] + '...') if len(url) > 25 else url

        pdf.cell(col_width[0], 8, name, border=1)
        pdf.cell(col_width[1], 8, short_hash, border=1)
        pdf.cell(col_width[2], 8, date_str, border=1)
        pdf.cell(col_width[3], 8, status, border=1)
        
        pdf.set_text_color(0, 0, 204)
        pdf.cell(col_width[4], 8, short_url, border=1, link=url)
        pdf.set_text_color(0, 0, 0)
        pdf.ln()

    # --- Appendix ---
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(0, 15, 'Appendix - Full Proof Details', ln=True)
    pdf.ln(10)

    for a in anchors:
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(180, 8, f"Document: {a.get('name', 'Untitled')}", ln=True)
        pdf.set_font('helvetica', '', 9)
        pdf.multi_cell(180, 5, f"Full Hash (SHA-256): {a.get('hash')}")
        sig = a.get('transactionSignature') or 'None'
        pdf.set_text_color(0, 0, 204)
        pdf.multi_cell(180, 5, f"Solana Transaction: {sig}")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    return bytes(pdf.output())
