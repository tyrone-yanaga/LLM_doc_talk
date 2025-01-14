import os
import fitz
import pdfplumber
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Preformatted


def extract_header_fontsize_from_pdf(pdf_path):
    font_size_counter = Counter()

    with pdfplumber.open(pdf_path) as pdf:
        for i in range(len(pdf.pages)):
            # lines1 = pdf.pages[i].extract_text().split('\n')
            words = pdf.pages[i].extract_words(
                extra_attrs=["fontname", "size"]
                )
            lines = {}

            for word in words:
                line_num = word["top"]
                if line_num not in lines:
                    lines[line_num] = []
                lines[line_num].append(word)

            for line_words in lines.values():
                font_size_counter[line_words[0]["size"]] += 1

    # Find the font sizes that were used more than once
    repeated_sizes = [
        size for size, count in font_size_counter.items() if count > 1
        ]
    print(repeated_sizes)
    # Return the highest font size among the repeated sizes
    if repeated_sizes:
        return max(repeated_sizes)
    else:
        return None


def extract_lines_with_font_size(pdf_path, target_font_size):
    lines_with_target_font_size = []

    with pdfplumber.open(pdf_path) as pdf:
        for i in range(len(pdf.pages)):
            words = pdf.pages[i].extract_words(extra_attrs=["fontname", "size"])
            lines = {}

            for word in words:
                line_num = word["top"]
                if line_num not in lines:
                    lines[line_num] = []
                lines[line_num].append(word)

            for line_num, line_words in lines.items():
                line_font_sizes = [word["size"] for word in line_words]
                if target_font_size in line_font_sizes:
                    line_text = " ".join([word["text"] for word in line_words])
                    lines_with_target_font_size.append(line_text)

    return lines_with_target_font_size


def write_chunks_to_pdf(chunks, output_pdf_path):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    story = []
    for chunk in chunks:
        preformatted = Preformatted(chunk, styles["Normal"])
        story.append(preformatted)

    doc.build(story)


def save_chunks_as_pdfs(chunks, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, chunk in enumerate(chunks, start=1):
        output_pdf_path = os.path.join(output_folder, f"output_pdf_part{i}.pdf")
        write_chunks_to_pdf([chunk], output_pdf_path)
        print(f"PDF saved at: {output_pdf_path}")


def extract_chunks_from_pdf(pdf_path, markers):
    chunks = []
    current_chunk = []
    current_marker_index = 0

    pdf_document = fitz.open(pdf_path)

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text = page.get_text("text")

        lines = text.split("\n")
        for line in lines:
            if (
                current_marker_index < len(markers)
                and markers[current_marker_index] in line
            ):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                current_marker_index += 1

            current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    pdf_document.close()

    output_folder = "output"
    save_chunks_as_pdfs(chunks, output_folder)

    return chunks


def ocr_read(pdf_path):
    pdf1 = "pdf_path"
    extracted_font_size = extract_header_fontsize_from_pdf(pdf1)
    extracted_headers = extract_lines_with_font_size(pdf1, extracted_font_size)
    print(extracted_headers)
    chunks = extract_chunks_from_pdf(pdf1, extracted_headers)
    return chunks
