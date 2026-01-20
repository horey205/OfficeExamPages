let allQuestions = [];
let currentQuiz = [];
let currentIndex = 0;
let score = 0;
let timer = null;
let timeLeft = 60;
let currentMode = 'study'; // 'study' or 'exam'
let selectedSource = '기출'; // '기출' or 'all'

// Initialize questions from loaded script
if (typeof questionData !== 'undefined') {
    allQuestions = questionData;
    document.getElementById('total-q-count').innerText = allQuestions.length + "+";
} else {
    console.error("questions.js failed to load.");
}

function showLanding() {
    document.getElementById('quiz').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('landing').classList.remove('hidden');
}

function setSource(src) {
    selectedSource = src;
    document.getElementById('src-official').classList.toggle('active', src === '기출');
    document.getElementById('src-all').classList.toggle('active', src === 'all');
}

function startQuiz(subject, mode) {
    currentMode = mode;

    // Filter questions by subject AND source
    let filtered = allQuestions.filter(q => q.subject.includes(subject));

    if (selectedSource === '기출') {
        filtered = filtered.filter(q => q.source === '기출' || !q.source);
    }

    if (filtered.length === 0) {
        alert("해당 과목의 문항이 없습니다.");
        return;
    }

    if (mode === 'exam') {
        // --- Mock Exam: Pick 20 questions (4 High, 12 Medium, 4 Low) ---
        const hardQ = filtered.filter(q => q.difficulty === '상').sort(() => 0.5 - Math.random());
        const midQ = filtered.filter(q => (q.difficulty === '중' || !q.difficulty)).sort(() => 0.5 - Math.random());
        const easyQ = filtered.filter(q => q.difficulty === '하').sort(() => 0.5 - Math.random());

        currentQuiz = [
            ...hardQ.slice(0, 4),
            ...midQ.slice(0, 12),
            ...easyQ.slice(0, 4)
        ];

        if (currentQuiz.length < 20) {
            const extra = filtered.filter(q => !currentQuiz.includes(q)).sort(() => 0.5 - Math.random());
            currentQuiz = [...currentQuiz, ...extra.slice(0, 20 - currentQuiz.length)];
        }
        currentQuiz = currentQuiz.sort(() => 0.5 - Math.random());
    } else {
        // --- Study Mode: Load all questions in order or shuffled ---
        currentQuiz = [...filtered].sort(() => 0.5 - Math.random());
    }

    currentIndex = 0;
    score = 0;

    document.getElementById('landing').classList.add('hidden');
    document.getElementById('quiz').classList.remove('hidden');

    showQuestion();
}

function showQuestion() {
    if (currentIndex >= currentQuiz.length) {
        showResult();
        return;
    }

    const q = currentQuiz[currentIndex];

    // Header Info
    document.getElementById('curr-subject').innerText = q.subject;
    document.getElementById('curr-num').innerText = q.num;
    document.getElementById('q-text').innerText = q.text;

    // Progress
    const progress = (currentIndex / currentQuiz.length) * 100;
    document.getElementById('progress-fill').style.width = `${progress}%`;
    document.getElementById('q-counter').innerText = `${currentIndex + 1} / ${currentQuiz.length}`;

    // Image
    const imgContainer = document.getElementById('q-image');
    if (q.image) {
        imgContainer.innerHTML = `<img src="${q.image}" alt="Question Image" onerror="this.style.display='none'">`;
        imgContainer.classList.remove('hidden');
    } else {
        imgContainer.classList.add('hidden');
    }

    // Options
    const optionsContainer = document.getElementById('options');
    optionsContainer.innerHTML = '';
    q.options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn glass';
        btn.innerHTML = `<span class="opt-num">${idx + 1}</span> ${opt}`;
        btn.onclick = () => checkAnswer(idx + 1);
        optionsContainer.appendChild(btn);
    });

    // Reset UI
    document.getElementById('explanation').classList.add('hidden');
    document.getElementById('next-btn').classList.add('hidden');

    // Timer (Only in Exam Mode)
    clearInterval(timer);
    if (currentMode === 'exam') {
        document.getElementById('timer').classList.remove('hidden');
        startQuestionTimer();
    } else {
        document.getElementById('timer').classList.add('hidden');
    }
}

function startQuestionTimer() {
    timeLeft = 60;
    updateTimerDisplay();
    timer = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        if (timeLeft <= 0) {
            clearInterval(timer);
            handleTimeout();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const min = Math.floor(timeLeft / 60);
    const sec = timeLeft % 60;
    const timerElem = document.getElementById('timer');
    timerElem.innerText = `${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;

    if (timeLeft < 10) {
        timerElem.style.color = '#ef4444';
    } else {
        timerElem.style.color = 'var(--admin-primary)';
    }
}

function handleTimeout() {
    alert("시간이 초과되었습니다!");
    checkAnswer(-1, true);
}

function checkAnswer(selectedIdx, isTimeout = false) {
    if (timer) clearInterval(timer);

    const q = currentQuiz[currentIndex];
    const isCorrect = selectedIdx === q.answer;

    const options = document.querySelectorAll('.option-btn');
    options.forEach((btn, idx) => {
        btn.disabled = true;
        if (idx + 1 === q.answer) {
            btn.classList.add('correct');
        } else if (idx + 1 === selectedIdx) {
            btn.classList.add('wrong');
        }
    });

    if (isCorrect) score++;

    // Show Explanation
    const expDiv = document.getElementById('explanation');
    expDiv.querySelector('#exp-text').innerText = q.explanation || "해설이 없습니다.";
    expDiv.classList.remove('hidden');

    // Show Next Button
    const nextBtn = document.getElementById('next-btn');
    nextBtn.classList.remove('hidden');

    // Auto-scroll to show explanation and button
    setTimeout(() => {
        nextBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);

    // In Exam mode, still show feedback but keep moving
    if (currentMode === 'exam' && isTimeout) {
        setTimeout(nextQuestion, 2000); // 2 seconds delay on timeout
    }
}

function nextQuestion() {
    currentIndex++;
    showQuestion();
}

function showResult() {
    document.getElementById('quiz').classList.add('hidden');
    document.getElementById('result').classList.remove('hidden');

    const finalScore = Math.round((score / currentQuiz.length) * 100);
    document.getElementById('final-score').innerText = finalScore;
    document.getElementById('correct-count').innerText = score;
    document.getElementById('total-questions').innerText = currentQuiz.length;
}

function restartQuiz() {
    showLanding();
}
