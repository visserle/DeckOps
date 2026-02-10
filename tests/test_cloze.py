"""Tests for DeckOpsCloze support: parsing, formatting, and round-trip."""

import pytest

from deckops.config import CARD_SEPARATOR, NOTE_TYPES
from deckops.html_converter import HTMLToMarkdown
from deckops.markdown_converter import MarkdownToHTML
from deckops.markdown_helpers import (
    extract_card_blocks,
    format_card,
    parse_card_block,
    validate_card,
)


class TestParseClozBlock:
    """Test parse_card_block with DeckOpsCloze blocks."""

    def test_cloze_with_note_id(self):
        block = (
            "<!-- note_id: 789 -->\n"
            "T: The capital of {{c1::France}} is {{c2::Paris}}\n"
            "E: Geography fact"
        )
        card = parse_card_block(block, 1)
        assert card.note_id == 789
        assert card.card_id is None
        assert card.note_type == "DeckOpsCloze"
        assert card.fields["Text"] == "The capital of {{c1::France}} is {{c2::Paris}}"
        assert card.fields["Extra"] == "Geography fact"

    def test_cloze_without_id_detected_from_prefix(self):
        block = "T: This is a {{c1::cloze}} test\nE: Extra"
        card = parse_card_block(block, 1)
        assert card.note_id is None
        assert card.card_id is None
        assert card.note_type == "DeckOpsCloze"
        assert card.fields["Text"] == "This is a {{c1::cloze}} test"

    def test_cloze_with_hint(self):
        block = (
            "<!-- note_id: 100 -->\n"
            "T: The {{c1::mitochondria::organelle}} is the powerhouse of the cell"
        )
        card = parse_card_block(block, 1)
        assert card.note_type == "DeckOpsCloze"
        assert "{{c1::mitochondria::organelle}}" in card.fields["Text"]

    def test_cloze_multiline_text(self):
        block = (
            "<!-- note_id: 200 -->\n"
            "T: First line with {{c1::cloze}}\n"
            "Second line continues\n"
            "E: Some extra info"
        )
        card = parse_card_block(block, 1)
        assert card.note_type == "DeckOpsCloze"
        assert (
            "First line with {{c1::cloze}}\nSecond line continues"
            == card.fields["Text"]
        )

    def test_cloze_all_fields(self):
        block = "<!-- note_id: 300 -->\nT: {{c1::Answer}}\nE: Extra\nM: More info"
        card = parse_card_block(block, 1)
        assert card.fields["Text"] == "{{c1::Answer}}"
        assert card.fields["Extra"] == "Extra"
        assert card.fields["More"] == "More info"

    def test_cloze_text_only(self):
        block = "<!-- note_id: 400 -->\nT: Just {{c1::text}}"
        card = parse_card_block(block, 1)
        assert card.note_type == "DeckOpsCloze"
        assert len(card.fields) == 1
        assert card.fields["Text"] == "Just {{c1::text}}"


class TestParseQABlock:
    """Verify DeckOpsQA still works after refactoring."""

    def test_qa_with_card_id(self):
        block = "<!-- card_id: 123 -->\nQ: What?\nA: This"
        card = parse_card_block(block, 1)
        assert card.card_id == 123
        assert card.note_id is None
        assert card.note_type == "DeckOpsQA"
        assert card.fields["Question"] == "What?"
        assert card.fields["Answer"] == "This"

    def test_qa_without_id(self):
        block = "Q: New question\nA: New answer"
        card = parse_card_block(block, 1)
        assert card.note_type == "DeckOpsQA"
        assert card.card_id is None
        assert card.note_id is None


class TestFormatCard:
    """Test format_card for both note types."""

    @pytest.fixture
    def converter(self):
        return HTMLToMarkdown()

    def test_format_cloze_note(self, converter):
        note = {
            "fields": {
                "Text": {"value": "The {{c1::answer}} is here"},
                "Extra": {"value": "Extra info"},
                "More": {"value": ""},
            }
        }
        result = format_card(789, note, converter, note_type="DeckOpsCloze")
        assert "<!-- note_id: 789 -->" in result
        assert "T: The {{c1::answer}} is here" in result
        assert "E: Extra info" in result
        assert "M:" not in result  # empty optional field omitted

    def test_format_qa_card(self, converter):
        note = {
            "fields": {
                "Question": {"value": "What?"},
                "Answer": {"value": "This"},
                "Extra": {"value": ""},
                "More": {"value": ""},
            }
        }
        result = format_card(123, note, converter, note_type="DeckOpsQA")
        assert "<!-- card_id: 123 -->" in result
        assert "Q: What?" in result
        assert "A: This" in result


class TestExtractCardBlocks:
    """Test extract_card_blocks with mixed content."""

    def test_mixed_qa_and_cloze(self):
        content = (
            "<!-- deck_id: 1 -->\n"
            "<!-- card_id: 10 -->\n"
            "Q: Question\n"
            "A: Answer\n"
            f"{CARD_SEPARATOR}"
            "<!-- note_id: 20 -->\n"
            "T: {{c1::Cloze}}"
        )
        blocks = extract_card_blocks(content)
        assert "card_id: 10" in blocks
        assert "note_id: 20" in blocks
        assert len(blocks) == 2

    def test_only_cloze_blocks(self):
        content = (
            "<!-- deck_id: 1 -->\n"
            "<!-- note_id: 100 -->\n"
            "T: {{c1::First}}\n"
            f"{CARD_SEPARATOR}"
            "<!-- note_id: 200 -->\n"
            "T: {{c1::Second}}"
        )
        blocks = extract_card_blocks(content)
        assert "note_id: 100" in blocks
        assert "note_id: 200" in blocks


class TestValidateCard:
    """Test validate_card for mandatory fields and unknown prefixes."""

    def _mandatory_fields(self, note_type: str) -> list[tuple[str, str]]:
        """Return (field_name, prefix) pairs for mandatory fields of a note type."""
        return [
            (name, prefix)
            for name, prefix, mandatory in NOTE_TYPES[note_type]["field_mappings"]
            if mandatory
        ]

    def test_valid_qa_card(self):
        block = "<!-- card_id: 1 -->\nQ: Question\nA: Answer"
        card = parse_card_block(block, 1)
        assert validate_card(card) == []

    def test_valid_cloze_card(self):
        block = "<!-- note_id: 1 -->\nT: {{c1::text}}"
        card = parse_card_block(block, 1)
        assert validate_card(card) == []

    def test_missing_mandatory_qa_fields(self):
        block = "<!-- card_id: 1 -->\nE: Only extra"
        card = parse_card_block(block, 1)
        errors = validate_card(card)
        for field_name, prefix in self._mandatory_fields("DeckOpsQA"):
            assert any(field_name in e and prefix in e for e in errors)

    def test_missing_mandatory_cloze_field(self):
        block = "<!-- note_id: 1 -->\nE: Only extra"
        card = parse_card_block(block, 1)
        errors = validate_card(card)
        for field_name, prefix in self._mandatory_fields("DeckOpsCloze"):
            assert any(field_name in e and prefix in e for e in errors)

    def test_continuation_lines_not_flagged(self):
        block = "<!-- card_id: 1 -->\nQ: Question\nA: Answer starts\nmore answer text"
        card = parse_card_block(block, 1)
        assert validate_card(card) == []


class TestClozeRoundTrip:
    """Test that cloze syntax passes through HTML↔Markdown converters unchanged."""

    @pytest.fixture
    def md_to_html(self):
        return MarkdownToHTML()

    @pytest.fixture
    def html_to_md(self):
        return HTMLToMarkdown()

    def test_cloze_syntax_through_markdown_to_html(self, md_to_html):
        md = "The capital of {{c1::France}} is {{c2::Paris}}"
        html = md_to_html.convert(md)
        assert "{{c1::France}}" in html
        assert "{{c2::Paris}}" in html

    def test_cloze_syntax_through_html_to_markdown(self, html_to_md):
        html = "The capital of {{c1::France}} is {{c2::Paris}}"
        md = html_to_md.convert(html)
        assert "{{c1::France}}" in md
        assert "{{c2::Paris}}" in md

    def test_cloze_with_hint_roundtrip(self, md_to_html, html_to_md):
        original = "The {{c1::mitochondria::organelle}} is the powerhouse"
        html = md_to_html.convert(original)
        md = html_to_md.convert(html)
        assert "{{c1::mitochondria::organelle}}" in md

    def test_cloze_with_formatting(self, md_to_html):
        md = "**Bold** text with {{c1::cloze}} and *italic*"
        html = md_to_html.convert(md)
        assert "{{c1::cloze}}" in html
        assert "<strong>Bold</strong>" in html
        assert "<em>italic</em>" in html

    def test_multiple_clozes_same_number(self, md_to_html):
        md = "{{c1::First}} and {{c1::second}} are both c1"
        html = md_to_html.convert(md)
        assert "{{c1::First}}" in html
        assert "{{c1::second}}" in html

    def test_multiple_clozes_different_numbers(self, md_to_html):
        md = "{{c1::One}}, {{c2::Two}}, {{c3::Three}}, {{c4::Four}}, {{c5::Five}}"
        html = md_to_html.convert(md)
        assert "{{c1::One}}" in html
        assert "{{c2::Two}}" in html
        assert "{{c3::Three}}" in html
        assert "{{c4::Four}}" in html
        assert "{{c5::Five}}" in html
