# M.Sc. (IT & CA) Semester 3 – Past Papers with Solutions

Question papers from the Semester 3 exams, each with a solved page. Every answer is written in simple words and sized to the marks of the question.

| Subject | Exam | Question paper | Solutions |
|---|---|---|---|
| CS-13 Flutter App Development | Oct–Nov 2024 | [PDF](papers/CS-13_Flutter_Nov-2024.pdf) | [HTML](solutions/CS-13_Flutter_Nov-2024.html) |
| CS-14 Node JS | Oct–Nov 2024 | [PDF](papers/CS-14_NodeJS_Nov-2024.pdf) | [HTML](solutions/CS-14_NodeJS_Nov-2024.html) |
| CS-14 Node JS | Nov 2025 (Regular) | [PDF](papers/CS-14_NodeJS_Nov-2025.pdf) | [HTML](solutions/CS-14_NodeJS_Nov-2025.html) |
| CS-15 Web Development Using Angular Framework | Oct–Nov 2024 | [PDF](papers/CS-15_Angular_Nov-2024.pdf) | [HTML](solutions/CS-15_Angular_Nov-2024.html) |

Download a solutions file and open it in any browser. Fonts and code colours load from the internet; without a connection the page still works with plain fonts.

## How the answers are sized

Each paper has 5 questions of 14 marks (A = 4 × 1, B = 2, C = 3, D = 5).

- **1 mark** – one word or one line (fill in the blank, True/False, a one-line meaning)
- **2 marks** – a definition plus two key points or a tiny example
- **3 marks** – a definition, three or four points, and a small table or code example
- **5 marks** – a full note with a diagram or code, five or six points and a closing line

In sections B, C and D you answer any one of two options. Both options are solved.

## Study features on each page

- Jump to any question (Q1–Q5) from the sticky bar.
- Filter by marks to revise only the 1, 2, 3 or 5 mark questions.
- **Hide answers** turns the page into a self-test; reveal answers one by one.
- Tick questions as revised; ticks are saved in your browser.
- Switch between light and dark mode with the sun/moon button; the page remembers your choice.

## Editing the answers

The pages are generated from plain text files, so answers are easy to fix or extend.

```
source/
├── build.py          builds every page
├── template.html     shared design (CSS + JS)
└── content/<paper>/
    ├── meta.json     title, paper code, colours
    └── q1.md … q5.md one file per question
```

```bash
pip install markdown
python3 source/build.py
```

The format of the question files is described at the top of `source/build.py`.
