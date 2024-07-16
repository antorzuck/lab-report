from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Student, Subject, Teacher
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
import PyPDF2



def split_text(text, max_length):
    """Split text into multiple lines to fit within the maximum length."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def add_text_to_pdf(input_pdf_path, output_pdf_path, text_positions):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    for text, position, font_size in text_positions:
        c.setFont("Times-Roman", font_size)
        c.drawString(position[0], position[1], text)

    c.save()
    packet.seek(0)

    with open(input_pdf_path, "rb") as input_pdf_file:
        existing_pdf = PyPDF2.PdfReader(input_pdf_file)
        temp_pdf = PyPDF2.PdfReader(packet)

        output = PyPDF2.PdfWriter()

        for i in range(len(existing_pdf.pages)):
            page = existing_pdf.pages[i]

            if i < len(temp_pdf.pages):
                temp_page = temp_pdf.pages[i]
                page.merge_page(temp_page)

            output.add_page(page)

        with open(output_pdf_path, "wb") as output_pdf_file:
            output.write(output_pdf_file)



def generate_lab_report_pdf(request):
    input_pdf_path = '/home/antorzuck/Desktop/labreport/static/Base.pdf'
    output_directory = '/home/antorzuck/Desktop/labreport/static/generated'

    if request.method == 'POST':
        board_roll = request.POST['board_roll']
        student_info = get_object_or_404(Student, board_roll=board_roll)
        
        num_reports = int(request.POST['num_reports'])
        titles = request.POST['titles'].split(',')
        submission_dates = request.POST['submission_dates'].split(',')

        subject_id = request.POST['subject']
        subject = get_object_or_404(Subject, id=subject_id)

        teacher_id = request.POST['teacher']
        teacher = get_object_or_404(Teacher, id=teacher_id)

        for i in range(num_reports):
            lab_report_no = str(i + 1)
            lab_report_title = titles[i].strip()
            date_of_submission = submission_dates[i].strip()

            title_lines = split_text(lab_report_title, 40)
            title_positions = [(353, 518 - (j * 14), 14) for j in range(len(title_lines))]

            text_positions = [
                *[(line, (pos[0], pos[1]), pos[2]) for line, pos in zip(title_lines, title_positions)],
                (f"{subject.name}", (279, 478), 14),
                (f"{subject.code}", (325, 451), 14),
                (f"{lab_report_no}", (336, 426), 14),
                (f"{date_of_submission}", (371, 403), 12),
                (f"{student_info.name}", (321, 330), 14),
                (f"{student_info.department.name}", (356, 309), 13),
                (f"{student_info.board_roll}", (352, 286), 14),
                (f"{student_info.session}", (330, 263), 14),
                (f"{student_info.semester}", (339, 244), 14),
                (f"{teacher.name}", (288, 165), 19)
            ]

            output_pdf_path = os.path.join(output_directory, f"{subject.name}_Report_{lab_report_no}.pdf")
            add_text_to_pdf(input_pdf_path, output_pdf_path, text_positions)
            print(f"PDF created successfully and saved as {output_pdf_path}.")

        return redirect(f'/static/generated/{subject.name}_Report_{lab_report_no}.pdf')

    else:
        subjects = Subject.objects.all()
        teachers = Teacher.objects.all()

    return render(request, 'report.html', {
        'subjects': subjects,
        'teachers': teachers,
    })
