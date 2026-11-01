// 練習卷互動程式：作答 → 交卷計分 → 錯題旁直接顯示正確答案與解析
(function () {
  const NUM = ['①', '②', '③', '④', '⑤', '⑥'];
  const data = window.QUIZ;
  const root = document.getElementById('quiz');
  const state = []; // per item: { sec, item, el, picked }

  function choiceSet(sec, item) {
    switch (sec.type) {
      case 'tf': return [{ v: '○', t: '○' }, { v: '✕', t: '✕' }];
      case 'check': return [{ v: '✓', t: '✓' }, { v: '✕', t: '✕' }];
      case 'match': return sec.labels.map(l => ({ v: l, t: l }));
      case 'mc':
      case 'multi': return item.opts.map((o, i) => ({ v: i + 1, t: NUM[i] + ' ' + o }));
    }
  }
  function answerText(sec, item) {
    if (sec.type === 'mc') return NUM[item.a - 1] + ' ' + item.opts[item.a - 1];
    if (sec.type === 'multi') return item.a.map(n => NUM[n - 1]).join('');
    return item.a;
  }
  function el(tag, cls, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  let qNo = 0;
  data.sections.forEach((sec, si) => {
    const h = el('h2', null, sec.title);
    root.appendChild(h);
    if (sec.note) root.appendChild(el('p', 'section-note', sec.note));
    if (sec.shared) root.appendChild(el('div', 'shared-opts', sec.shared));
    sec.items.forEach((item, ii) => {
      if (item.scene) root.appendChild(el('p', 'section-note', '<b>' + item.scene + '</b>'));
      const box = el('div', 'q');
      const stem = el('div', 'stem');
      stem.appendChild(el('span', 'no', (ii + 1) + '.'));
      stem.appendChild(el('span', null, item.q));
      box.appendChild(stem);
      const cs = el('div', 'choices');
      const rec = { sec, item, el: box, picked: sec.type === 'multi' ? new Set() : null, btns: [] };
      choiceSet(sec, item).forEach(c => {
        const b = el('button', 'choice' + (['tf', 'check', 'match'].includes(sec.type) ? ' big' : ''), c.t);
        b.type = 'button';
        b.addEventListener('click', () => {
          if (root.classList.contains('done')) return;
          if (sec.type === 'multi') {
            rec.picked.has(c.v) ? rec.picked.delete(c.v) : rec.picked.add(c.v);
            b.classList.toggle('sel');
          } else {
            rec.picked = c.v;
            rec.btns.forEach(x => x.classList.remove('sel'));
            b.classList.add('sel');
          }
        });
        b.dataset.v = c.v;
        rec.btns.push(b);
        cs.appendChild(b);
      });
      box.appendChild(cs);
      const fb = el('div', 'feedback',
        '<span class="ans"></span> ' + (item.exp || '') +
        (item.page ? ' <span class="page">（課本 ' + item.page + '）</span>' : ''));
      box.appendChild(fb);
      rec.fb = fb;
      root.appendChild(box);
      state.push(rec);
      qNo++;
    });
  });

  const total = data.sections.reduce((s, sec) =>
    s + sec.items.reduce((t, it) => t + (sec.type === 'multi' ? sec.points * it.opts.length : sec.points), 0), 0);
  const scoreEl = document.getElementById('score');
  scoreEl.textContent = '滿分 ' + total + ' 分';

  function grade() {
    let got = 0, wrong = 0;
    state.forEach(r => {
      const { sec, item } = r;
      let pts = 0, ok;
      if (sec.type === 'multi') {
        item.opts.forEach((_, i) => {
          const should = item.a.includes(i + 1);
          if (should === r.picked.has(i + 1)) pts += sec.points;
        });
        if (r.picked.size === 0) pts = 0; // 沒作答不給分
        ok = pts === sec.points * item.opts.length;
      } else {
        ok = String(r.picked) === String(item.a);
        if (ok) pts = sec.points;
      }
      got += pts;
      if (!ok) wrong++;
      r.el.classList.remove('ok', 'bad');
      r.el.classList.add(ok ? 'ok' : 'bad');
      r.btns.forEach(b => {
        const v = sec.type === 'mc' || sec.type === 'multi' ? Number(b.dataset.v) : b.dataset.v;
        const isAns = sec.type === 'multi' ? item.a.includes(v) : String(v) === String(item.a);
        b.classList.toggle('correct', isAns);
      });
      const unanswered = sec.type === 'multi' ? r.picked.size === 0 : r.picked == null;
      r.fb.querySelector('.ans').textContent =
        (ok ? '✔ 答對！' : (unanswered ? '✘ 沒有作答。' : '✘ 答錯了。') + '正確答案：' + answerText(sec, item) + '。') +
        (sec.type === 'multi' && !ok ? '（得 ' + pts + ' 分）' : '');
    });
    root.classList.add('done');
    scoreEl.textContent = '得分 ' + got + ' / ' + total + '　錯 ' + wrong + ' 題';
    const firstBad = root.querySelector('.q.bad');
    if (firstBad) firstBad.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function reset() {
    state.forEach(r => {
      r.picked = r.sec.type === 'multi' ? new Set() : null;
      r.btns.forEach(b => b.classList.remove('sel', 'correct'));
      r.el.classList.remove('ok', 'bad');
    });
    root.classList.remove('done');
    scoreEl.textContent = '滿分 ' + total + ' 分';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  function showAnswers() {
    state.forEach(r => {
      r.fb.querySelector('.ans').textContent = '答案：' + answerText(r.sec, r.item) + '。';
      r.el.classList.remove('ok', 'bad');
      r.btns.forEach(b => {
        const v = r.sec.type === 'mc' || r.sec.type === 'multi' ? Number(b.dataset.v) : b.dataset.v;
        b.classList.toggle('correct', r.sec.type === 'multi' ? r.item.a.includes(v) : String(v) === String(r.item.a));
      });
    });
    root.classList.add('done');
  }
  document.getElementById('submit').addEventListener('click', grade);
  document.getElementById('reset').addEventListener('click', reset);
  document.getElementById('answers').addEventListener('click', showAnswers);
})();
