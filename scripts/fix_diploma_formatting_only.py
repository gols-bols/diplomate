"""
Fix ONLY formatting issues without changing document structure:
- Normalize list formatting (bullets/numbering)
- Remove blue headings (make black)
- Fix font sizes
"""

import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH



def remove_blue_headings(doc: Document) -> None:
    """Change any blue/colored heading text to black."""
    for paragraph in doc.paragraphs:
        style_name = getattr(paragraph.style, "name", "")
        if style_name.startswith("Heading"):
            for run in paragraph.runs:
                # Remove any color-related properties from run
                rPr = run._element.get_or_add_rPr()
                
                # Remove existing color elements
                for color_elem in rPr.findall(qn('w:color')):
                    rPr.remove(color_elem)
                
                # Set color to black explicitly
                run.font.color.rgb = RGBColor(0, 0, 0)
                run.font.bold = True


def normalize_list_formatting(doc: Document) -> None:
    """Ensure list paragraphs have consistent formatting."""
    for paragraph in doc.paragraphs:
        text = (paragraph.text or "").strip()
        style_name = getattr(paragraph.style, "name", "")
        
        # Skip headings
        if style_name.startswith("Heading"):
            continue
        
        # Check if line starts with bullet marker (-, –, —, *, •)
        if text and text[0] in '-–—*•':
            # Ensure it has bullet style
            try:
                paragraph.style = 'List Bullet'
            except:
                pass


def remove_dashes_after_bullets(doc: Document) -> None:
    """Remove em-dashes that appear after bullet markers in list items."""
    import re
    from docx.oxml.ns import qn
    
    for paragraph in doc.paragraphs:
        # Look for list items - check if they have pPr with pStyle pointing to bullet list
        pPr = paragraph._element.get_or_add_pPr()
        pStyle = pPr.find(qn('w:pStyle'))
        
        # Check if it's a bullet/list paragraph
        if pStyle is not None:
            style_val = pStyle.get(qn('w:val'))
            if style_val and ('Bullet' in style_val or 'List' in style_val):
                # This is a list item - process its text
                for run in paragraph.runs:
                    if run.text and run.text.startswith('—'):
                        # Remove leading em-dash with space
                        run.text = re.sub(r'^—\s+', '', run.text)
                        break


def convert_bullets_to_dashes(doc: Document) -> None:
    """Replace bullet markers with an explicit em-dash at the start of the paragraph.
    This removes numbering properties so Word won't render a dot marker, and
    prefixes the line with '— '. Keeps existing formatting of the rest of the runs.
    """
    from docx.oxml.ns import qn

    for paragraph in doc.paragraphs:
        # get or add paragraph properties
        pPr = paragraph._element.get_or_add_pPr()
        if pPr is None:
            continue

        numPr = pPr.find(qn('w:numPr'))
        if numPr is None:
            # also check by style name containing 'List' or 'Bullet'
            style_name = getattr(paragraph.style, 'name', '')
            if 'List' not in style_name and 'Bullet' not in style_name:
                continue
            # if style suggests a list but no numPr, we still prefix

        else:
            # remove numbering so the dot/bullet disappears
            try:
                pPr.remove(numPr)
            except Exception:
                pass

        # prefix with em-dash if not already
        text = (paragraph.text or '').lstrip()
        if not text.startswith('—'):
            if paragraph.runs:
                paragraph.runs[0].text = f'— {paragraph.runs[0].text}'
            else:
                paragraph.add_run('— ')
        # ensure font for visible text
        for run in paragraph.runs:
            if not run.font.name:
                run.font.name = 'Times New Roman'


def _next_id(xml_root, tag):
    """Return next integer id for elements with given tag that have 'w:abstractNumId' or 'w:numId'."""
    vals = []
    for child in xml_root.findall('.//' + tag):
        val = child.get(qn('w:val'))
        try:
            vals.append(int(val))
        except Exception:
            pass
    return (max(vals) + 1) if vals else 1


def add_custom_bullet_numbering(doc: Document, bullet_char: str = '—') -> int:
    """Add a custom bullet numbering (single-level) using bullet_char and return numId."""
    numbering = doc.part.numbering_part.element

    # compute ids
    # find max abstractNumId and numId
    abs_ids = [int(n.get(qn('w:abstractNumId'))) for n in numbering.findall('.//w:abstractNum', namespaces=numbering.nsmap) if n.get(qn('w:abstractNumId'))]
    max_abs = max(abs_ids) + 1 if abs_ids else 1
    num_ids = [int(n.get(qn('w:numId'))) for n in numbering.findall('.//w:num', namespaces=numbering.nsmap) if n.get(qn('w:numId'))]
    max_num = max(num_ids) + 1 if num_ids else 1

    # build abstractNum XML
    abs_xml = f'''<w:abstractNum w:abstractNumId="{max_abs}" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:lvl w:ilvl="0">
        <w:start w:val="1"/>
        <w:numFmt w:val="bullet"/>
        <w:lvlText w:val="{bullet_char}"/>
        <w:lvlJc w:val="left"/>
        <w:pPr>
          <w:ind w:left="720" w:hanging="360"/>
        </w:pPr>
      </w:lvl>
    </w:abstractNum>'''

    abs_elem = parse_xml(abs_xml)
    numbering.append(abs_elem)

    # add num element referencing abstractNum
    num_xml = f'<w:num w:numId="{max_num}" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:abstractNumId w:val="{max_abs}"/></w:num>'
    num_elem = parse_xml(num_xml)
    numbering.append(num_elem)

    return max_num


def apply_numbering_to_dash_paragraphs(doc: Document, numId: int) -> None:
    """Apply numbering with numId to paragraphs that start with an em-dash and remove the leading dash text."""
    for paragraph in doc.paragraphs:
        text = (paragraph.text or '').lstrip()
        if not text.startswith('—'):
            continue

        # remove leading dash from runs
        import re
        if paragraph.runs:
            first = paragraph.runs[0]
            first.text = re.sub(r'^—\s+', '', first.text)

        # add numPr to paragraph
        pPr = paragraph._element.get_or_add_pPr()
        # remove any existing numPr
        for existing in pPr.findall(qn('w:numPr')):
            pPr.remove(existing)
        numPr = parse_xml(f'<w:numPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:ilvl w:val="0"/><w:numId w:val="{numId}"/></w:numPr>')
        pPr.append(numPr)
        # set paragraph style to list bullet if exists
        try:
            paragraph.style = 'List Bullet'
        except Exception:
            pass


def fix_diagram_font_sizes(doc: Document) -> None:
    """Ensure figure captions use 14pt font size."""
    for paragraph in doc.paragraphs:
        text = (paragraph.text or "").strip()
        
        # If it's a figure caption (starts with "Рисунок"), set size to exactly 14pt for ALL runs
        if text.startswith("Рисунок"):
            for run in paragraph.runs:
                run.font.size = Pt(14)
                run.font.name = "Times New Roman"

def normalize_text_font(doc: Document) -> None:
    """Ensure all text uses Times New Roman."""
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if not run.font.name or run.font.name not in ["Times New Roman", "Courier New"]:
                run.font.name = "Times New Roman"


def remove_spellcheck_markup(doc: Document) -> None:
    """Remove red underline marks (proofErr/spellcheck) from all runs."""
    from docx.oxml.ns import qn
    
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            rPr = run._element.get_or_add_rPr()
            # Remove proofErr elements
            for proofErr in rPr.findall(qn('w:proofErr')):
                rPr.remove(proofErr)


def main():
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    
    # Use provided file as is
    doc = Document(str(source))
    
    # Apply ONLY formatting fixes
    remove_blue_headings(doc)
    normalize_list_formatting(doc)
    remove_dashes_after_bullets(doc)
    remove_spellcheck_markup(doc)
    convert_bullets_to_dashes(doc)
    
    # Create custom bullet numbering and apply to paragraphs with dashes
    numId = add_custom_bullet_numbering(doc, bullet_char='—')
    apply_numbering_to_dash_paragraphs(doc, numId)
    
    fix_diagram_font_sizes(doc)
    normalize_text_font(doc)
    
    doc.save(str(output))
    print(f"Formatting fixed: {output}")


if __name__ == "__main__":
    main()
