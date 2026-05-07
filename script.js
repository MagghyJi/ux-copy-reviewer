document.addEventListener('DOMContentLoaded', () => {
    const skillButtons = document.querySelectorAll('.skill-btn');
    const runBtn = document.getElementById('runBtn');
    const userInput = document.getElementById('userInput');
    const contextInput = document.getElementById('contextInput');
    const statusMsg = document.getElementById('statusMsg');
    const progressCard = document.getElementById('progressCard');
    const resultCard = document.getElementById('resultCard');
    const progressBarFill = document.getElementById('progressBarFill');
    const percentText = document.getElementById('percentText');
    const analysisResult = document.getElementById('analysisResult');
    const currentSkillBadge = document.getElementById('currentSkillBadge');
    const resultSkillBadge = document.getElementById('resultSkillBadge');
    const resultScoreBadge = document.getElementById('resultScoreBadge');

    let selectedSkill = 'copy';
    let analysisHistory = {};

    // Skill Selection Logic
    skillButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            skillButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedSkill = btn.dataset.skill;
            statusMsg.innerText = `Expert ${selectedSkill.toUpperCase()} selected`;
        });
    });

    // Progress Bar Animation
    function animateProgress(duration) {
        let start = 0;
        const interval = 50;
        const step = (interval / duration) * 100;
        
        progressCard.classList.remove('hidden');
        resultCard.classList.add('hidden');
        
        const timer = setInterval(() => {
            start += step;
            if (start >= 95) {
                clearInterval(timer);
                start = 95;
            }
            progressBarFill.style.width = `${start}%`;
            percentText.innerText = `loading ${Math.floor(start).toString().padStart(2, '0')}%`;
        }, interval);

        return timer;
    }

    runBtn.addEventListener('click', async () => {
        const input = userInput.value.trim();
        const context = contextInput.value.trim();

        if (!input) {
            statusMsg.innerText = "Error: Please insert a URL or text.";
            return;
        }

        statusMsg.innerText = `Skill ${selectedSkill} is now running...`;
        currentSkillBadge.innerText = `Skill: ${selectedSkill.toUpperCase()}`;
        
        const progressTimer = animateProgress(3000);

        try {
            let finalInput = input;
            if (selectedSkill === 'recap') {
                const historyText = Object.entries(analysisHistory)
                    .map(([skill, result]) => `--- ANALYSIS ${skill.toUpperCase()} ---\n${result}`)
                    .join('\n\n');
                finalInput = `HISTORY OF PREVIOUS ANALYSES:\n${historyText}\n\nURL/SITE: ${input}`;
            }

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    input: finalInput, 
                    skill_type: selectedSkill,
                    context: context 
                })
            });

            const data = await response.json();
            clearInterval(progressTimer);

            if (data.status === 'success') {
                progressBarFill.style.width = '100%';
                percentText.innerText = 'loading 100%';

                setTimeout(() => {
                    progressCard.classList.add('hidden');
                    resultCard.classList.remove('hidden');
                    
                    resultSkillBadge.innerText = `Skill: ${selectedSkill.toUpperCase()}`;
                    
                    const scoreMatch = data.analysis.match(/Score:\s*(\d+)\/100/i);
                    if (scoreMatch) {
                        resultScoreBadge.innerText = `OVERALL SCORE ${scoreMatch[1]}/100`;
                    } else {
                        resultScoreBadge.innerText = `OVERALL SCORE __`;
                    }

                    analysisResult.innerHTML = formatAnalysis(data.analysis);
                    analysisHistory[selectedSkill] = data.analysis;
                    statusMsg.innerText = "Analysis complete.";
                }, 500);

            } else {
                statusMsg.innerText = "Error: " + data.message;
                progressCard.classList.add('hidden');
            }
        } catch (error) {
            clearInterval(progressTimer);
            statusMsg.innerText = "System Error: Unable to connect to backend.";
            progressCard.classList.add('hidden');
            console.error(error);
        }
    });

    function formatAnalysis(text) {
        // Advanced Formatter
        return text
            .replace(/^# (.*$)/gim, '<h2>$1</h2>')
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            .replace(/^### (.*$)/gim, '<h4>$1</h4>')
            .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/^\- (.*$)/gim, '<li>$1</li>')
            .replace(/^\d\. (.*$)/gim, '<li>$1</li>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>')
            .replace(/---/g, '<hr style="border: 0; border-top: 1px solid rgba(135, 243, 46, 0.2); margin: 20px 0;">');
    }
});
