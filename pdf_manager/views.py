from io import BytesIO
from django.shortcuts import render
from django.http import FileResponse
from .forms import ExtractPagesForm, CombinePdfsForm

from .forms import CombinePdfsForm
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF


from django.shortcuts import render
from django.http import FileResponse
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from .forms import ExtractPagesForm


def extract_pages(request):
    if request.method == "POST":
        form = ExtractPagesForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            page_range = form.cleaned_data['page_range'].strip()
            page_type = form.cleaned_data['page_type']

            reader = PdfReader(pdf_file)
            writer = PdfWriter()
            total_pages = len(reader.pages)

            # -----------------------------
            # 1️⃣ Determine which pages to extract
            # -----------------------------
            pages = set()

            if page_range:
                # Case 1: User entered specific page numbers/ranges
                for part in page_range.split(','):
                    part = part.strip()
                    if '-' in part:
                        try:
                            start, end = map(int, part.split('-'))
                            pages.update(range(start, end + 1))
                        except ValueError:
                            continue  # Skip invalid ranges
                    elif part.isdigit():
                        pages.add(int(part))
            else:
                # Case 2: page_range empty → use dropdown
                if page_type == "odd":
                    pages = {i for i in range(1, total_pages + 1) if i % 2 == 1}
                elif page_type == "even":
                    pages = {i for i in range(1, total_pages + 1) if i % 2 == 0}
                else:  # "all"
                    pages = set(range(1, total_pages + 1))

            # -----------------------------
            # 2️⃣ Extract the selected pages
            # -----------------------------
            for p in sorted(pages):
                if 1 <= p <= total_pages:
                    writer.add_page(reader.pages[p - 1])

            # -----------------------------
            # 3️⃣ Return as downloadable PDF
            # -----------------------------
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            return FileResponse(output, as_attachment=True, filename="extracted_pages.pdf")

    else:
        form = ExtractPagesForm()

    return render(request, "pdf_manager/extract_pages.html", {"form": form})


def combine_pdfs(request):
    if request.method == "POST":
        form = CombinePdfsForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('pdf_files')
            add_bookmarks = form.cleaned_data.get('add_bookmarks', False)

            # Create an empty PDF document to hold merged pages
            merged = fitz.Document()
            combined_toc = []   # will hold TOC entries as [level, title, page]

            try:
                for f in files:
                    # Ensure file pointer at start, read bytes
                    try:
                        f.seek(0)
                    except Exception:
                        pass
                    pdf_bytes = f.read()
                    src = fitz.open(stream=pdf_bytes, filetype="pdf")

                    # current page count (PyMuPDF's page numbers for TOC are 1-based)
                    start_page_count = merged.page_count  # 0-based count

                    # Optionally add a top-level bookmark for the file (pointing to first page of this file after merge)
                    if add_bookmarks:
                        # page numbers in TOC are 1-based
                        combined_toc.append([1, f.name[0:-4], start_page_count + 1])

                    # Append pages from src to merged
                    merged.insert_pdf(src)  # inserts whole document at the end

                    # Get source TOC and rebase page numbers
                    # list of [level, title, page] (page is 1-based)
                    src_toc = src.get_toc()
                    if src_toc:
                        for level, title, page in src_toc:
                            new_page = start_page_count + page  # keep 1-based page numbers
                            combined_toc.append(
                                [level + (1 if add_bookmarks else 0), title, new_page])
                            # If add_bookmarks=True we bumped file bookmark as level=1, so we want original levels to be deeper.
                            # Alternatively remove +(1 if add_bookmarks else 0) if you want original levels preserved exactly.

                    src.close()

                # Set combined TOC (if any) — PyMuPDF expects a list of [level, title, page]
                if combined_toc:
                    merged.set_toc(combined_toc)

                # Write merged PDF to memory and return
                merged_bytes = merged.write()
                merged.close()

                output = BytesIO(merged_bytes)
                output.seek(0)

                return FileResponse(output, as_attachment=True, filename="combined.pdf")

            except Exception as e:
                # helpful debug info returned to template
                return render(request, "pdf_manager/combine_pdfs.html", {
                    "form": form,
                    "error": f"Failed to combine PDFs: {e}"
                })
    else:
        form = CombinePdfsForm()

    return render(request, "pdf_manager/combine_pdfs.html", {"form": form})
