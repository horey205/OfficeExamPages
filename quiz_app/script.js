let allQuestions = [];
let currentQuiz = [];
let currentIndex = 0;
let score = 0;
let selectedOption = null;
let timerInterval;
let startTime;

// Load questions on startup
fetch('questions.json')
    .then(res => res.json())
    .then(data => {
        allQuestions = data;
        document.getElementById('total-q-count').innerText = allQuestions.length + "+";
    })
    .catch(err => console.error("Failed to load questions:", err));

function showLanding() {
    document.getElementById('quiz').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('landing').classList.remove('hidden');
    clearInterval(timerInterval);
}

function startQuiz(subject) {
    // Filter questions by subject
    const filtered = allQuestions.filter(q => q.subject.includes(subject));
    if (filtered.length === 0) {
        alert("해당 과목의 문항이 없습니다.");
        return;
    }

    // Shuffle and pick 20
    currentQuiz = filtered.sort(() => 0.5 - Math.random()).slice(0, 20);
    currentIndex = 0;
    score = 0;

    document.getElementById('landing').classList.add('hidden');
    document.getElementById('quiz').classList.remove('hidden');

    startTimer();
    showQuestion();
}

function startTimer() {
    startTime = Date.now();
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const secs = (elapsed % 60).toString().padStart(2, '0');
        document.getElementById('timer').innerText = `${mins}:${secs}`;
    }, 1000);
}

function showQuestion() {
    const q = currentQuiz[currentIndex];
    selectedOption = null;

    // Update Progress
    const progress = ((currentIndex + 1) / currentQuiz.length) * 100;
    document.getElementById('progress-bar').style.setProperty('--progress', `${progress}%`);
    document.getElementById('progress-text').innerText = `${currentIndex + 1} / ${currentQuiz.length}`;

    // Update Meta
    document.getElementById('q-subject').innerText = q.subject;
    document.getElementById('q-num').innerText = q.num.replace(/\n/g, ' ');
    document.getElementById('q-text').innerText = q.text;

    // Image
    const imgContainer = document.getElementById('q-image-container');
    const imgTag = document.getElementById('q-image');
    if (q.image) {
        imgTag.src = q.image;
        imgContainer.classList.remove('hidden');
    } else {
        imgContainer.classList.add('hidden');
    }

    // Options
    const container = document.getElementById('options-container');
    container.innerHTML = '';

    // Prefixes for Korean Multiple Choice
    const prefixes = ['①', '②', '③', '④'];

    q.options.forEach((opt, idx) => {
        const div = document.createElement('div');
        div.className = 'option';
        div.innerHTML = `
            <span class="opt-prefix">${prefixes[idx]}</span>
            <span class="opt-text">${opt}</span>
        `;
        div.onclick = () => selectOption(idx, div);
        container.appendChild(div);
    });

    // Reset Explanation
    document.getElementById('explanation-container').classList.add('hidden');
    document.getElementById('explanation-text').innerText = '';

    // Reset Buttons
    document.getElementById('submit-btn').classList.remove('hidden');
    document.getElementById('next-btn').classList.add('hidden');
}

function selectOption(idx, element) {
    // Unselect others
    const options = document.querySelectorAll('.option');
    options.forEach(opt => opt.classList.remove('selected'));

    element.classList.add('selected');
    selectedOption = idx + 1; // 1-based
}

function checkAnswer() {
    if (selectedOption === null) {
        alert("정답을 선택해주세요.");
        return;
    }

    const q = currentQuiz[currentIndex];
    const options = document.querySelectorAll('.option');

    const isCorrect = selectedOption === q.answer; // Using the placeholder/extracted answer

    if (isCorrect) {
        score++;
        options[selectedOption - 1].classList.add('correct');
    } else {
        options[selectedOption - 1].classList.add('incorrect');
        options[q.answer - 1].classList.add('correct');
    }

    // Show Explanation
    if (q.explanation) {
        document.getElementById('explanation-text').innerText = q.explanation;
        document.getElementById('explanation-container').classList.remove('hidden');
    }

    document.getElementById('submit-btn').classList.add('hidden');
    document.getElementById('next-btn').classList.remove('hidden');
}

function nextQuestion() {
    currentIndex++;
    if (currentIndex < currentQuiz.length) {
        showQuestion();
    } else {
        showResult();
    }
}

function showResult() {
    clearInterval(timerInterval);
    document.getElementById('quiz').classList.add('hidden');
    document.getElementById('result').classList.remove('hidden');

    const total = currentQuiz.length;
    const percentage = Math.round((score / total) * 100);

    document.getElementById('final-score').innerText = percentage;
    document.getElementById('correct-count').innerText = score;
    document.getElementById('total-count').innerText = total;

    if (percentage >= 80) {
        document.getElementById('result-title').innerText = "훌륭합니다!";
    } else if (percentage >= 60) {
        document.getElementById('result-title').innerText = "합격권입니다!";
    } else {
        document.getElementById('result-title').innerText = "조금 더 노력해볼까요?";
    }
}

function restartQuiz() {
    currentIndex = 0;
    score = 0;
    document.getElementById('result').classList.add('hidden');
    document.getElementById('quiz').classList.remove('hidden');
    startTimer();
    showQuestion();
}
