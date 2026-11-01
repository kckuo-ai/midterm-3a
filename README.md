# 三年級上學期 期中考複習（康軒版）

網站：https://kckuo-ai.github.io/midterm-3a/

| 科目 | 範圍 | 重點整理 | 練習卷 |
|---|---|---|---|
| 自然 | 第 1、2 單元（p.12–73），可切換全冊 1–4 單元 | [science/notes.html](science/notes.html) | [science/quiz.html](science/quiz.html) |
| 社會 | 第一、二單元（p.11–55），可切換全冊一到五單元 | [social/notes.html](social/notes.html) | [social/quiz.html](social/quiz.html) |

- 練習卷題目放在各科的 `quiz-data.js`，作答與計分程式在 `assets/quiz.js`。
- 新增題目：在 `quiz-data.js` 對應大題的 `items` 加一筆即可（`tf` 是非、`mc` 選擇、`multi` 活用、`match` 配合、`check` 勾選）。
- 範圍切換：題目加 `later: true` 代表不在期中考範圍，只在「全冊」出現；重點整理頁用 `<div class="later">` 包住期中不考的內容。
