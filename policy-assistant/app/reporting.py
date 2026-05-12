# from reportlab.lib.pagesizes import LETTER
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# import os

# def generate_policy_pdf(audit_record) -> str:
#     """
#     Generates a professional Audit Report PDF.
#     Contains: Question, Recommendation, and the full Reasoning Trace.
#     """
#     folder = "exports"
#     if not os.path.exists(folder):
#         os.makedirs(folder)
        
#     file_path = os.path.join(folder, f"Audit_{audit_record.id}.pdf")
    
#     c = canvas.Canvas(file_path, pagesize=LETTER)
#     width, height = LETTER

#     # Header
#     c.setFont("Helvetica-Bold", 18)
#     c.setStrokeColor(colors.black)
#     c.drawString(50, height - 50, "PolicyAudit: Explainable Decision Report")
#     c.line(50, height - 60, width - 50, height - 60)

#     # Metadata
#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(50, height - 90, f"Audit ID: {audit_record.id}")
#     c.setFont("Helvetica", 11)
#     c.drawString(50, height - 110, f"Domain: {audit_record.domain}")
#     c.drawString(50, height - 130, f"User ID: {audit_record.user_id}")
#     c.drawString(50, height - 150, f"Timestamp: {audit_record.created_at}")

#     # The Decision
#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(50, height - 190, "FINAL RECOMMENDATION:")
#     c.setFont("Helvetica", 14)
#     c.drawString(70, height - 210, f"> {audit_record.recommendation}")

#     # Reasoning Trace Section
#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(50, height - 250, "REASONING TRACE (Audit Trail):")
    
#     y_position = height - 270
#     for step in audit_record.reasoning_trace:
#         if y_position < 100: # Simple pagination
#             c.showPage()
#             y_position = height - 50
            
#         c.setFont("Helvetica-Bold", 10)
#         c.drawString(60, y_position, f"Step {step['step_number']}: {step['title']}")
#         y_position -= 15
        
#         c.setFont("Helvetica", 9)
#         # Basic text wrap for analysis
#         analysis_text = step['analysis'][:100] + "..." if len(step['analysis']) > 100 else step['analysis']
#         c.drawString(80, y_position, f"Analysis: {analysis_text}")
#         y_position -= 12
#         c.drawString(80, y_position, f"Source: {step.get('source_file', 'Internal Policy')}")
#         y_position -= 25

#     c.save()
#     return file_path