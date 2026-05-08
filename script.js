document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const expertBtns = document.querySelectorAll('.expert-btn');
    const runBtn = document.getElementById('runBtn');
    const userInput = document.getElementById('userInput');
    const contextInput = document.getElementById('contextInput');
    const statusMsg = document.getElementById('statusMsg');
    
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    const imageContainer = document.getElementById('imageContainer');
    const imageList = document.getElementById('imageList');

    const emptyState = document.getElementById('emptyState');
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
    let selectedImagesData = []; // Array for multiple images

    // Expert Selection Logic
    expertBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            expertBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedSkill = btn.dataset.skill;
            
            if (analysisHistory[selectedSkill]) {
                const skillName = {
                    'copy': 'Skill 1', 'structure': 'Skill 2', 'aesthetic': 'Skill 3', 'recap': 'Skill 4'
                }[selectedSkill];
                
                analysisResult.innerHTML = formatAnalysis(analysisHistory[selectedSkill]);
                resultSkillBadge.innerText = skillName;
                
                const scoreMatch = analysisHistory[selectedSkill].match(/(?:Score|Punteggio):\s*\*?\*?(\d+)/i);
                if (scoreMatch) {
                    resultScoreBadge.innerText = `Overall Score ${scoreMatch[1]}/100`;
                } else {
                    resultScoreBadge.innerText = `Overall Score __`;
                }

                emptyState.classList.add('hidden');
                progressCard.classList.add('hidden');
                resultCard.classList.remove('hidden');
                statusMsg.innerText = "Loaded from history";
            } else {
                const displayName = btn.innerText.includes(': ') ? btn.innerText.split(': ')[1] : btn.innerText;
                statusMsg.innerText = `${displayName.toUpperCase()} selected`;
                emptyState.classList.remove('hidden');
                progressCard.classList.add('hidden');
                resultCard.classList.add('hidden');
            }
        });
    });

    // Image Upload Handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        Array.from(e.dataTransfer.files).forEach(file => {
            if (file && file.type.startsWith('image/')) {
                handleImageFile(file);
            }
        });
    });

    userInput.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const file = items[i].getAsFile();
                handleImageFile(file);
            }
        }
    });

    function handleImageFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            selectedImagesData.push(e.target.result);
            renderThumbnails();
        };
        reader.readAsDataURL(file);
    }

    function renderThumbnails() {
        imageList.innerHTML = '';
        if (selectedImagesData.length > 0) {
            imageContainer.classList.remove('hidden');
            selectedImagesData.forEach((data, index) => {
                const item = document.createElement('div');
                item.className = 'image-item';
                item.innerHTML = `
                    <img src="${data}" alt="Thumbnail">
                    <div class="remove-img-btn" data-index="${index}">×</div>
                `;
                imageList.appendChild(item);
            });

            // Re-attach removal listeners
            document.querySelectorAll('.remove-img-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const idx = parseInt(e.target.dataset.index);
                    selectedImagesData.splice(idx, 1);
                    renderThumbnails();
                });
            });
        } else {
            imageContainer.classList.add('hidden');
        }
    }

    // Progress Bar Animation
    function animateProgress(duration) {
        let start = 0;
        const interval = 50;
        const step = (interval / duration) * 100;
        
        emptyState.classList.add('hidden');
        progressCard.classList.remove('hidden');
        resultCard.classList.add('hidden');
        
        const timer = setInterval(() => {
            start += step;
            if (start >= 98) {
                clearInterval(timer);
                start = 98;
            }
            progressBarFill.style.width = `${start}%`;
            percentText.innerText = `loading ${Math.floor(start).toString().padStart(2, '0')}%`;
        }, interval);

        return timer;
    }

    runBtn.addEventListener('click', async () => {
        const input = userInput.value.trim();
        const context = contextInput.value.trim();

        if (!input && selectedImagesData.length === 0) {
            statusMsg.innerText = "Error: Input required";
            return;
        }

        const skillName = {
            'copy': 'Skill 1',
            'structure': 'Skill 2',
            'aesthetic': 'Skill 3',
            'recap': 'Skill 4'
        }[selectedSkill];

        statusMsg.innerText = `${skillName} is now running`;
        currentSkillBadge.innerText = skillName;
        
        const progressTimer = animateProgress(selectedImagesData.length > 1 ? 8000 : 5000);
        
        progressCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

        try {
            let finalInput = input;
            if (selectedSkill === 'recap') {
                const historyText = Object.entries(analysisHistory)
                    .map(([skill, result]) => `--- ANALYSIS ${skill.toUpperCase()} ---\n${result.substring(0, 2500)}`)
                    .join('\n\n');
                finalInput = `HISTORY OF PREVIOUS ANALYSES:\n${historyText}\n\nURL/SITE: ${input}`;
            }

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    input: finalInput, 
                    skill_type: selectedSkill,
                    context: context,
                    images: selectedImagesData // Send array of images
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
                    resultSkillBadge.innerText = skillName;
                    
                    const scoreMatch = data.analysis.match(/(?:Score|Punteggio|Rating|Valutazione).*?(\d+)\s*\/\s*100/i) || 
                                     data.analysis.match(/(?:Score|Punteggio|Rating|Valutazione):\s*\*?\*?(\d+)/i);
                                     
                    if (scoreMatch) {
                        resultScoreBadge.innerText = `Overall Score ${scoreMatch[1]}/100`;
                    } else {
                        resultScoreBadge.innerText = `Overall Score __`;
                    }

                    analysisResult.innerHTML = formatAnalysis(data.analysis);
                    analysisHistory[selectedSkill] = data.analysis;
                    statusMsg.innerText = "Done";
                }, 500);

            } else {
                statusMsg.innerText = "Error: " + data.message;
                progressCard.classList.add('hidden');
                emptyState.classList.remove('hidden');
            }
        } catch (error) {
            clearInterval(progressTimer);
            statusMsg.innerText = "Connection failed";
            progressCard.classList.add('hidden');
            emptyState.classList.remove('hidden');
            console.error(error);
        }
    });

    function formatAnalysis(text) {
        if (!text) return "";
        let cleanText = text.trim().replace(/\r\n/g, '\n');
        const parts = cleanText.split(/^(?=#+ )/gm);
        
        return parts.map(part => {
            if (!part.trim()) return "";
            let headerMatch = part.match(/^(#+ .*)\n([\s\S]*)/);
            let headerHtml = "";
            let content = part;
            if (headerMatch) {
                const headerText = headerMatch[1].replace(/#+\s*/, '');
                headerHtml = `<h3>${headerText}</h3>`;
                content = headerMatch[2];
            }
            let formattedContent = content.trim() ? marked.parse(content.trim()) : "";
            if (!formattedContent && !headerHtml) return "";
            const contentHtml = formattedContent ? `<div class="result-box markdown-body">${formattedContent}</div>` : "";
            return `<div class="analysis-section">${headerHtml}${contentHtml}</div>`;
        }).join('\n');
    }
});
