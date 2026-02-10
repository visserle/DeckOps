Q: Welcome to DeckOps!
A: Manage your Anki decks as Markdown files.
E: Edit in your favorite editor, sync to Anki, and review anywhere.
M: Pretty neat, huh

---

T: DeckOps supports {{c1::cloze deletions}} and even {{c1::multiple}} {{c2::clozes}} in one card.

---

Q: What Markdown features are supported?
A: **Bold text**, *italic text*, ==highlighted text==, ~~strikethrough~~, and `inline code`

> This is a blockquote
> And another one

**Lists:**

- Unordered item 1
- Unordered item 2
  - Nested item 1 
  - (also available for ordered lists)

**Tables:**

| Header 1 | Header 2 |
| --- | --- |
| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |

**Code blocks** with syntax highlighting:

```python
def hello():
    print("Hello, World!")
    return 42

```

**Math**: Inline \(E = mc^2\) and block formulas

\[\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}\]
E: *Everything renders beautifully on desktop and mobile.*

M: If an image were here, you could resize it and the width would be saved in the Markdown file. 

---

Q: How do I get started?
A: Run `deckops ma` to import Markdown --> Anki

Run `deckops am` to export Anki --> Markdown
E: Check the README for detailed documentation!