// CrewAI 9-Agent Master Studio - Interactive Frontend Engine
document.addEventListener("DOMContentLoaded", () => {
    // Pipeline DOM Nodes
    const nodeInput = document.getElementById("nodeInput");
    const nodeInputTopic = document.getElementById("nodeInputTopic");
    const nodeResearcher = document.getElementById("nodeResearcher");
    const nodeCrossVerifier = document.getElementById("nodeCrossVerifier");
    const nodeWriter = document.getElementById("nodeWriter");
    const nodeDiagrammer = document.getElementById("nodeDiagrammer");
    const nodeCodeQa = document.getElementById("nodeCodeQa");
    const nodeEditor = document.getElementById("nodeEditor");
    const nodeSeo = document.getElementById("nodeSeo");
    const nodePodcast = document.getElementById("nodePodcast");
    const nodeNewsletter = document.getElementById("nodeNewsletter");
    const nodeOutput = document.getElementById("nodeOutput");

    // UI Input Elements
    const generateForm = document.getElementById("generateForm");
    const topicInput = document.getElementById("topicInput");
    const channelInput = document.getElementById("channelInput");
    const startBtn = document.getElementById("startBtn");
    const terminalLogs = document.getElementById("terminalLogs");
    const clearLogsBtn = document.getElementById("clearLogsBtn");
    const topicChips = document.querySelectorAll(".chip");
    const channelChips = document.querySelectorAll(".channel-chip");
    const ytChips = document.querySelectorAll(".yt-chip");
    const quickModelChips = document.querySelectorAll(".quick-model-chip");
    const headerModelText = document.getElementById("headerModelText");
    const sessionTimerText = document.getElementById("sessionTimerText");
    const toastContainer = document.getElementById("toastContainer");

    // YouTube Live Preview Card Elements
    const ytPreviewCard = document.getElementById("ytPreviewCard");
    const ytThumbImg = document.getElementById("ytThumbImg");
    const ytPreviewTitle = document.getElementById("ytPreviewTitle");
    const ytChannelBadge = document.getElementById("ytChannelBadge");
    const ytTranscriptPill = document.getElementById("ytTranscriptPill");
    const ytPreviewClose = document.getElementById("ytPreviewClose");

    // Content Display Panels
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const markdownOutput = document.getElementById("markdownOutput");
    const socialKitContainer = document.getElementById("socialKitContainer");
    const podcastContainer = document.getElementById("podcastContainer");
    const newsletterContainer = document.getElementById("newsletterContainer");
    const articleMetaBar = document.getElementById("articleMetaBar");
    const metaTopic = document.getElementById("metaTopic");
    const metaReadTime = document.getElementById("metaReadTime");
    const metaWordCount = document.getElementById("metaWordCount");
    const narrateArticleBtn = document.getElementById("narrateArticleBtn");

    // Podcast Studio Audio Controls
    const podcastPlayerCard = document.getElementById("podcastPlayerCard");
    const playPodcastAudioBtn = document.getElementById("playPodcastAudioBtn");
    const stopPodcastAudioBtn = document.getElementById("stopPodcastAudioBtn");
    const audioVoiceSelector = document.getElementById("audioVoiceSelector");
    const audioSpeedSelector = document.getElementById("audioSpeedSelector");
    const podcastPlayerTitle = document.getElementById("podcastPlayerTitle");
    const audioWaveform = document.getElementById("audioWaveform");

    // YouTube Knowledge Base Explorer Tab
    const ytExplorerInput = document.getElementById("ytExplorerInput");
    const ytExplorerSearchBtn = document.getElementById("ytExplorerSearchBtn");
    const ytSearchResultsGrid = document.getElementById("ytSearchResultsGrid");

    // Agent Co-Working Dialogue Stream Tab
    const dialogueStream = document.getElementById("dialogueStream");
    const clearDialogueBtn = document.getElementById("clearDialogueBtn");

    // Training Lab Tab
    const trainingForm = document.getElementById("trainingForm");
    const trainIterationsInput = document.getElementById("trainIterationsInput");
    const trainWeightsFilename = document.getElementById("trainWeightsFilename");
    const trainTopicInput = document.getElementById("trainTopicInput");
    const trainChannelInput = document.getElementById("trainChannelInput");
    const startTrainingBtn = document.getElementById("startTrainingBtn");
    const trainingProgressBox = document.getElementById("trainingProgressBox");
    const trainingProgressBar = document.getElementById("trainingProgressBar");
    const trainingProgressLabel = document.getElementById("trainingProgressLabel");
    const trainingFeedbackLog = document.getElementById("trainingFeedbackLog");
    const trainingLabStatusText = document.getElementById("trainingLabStatusText");
    const activeWeightsFile = document.getElementById("activeWeightsFile");

    // Action Buttons
    const copyMarkdownBtn = document.getElementById("copyMarkdownBtn");
    const downloadMdBtn = document.getElementById("downloadMdBtn");
    const downloadHtmlBtn = document.getElementById("downloadHtmlBtn");
    const printPdfBtn = document.getElementById("printPdfBtn");
    const openWebhookBtn = document.getElementById("openWebhookBtn");

    // Cover Studio Elements
    const articleCoverContainer = document.getElementById("articleCoverContainer");
    const articleCoverImg = document.getElementById("articleCoverImg");
    const studioCoverImg = document.getElementById("studioCoverImg");
    const coverTopicLabel = document.getElementById("coverTopicLabel");
    const regenCoverBtn = document.getElementById("regenCoverBtn");
    const downloadCoverBtn = document.getElementById("downloadCoverBtn");
    const copyCoverMdBtn = document.getElementById("copyCoverMdBtn");
    const coverStyleChips = document.querySelectorAll(".style-chip");

    // Settings & Webhook Modals
    const openSettingsBtn = document.getElementById("openSettingsBtn");
    const closeSettingsBtn = document.getElementById("closeSettingsBtn");
    const cancelSettingsBtn = document.getElementById("cancelSettingsBtn");
    const saveSettingsBtn = document.getElementById("saveSettingsBtn");
    const settingsModal = document.getElementById("settingsModal");
    const modalApiKey = document.getElementById("modalApiKey");
    const modalModelSelect = document.getElementById("modalModelSelect");
    const modalMemoryToggle = document.getElementById("modalMemoryToggle");
    const modalEmbedderSelect = document.getElementById("modalEmbedderSelect");
    const embedderGroup = document.getElementById("embedderGroup");
    const resetMemoryBtn = document.getElementById("resetMemoryBtn");
    const memoryResetStatus = document.getElementById("memoryResetStatus");
    const memoryStatusBadge = document.getElementById("memoryStatusBadge");
    const memoryStatusText = document.getElementById("memoryStatusText");

    const webhookModal = document.getElementById("webhookModal");
    const closeWebhookBtn = document.getElementById("closeWebhookBtn");
    const cancelWebhookBtn = document.getElementById("cancelWebhookBtn");
    const sendWebhookBtn = document.getElementById("sendWebhookBtn");
    const webhookUrlInput = document.getElementById("webhookUrlInput");
    const webhookStatus = document.getElementById("webhookStatus");

    // State Variables
    let currentMarkdown = "";
    let currentSocialMarkdown = "";
    let currentPodcastMarkdown = "";
    let currentNewsletterMarkdown = "";
    let currentCoverUrl = "";
    let selectedCoverStyle = "3d_tech";
    let isRunning = false;
    let inspectDebounceTimer = null;
    let detectedVideoData = null;
    let currentUtterance = null;
    let availableVoices = [];
    let timerInterval = null;
    let timerSeconds = 0;

    // Toast Notification Utility
    function showToast(message, type = "info") {
        if (!toastContainer) return;
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        const icon = type === "success" ? "✅" : type === "error" ? "❌" : "ℹ️";
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = "fadeOutRight 0.3s forwards";
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }

    // Session Timer Helpers
    function startTimer() {
        clearInterval(timerInterval);
        timerSeconds = 0;
        if (sessionTimerText) sessionTimerText.textContent = "00:00";
        timerInterval = setInterval(() => {
            timerSeconds++;
            const mins = String(Math.floor(timerSeconds / 60)).padStart(2, "0");
            const secs = String(timerSeconds % 60).padStart(2, "0");
            if (sessionTimerText) sessionTimerText.textContent = `${mins}:${secs}`;
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
    }

    // Initialize Mermaid
    if (window.mermaid) {
        mermaid.initialize({
            startOnLoad: false,
            theme: "dark",
            securityLevel: "loose",
            themeVariables: {
                darkMode: true,
                background: "#0d1117",
                primaryColor: "#38bdf8",
                primaryTextColor: "#f1f5f9",
                primaryBorderColor: "#0284c7",
                lineColor: "#60a5fa",
                secondaryColor: "#818cf8",
                tertiaryColor: "#1e293b",
            }
        });
    }

    // Configure Marked options
    if (window.marked) {
        marked.setOptions({
            gfm: true,
            breaks: true,
            headerIds: true,
            mangle: false,
        });
    }

    // Initialize Web Speech Voices
    function populateVoiceList() {
        if (!window.speechSynthesis) return;
        availableVoices = window.speechSynthesis.getVoices();
        if (audioVoiceSelector && availableVoices.length > 0) {
            audioVoiceSelector.innerHTML = "";
            availableVoices.forEach((voice, i) => {
                const opt = document.createElement("option");
                opt.value = i;
                opt.textContent = `${voice.name} (${voice.lang})${voice.default ? ' — Default' : ''}`;
                audioVoiceSelector.appendChild(opt);
            });
        }
    }

    if (window.speechSynthesis) {
        populateVoiceList();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = populateVoiceList;
        }
    }

    // Initialize Application State
    fetchSettings();
    fetchExistingArticle();

    // YouTube URL Detection Helper
    function isYouTubeUrl(str) {
        if (!str) return false;
        const pattern = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|shorts\/|live\/|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/i;
        return pattern.test(str.trim());
    }

    // Live YouTube Inspector
    async function inspectYouTube(urlOrQuery) {
        if (!urlOrQuery || !isYouTubeUrl(urlOrQuery)) {
            if (ytPreviewCard) ytPreviewCard.style.display = "none";
            detectedVideoData = null;
            return;
        }

        if (ytPreviewCard) {
            ytPreviewCard.style.display = "flex";
            ytPreviewTitle.textContent = "Inspecting YouTube Video...";
            ytChannelBadge.textContent = "Connecting to YouTube";
            ytTranscriptPill.className = "yt-transcript-pill inspecting";
            ytTranscriptPill.textContent = "🔍 Checking Subtitles...";
        }

        try {
            const res = await fetch("/api/youtube/inspect", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: urlOrQuery })
            });
            const data = await res.json();
            if (data.valid) {
                detectedVideoData = data;
                if (ytPreviewCard) ytPreviewCard.style.display = "flex";
                if (ytThumbImg) ytThumbImg.src = data.thumbnail_url;
                if (ytPreviewTitle) ytPreviewTitle.textContent = data.title;
                if (ytChannelBadge) ytChannelBadge.textContent = data.author;
                
                if (ytTranscriptPill) {
                    if (data.has_transcript) {
                        ytTranscriptPill.className = "yt-transcript-pill available";
                        ytTranscriptPill.textContent = "🟢 Full Transcript Ready";
                    } else {
                        ytTranscriptPill.className = "yt-transcript-pill unavailable";
                        ytTranscriptPill.textContent = "🟡 Auto Synthesis Mode";
                    }
                }

                if (nodeInputTopic) {
                    nodeInputTopic.textContent = data.title;
                }
                if (channelInput && data.author) {
                    channelInput.value = data.author;
                }
                showToast(`YouTube Video Detected: "${data.title.substring(0, 30)}..."`, "success");
            } else {
                detectedVideoData = null;
                if (ytPreviewCard) ytPreviewCard.style.display = "none";
            }
        } catch (err) {
            console.log("YouTube inspection error:", err);
            detectedVideoData = null;
        }
    }

    // Input listeners with debounce for instant YouTube URL detection
    topicInput.addEventListener("input", () => {
        const val = topicInput.value.trim();
        nodeInputTopic.textContent = val || "Custom Topic";
        
        clearTimeout(inspectDebounceTimer);
        if (isYouTubeUrl(val)) {
            inspectDebounceTimer = setTimeout(() => inspectYouTube(val), 350);
        } else {
            if (ytPreviewCard) ytPreviewCard.style.display = "none";
            detectedVideoData = null;
        }
    });

    if (ytPreviewClose) {
        ytPreviewClose.addEventListener("click", () => {
            ytPreviewCard.style.display = "none";
            detectedVideoData = null;
            topicInput.value = "";
            nodeInputTopic.textContent = "Enter Topic or URL";
        });
    }

    // Quick Model Selector Chips
    quickModelChips.forEach(chip => {
        chip.addEventListener("click", async () => {
            quickModelChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            const chosenModel = chip.getAttribute("data-model");
            
            if (modalModelSelect) modalModelSelect.value = chosenModel;
            if (headerModelText) headerModelText.textContent = chosenModel.split("/").pop().replace(":free", "");

            try {
                await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        api_key: modalApiKey ? modalApiKey.value : "",
                        model_name: chosenModel,
                        memory_enabled: modalMemoryToggle ? modalMemoryToggle.checked : true,
                        embedder_provider: modalEmbedderSelect ? modalEmbedderSelect.value : "onnx"
                    })
                });
                appendLog(`[MODEL] Active LLM switched to: ${chosenModel}`, "log-info");
                showToast(`Model switched to ${chosenModel.split("/").pop()}`, "success");
            } catch (err) {
                console.log("Quick model switch error:", err);
            }
        });
    });

    // YouTube Preset Chips Click Handler
    ytChips.forEach(chip => {
        chip.addEventListener("click", () => {
            channelChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            const url = chip.getAttribute("data-url");
            if (url) {
                topicInput.value = url;
                inspectYouTube(url);
            }
        });
    });

    // Topic Chip Clicks
    topicChips.forEach(chip => {
        chip.addEventListener("click", () => {
            topicInput.value = chip.getAttribute("data-topic");
            nodeInputTopic.textContent = topicInput.value;
            if (ytPreviewCard) ytPreviewCard.style.display = "none";
            detectedVideoData = null;
        });
    });

    // Channel Chip Clicks
    channelChips.forEach(chip => {
        chip.addEventListener("click", () => {
            if (chip.classList.contains("yt-chip")) return;
            channelChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            channelInput.value = chip.getAttribute("data-channel");
        });
    });

    // Tab Switching Logic
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            btn.classList.add("active");
            const targetEl = document.getElementById(targetTab);
            if (targetEl) targetEl.classList.add("active");
        });
    });

    // Terminal Clear Button
    clearLogsBtn.addEventListener("click", () => {
        terminalLogs.innerHTML = `<span class="log-info">[CLEARED] Logs reset at ${new Date().toLocaleTimeString()}</span>\n`;
    });

    // Export Actions Handlers
    copyMarkdownBtn.addEventListener("click", () => {
        if (!currentMarkdown) return;
        navigator.clipboard.writeText(currentMarkdown);
        showToast("Master Article Markdown copied to clipboard!", "success");
        flashButtonText(copyMarkdownBtn, "Copied!");
    });

    downloadMdBtn.addEventListener("click", () => {
        if (!currentMarkdown) return;
        const topicName = (topicInput.value || "article").toLowerCase().replace(/[^a-z0-9]+/g, "-");
        const blob = new Blob([currentMarkdown], { type: "text/markdown;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `blog-${topicName}.md`;
        link.click();
        showToast("Downloaded master markdown file", "success");
    });

    downloadHtmlBtn.addEventListener("click", async () => {
        if (!currentMarkdown) return;
        const renderedHtml = markdownOutput.innerHTML;
        const topicName = topicInput.value || "AI Insights";

        try {
            const res = await fetch("/api/export-html", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: topicName, html_body: renderedHtml })
            });
            const blob = await res.blob();
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `blog-${topicName.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.html`;
            link.click();
            showToast("Downloaded styled standalone HTML document", "success");
        } catch (err) {
            alert("Failed to export HTML: " + err.message);
        }
    });

    printPdfBtn.addEventListener("click", () => {
        if (!currentMarkdown) {
            alert("Please generate or load an article before exporting to PDF.");
            return;
        }
        document.querySelector('[data-tab="articleTab"]').click();
        window.print();
    });

    // Web Speech Narration for Master Article
    if (narrateArticleBtn) {
        narrateArticleBtn.addEventListener("click", () => {
            if (!window.speechSynthesis) {
                alert("Speech Synthesis is not supported in this browser.");
                return;
            }

            if (speechSynthesis.speaking) {
                speechSynthesis.cancel();
                narrateArticleBtn.classList.remove("speaking");
                narrateArticleBtn.querySelector("span").textContent = "🔊 Listen to Article";
                return;
            }

            const cleanText = (currentMarkdown || "").replace(/[#*`_\[\]()>-]/g, " ").trim();
            if (!cleanText) {
                alert("No article loaded to narrate.");
                return;
            }

            const utterance = new SpeechSynthesisUtterance(cleanText.substring(0, 3000));
            utterance.rate = 1.05;
            utterance.pitch = 1.0;

            if (availableVoices.length > 0) {
                const preferred = availableVoices.find(v => v.lang.startsWith("en") && !v.localService) || availableVoices[0];
                if (preferred) utterance.voice = preferred;
            }

            utterance.onend = () => {
                narrateArticleBtn.classList.remove("speaking");
                narrateArticleBtn.querySelector("span").textContent = "🔊 Listen to Article";
            };

            narrateArticleBtn.classList.add("speaking");
            narrateArticleBtn.querySelector("span").textContent = "⏹ Stop Narration";
            speechSynthesis.speak(utterance);
        });
    }

    // Podcast Speech Synthesizer Player Controls
    if (playPodcastAudioBtn && stopPodcastAudioBtn) {
        playPodcastAudioBtn.addEventListener("click", () => {
            if (!window.speechSynthesis) {
                alert("Speech Synthesis is not supported in this browser.");
                return;
            }

            if (speechSynthesis.speaking) {
                speechSynthesis.cancel();
            }

            const textToSpeak = (currentPodcastMarkdown || currentMarkdown || "").replace(/[#*`_\[\]()>-]/g, " ").trim();
            if (!textToSpeak) {
                alert("No podcast script generated yet.");
                return;
            }

            currentUtterance = new SpeechSynthesisUtterance(textToSpeak.substring(0, 4500));
            
            const selectedSpeed = audioSpeedSelector ? parseFloat(audioSpeedSelector.value) : 1.0;
            currentUtterance.rate = selectedSpeed;
            currentUtterance.pitch = 1.02;

            const selectedIdx = audioVoiceSelector ? parseInt(audioVoiceSelector.value, 10) : 0;
            if (availableVoices[selectedIdx]) {
                currentUtterance.voice = availableVoices[selectedIdx];
            }

            currentUtterance.onstart = () => {
                if (audioWaveform) audioWaveform.classList.add("active");
            };

            currentUtterance.onend = () => {
                playPodcastAudioBtn.style.display = "flex";
                stopPodcastAudioBtn.style.display = "none";
                if (audioWaveform) audioWaveform.classList.remove("active");
                document.getElementById("playText").textContent = "Play Voice Audio";
            };

            playPodcastAudioBtn.style.display = "none";
            stopPodcastAudioBtn.style.display = "flex";
            speechSynthesis.speak(currentUtterance);
        });

        stopPodcastAudioBtn.addEventListener("click", () => {
            if (window.speechSynthesis) speechSynthesis.cancel();
            playPodcastAudioBtn.style.display = "flex";
            stopPodcastAudioBtn.style.display = "none";
            if (audioWaveform) audioWaveform.classList.remove("active");
            document.getElementById("playText").textContent = "Play Voice Audio";
        });
    }

    // YouTube Knowledge Base Explorer Search
    if (ytExplorerSearchBtn && ytExplorerInput) {
        ytExplorerSearchBtn.addEventListener("click", async () => {
            const query = ytExplorerInput.value.trim();
            if (!query) return;

            ytExplorerSearchBtn.disabled = true;
            ytExplorerSearchBtn.querySelector("span").textContent = "Searching YouTube...";
            ytSearchResultsGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⏳</div>
                    <h3>Querying Universal YouTube Knowledge Base...</h3>
                    <p>Scraping transcripts and metadata for "${query}" across creators.</p>
                </div>
            `;

            try {
                const res = await fetch("/api/youtube/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query: query, max_videos: 3 })
                });
                const data = await res.json();

                const videoList = data.videos || data.records || [];
                if (videoList && videoList.length > 0) {
                    ytSearchResultsGrid.innerHTML = "";
                    videoList.forEach(rec => {
                        const card = document.createElement("div");
                        card.className = "yt-video-card";
                        const videoUrl = rec.url || rec.video_url || `https://www.youtube.com/watch?v=${rec.video_id}`;
                        const thumbUrl = rec.thumbnail_url || `https://i.ytimg.com/vi/${rec.video_id}/hqdefault.jpg`;
                        const wordCount = rec.transcript ? rec.transcript.split(/\s+/).length : (rec.transcript_chars ? Math.round(rec.transcript_chars / 5) : 0);

                        card.innerHTML = `
                            <div class="yt-video-thumb-container">
                                <img src="${thumbUrl}" alt="Thumbnail">
                                <div class="yt-video-badge-row">
                                    <span class="badge" style="background: rgba(0,0,0,0.75);">${rec.has_transcript || rec.transcript ? '🟢 Transcript Loaded' : '🟡 Video Metadata'}</span>
                                    <span class="badge" style="background: rgba(0,0,0,0.75);">${wordCount} words</span>
                                </div>
                            </div>
                            <div class="yt-video-card-body">
                                <div class="yt-video-card-title">${rec.title}</div>
                                <div class="yt-video-card-author">${rec.author || "Creator"}</div>
                                <div class="yt-video-transcript-box">${(rec.transcript || "No raw subtitle text found. Video metadata indexed for synthesis.").substring(0, 320)}...</div>
                                <div class="yt-video-card-actions">
                                    <button type="button" class="btn btn-primary btn-sm load-to-pipeline-btn" data-url="${videoUrl}" data-title="${rec.title}">
                                        <span>⚡ Load into 9-Agent Pipeline</span>
                                    </button>
                                </div>
                            </div>
                        `;
                        ytSearchResultsGrid.appendChild(card);
                    });

                    // Add listeners for "Load into Pipeline" buttons
                    ytSearchResultsGrid.querySelectorAll(".load-to-pipeline-btn").forEach(btn => {
                        btn.addEventListener("click", () => {
                            const url = btn.getAttribute("data-url");
                            const title = btn.getAttribute("data-title");
                            topicInput.value = url;
                            inspectYouTube(url);
                            showToast(`Loaded "${title.substring(0, 30)}..." into Pipeline Input`, "success");
                            document.querySelector('[data-tab="articleTab"]').click();
                        });
                    });
                } else {
                    ytSearchResultsGrid.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">⚠️</div>
                            <h3>No Video Records Retrieved</h3>
                            <p>Try searching for a different keyword or topic.</p>
                        </div>
                    `;
                }
            } catch (err) {
                ytSearchResultsGrid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <h3>Search Failed</h3>
                        <p>${err.message}</p>
                    </div>
                `;
            } finally {
                ytExplorerSearchBtn.disabled = false;
                ytExplorerSearchBtn.querySelector("span").textContent = "🔍 Search Database";
            }
        });
    }

    // Training & Fine-Tuning Lab Form Handler
    if (trainingForm) {
        trainingForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const iterations = parseInt(trainIterationsInput.value, 10) || 2;
            const filename = trainWeightsFilename.value.trim() || "trained_agents.pkl";
            const topic = trainTopicInput.value.trim() || "AI vs ML vs Data Science";
            const channel = trainChannelInput.value.trim() || "@krishnaik06";

            startTrainingBtn.disabled = true;
            startTrainingBtn.querySelector("span").textContent = `Training ${iterations} Iterations...`;
            trainingProgressBox.style.display = "flex";
            trainingProgressBar.style.width = "30%";
            trainingProgressLabel.textContent = `Calibrating agents (Iteration 1 of ${iterations})...`;
            trainingLabStatusText.textContent = "Training in Progress";

            trainingFeedbackLog.innerHTML = `<span class="log-info">[TRAINING] Starting CrewAI reinforcement training (${iterations} iterations)...</span>\n`;

            try {
                const res = await fetch("/api/train", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ iterations, filename, topic, channel })
                });

                const data = await res.json();
                trainingProgressBar.style.width = "100%";
                trainingProgressLabel.textContent = "Training Complete (100%)";

                if (res.ok) {
                    trainingFeedbackLog.innerHTML += `\n<span class="log-success">✅ ${data.message}</span>\n<span class="log-info">[SAVED] Prompt calibrator serialized to: ${filename}</span>\n`;
                    activeWeightsFile.textContent = filename;
                    trainingLabStatusText.textContent = "Trained & Calibrated";
                    showToast(`Training complete! Saved weights to ${filename}`, "success");
                } else {
                    trainingFeedbackLog.innerHTML += `\n<span class="log-err">❌ Training failed: ${data.detail || "Error"}</span>\n`;
                    trainingLabStatusText.textContent = "Training Failed";
                }
            } catch (err) {
                trainingFeedbackLog.innerHTML += `\n<span class="log-err">❌ Network error: ${err.message}</span>\n`;
                trainingLabStatusText.textContent = "Error";
            } finally {
                startTrainingBtn.disabled = false;
                startTrainingBtn.querySelector("span").textContent = "⚡ Start Crew Training Run";
            }
        });
    }

    // Agent Dialogue Stream Clear
    if (clearDialogueBtn) {
        clearDialogueBtn.addEventListener("click", () => {
            dialogueStream.innerHTML = `
                <div class="dialogue-msg system">
                    <div class="dialogue-avatar">⚡</div>
                    <div class="dialogue-bubble">
                        <div class="dialogue-meta">
                            <span class="dialogue-agent">Master Coordinator</span>
                            <span class="dialogue-time">${new Date().toLocaleTimeString()}</span>
                        </div>
                        <div class="dialogue-text">Dialogue stream cleared. Ready for next collaborative run.</div>
                    </div>
                </div>
            `;
        });
    }

    // Helper to append dialogue message
    function appendDialogueMsg(agentName, text, avatar = "🤖", isSystem = false) {
        if (!dialogueStream) return;
        const msg = document.createElement("div");
        msg.className = isSystem ? "dialogue-msg system" : "dialogue-msg";
        msg.innerHTML = `
            <div class="dialogue-avatar">${avatar}</div>
            <div class="dialogue-bubble">
                <div class="dialogue-meta">
                    <span class="dialogue-agent">${agentName}</span>
                    <span class="dialogue-time">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="dialogue-text">${text}</div>
            </div>
        `;
        dialogueStream.appendChild(msg);
        dialogueStream.scrollTop = dialogueStream.scrollHeight;
    }

    // Webhook Publish Modal
    openWebhookBtn.addEventListener("click", () => {
        webhookStatus.className = "webhook-status";
        webhookStatus.textContent = "";
        webhookModal.classList.add("active");
    });

    closeWebhookBtn.addEventListener("click", () => webhookModal.classList.remove("active"));
    cancelWebhookBtn.addEventListener("click", () => webhookModal.classList.remove("active"));

    sendWebhookBtn.addEventListener("click", async () => {
        const url = webhookUrlInput.value.trim();
        if (!url) {
            alert("Please enter a valid webhook URL.");
            return;
        }

        sendWebhookBtn.disabled = true;
        sendWebhookBtn.textContent = "Dispatching...";
        webhookStatus.className = "webhook-status";
        webhookStatus.textContent = "Sending 9-agent master payload to webhook...";

        try {
            const res = await fetch("/api/publish-webhook", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    webhook_url: url,
                    topic: topicInput.value,
                    channel: channelInput.value,
                    markdown_content: currentMarkdown,
                    social_content: currentSocialMarkdown,
                    podcast_content: currentPodcastMarkdown,
                    newsletter_content: currentNewsletterMarkdown
                })
            });

            const data = await res.json();
            if (res.ok && data.status === "ok") {
                webhookStatus.className = "webhook-status success";
                webhookStatus.textContent = `✅ Successfully published! HTTP ${data.http_status} Response: ${data.response || "OK"}`;
                appendLog(`[SUCCESS] Master kit webhook dispatched to ${url}`, "log-success");
                showToast("Payload published to Webhook successfully!", "success");
            } else {
                webhookStatus.className = "webhook-status error";
                webhookStatus.textContent = `❌ Failed: ${data.detail || "Unknown error"}`;
            }
        } catch (err) {
            webhookStatus.className = "webhook-status error";
            webhookStatus.textContent = `❌ Network Error: ${err.message}`;
        } finally {
            sendWebhookBtn.disabled = false;
            sendWebhookBtn.textContent = "Dispatch Webhook";
        }
    });

    // Cover Studio Controls
    coverStyleChips.forEach(chip => {
        chip.addEventListener("click", async () => {
            coverStyleChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            selectedCoverStyle = chip.getAttribute("data-style");
            await triggerCoverGeneration();
        });
    });

    regenCoverBtn.addEventListener("click", async () => {
        await triggerCoverGeneration();
    });

    downloadCoverBtn.addEventListener("click", () => {
        if (!currentCoverUrl) return;
        const link = document.createElement("a");
        link.href = currentCoverUrl;
        link.download = `cover-${Date.now()}.jpg`;
        link.click();
        showToast("Downloaded HD cover image", "success");
    });

    copyCoverMdBtn.addEventListener("click", () => {
        if (!currentCoverUrl) return;
        const topic = topicInput.value || "AI Insights";
        const tag = `![${topic}](${currentCoverUrl})`;
        navigator.clipboard.writeText(tag);
        showToast("Cover markdown image tag copied!", "success");
        flashButtonText(copyCoverMdBtn, "Copied Tag!");
    });

    async function triggerCoverGeneration() {
        const topic = topicInput.value.trim() || (detectedVideoData ? detectedVideoData.title : "AI Architecture Masterclass");
        const channel = channelInput.value.trim() || "@krishnaik06";

        regenCoverBtn.disabled = true;
        regenCoverBtn.querySelector("span").textContent = "Rendering...";

        try {
            const res = await fetch("/api/generate-cover", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic, channel, style_key: selectedCoverStyle })
            });
            const data = await res.json();
            if (data.success && data.image_url) {
                renderCover(data.image_url, topic);
                appendLog(`[COVER] New ${selectedCoverStyle.toUpperCase()} banner rendered: ${data.image_url}`, "log-success");
                showToast("New cover banner generated", "success");
            }
        } catch (err) {
            appendLog(`[ERROR] Cover generation failed: ${err.message}`, "log-err");
        } finally {
            regenCoverBtn.disabled = false;
            regenCoverBtn.querySelector("span").textContent = "Regenerate Banner";
        }
    }

    // Memory toggle handler
    if (modalMemoryToggle && embedderGroup) {
        modalMemoryToggle.addEventListener("change", () => {
            embedderGroup.style.display = modalMemoryToggle.checked ? "block" : "none";
        });
    }

    // Reset Memory Handler
    if (resetMemoryBtn) {
        resetMemoryBtn.addEventListener("click", async () => {
            if (!confirm("Are you sure you want to reset and clear all agent memory embeddings? This will wipe cross-session recall and entity history.")) {
                return;
            }

            resetMemoryBtn.disabled = true;
            memoryResetStatus.className = "memory-reset-status";
            memoryResetStatus.textContent = "Clearing persistent memory tables...";

            try {
                const res = await fetch("/api/memory/reset", { method: "POST" });
                const data = await res.json();
                if (res.ok) {
                    memoryResetStatus.className = "memory-reset-status success";
                    memoryResetStatus.textContent = "✅ Agent memory cache reset successfully!";
                    appendLog("[SYSTEM] Agent contextual memory store cleared.", "log-success");
                    showToast("Agent contextual memory cleared", "success");
                } else {
                    memoryResetStatus.className = "memory-reset-status error";
                    memoryResetStatus.textContent = `❌ Reset failed: ${data.message || "Error"}`;
                }
            } catch (err) {
                memoryResetStatus.className = "memory-reset-status error";
                memoryResetStatus.textContent = `❌ Error: ${err.message}`;
            } finally {
                resetMemoryBtn.disabled = false;
                setTimeout(() => {
                    if (memoryResetStatus) memoryResetStatus.textContent = "";
                }, 3500);
            }
        });
    }

    // Open/Close Settings Modal
    openSettingsBtn.addEventListener("click", () => {
        if (memoryResetStatus) memoryResetStatus.textContent = "";
        settingsModal.classList.add("active");
    });
    closeSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("active"));
    cancelSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("active"));
    
    saveSettingsBtn.addEventListener("click", async () => {
        const apiKey = modalApiKey.value.trim();
        const modelName = modalModelSelect.value;
        const memoryEnabled = modalMemoryToggle ? modalMemoryToggle.checked : true;
        const embedderProvider = modalEmbedderSelect ? modalEmbedderSelect.value : "onnx";

        try {
            const res = await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    api_key: apiKey, 
                    model_name: modelName,
                    memory_enabled: memoryEnabled,
                    embedder_provider: embedderProvider
                })
            });
            const data = await res.json();
            if (data.status === "ok") {
                appendLog(`[SYSTEM] Settings saved: Model=${modelName}, Memory=${memoryEnabled ? 'ON' : 'OFF'} (${embedderProvider.toUpperCase()})`, "log-success");
                updateMemoryBadge(memoryEnabled, embedderProvider);
                if (headerModelText) headerModelText.textContent = modelName.split("/").pop().replace(":free", "");
                settingsModal.classList.remove("active");
                showToast("Configuration saved successfully", "success");
            }
        } catch (err) {
            appendLog(`[ERROR] Failed to save settings: ${err}`, "log-err");
        }
    });

    // Kickoff Form Submission
    generateForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (isRunning) return;

        const topic = topicInput.value.trim();
        const channel = channelInput.value.trim();

        if (!topic) return;

        isRunning = true;
        startBtn.disabled = true;
        startBtn.querySelector(".btn-text").textContent = "9 Agents Running...";
        startTimer();

        // Switch to terminal tab during execution
        document.querySelector('[data-tab="consoleTab"]').click();

        // Reset Pipeline UI
        setNodeState(nodeInput, "node-complete", "Active");
        setNodeState(nodeResearcher, "node-active", "Searching YT");
        setNodeState(nodeCrossVerifier, "node-idle", "Waiting");
        setNodeState(nodeWriter, "node-idle", "Waiting");
        setNodeState(nodeDiagrammer, "node-idle", "Waiting");
        setNodeState(nodeCodeQa, "node-idle", "Waiting");
        setNodeState(nodeEditor, "node-idle", "Waiting");
        setNodeState(nodeSeo, "node-idle", "Waiting");
        setNodeState(nodePodcast, "node-idle", "Waiting");
        setNodeState(nodeNewsletter, "node-idle", "Waiting");
        setNodeState(nodeOutput, "node-idle", "Queued");

        appendLog(`\n============================================================`, "log-info");
        appendLog(`🚀 Launching 9-Agent Master Studio Pipeline for: '${topic}'`, "log-info");
        appendLog(`📺 Target Source: ${channel}`, "log-info");
        appendLog(`============================================================\n`, "log-info");

        appendDialogueMsg("Master Coordinator", `Initiating 9-agent autonomous synthesis workflow for: "${topic}"`, "⚡", true);

        try {
            const response = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic, channel })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop(); // Keep partial line in buffer

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const rawData = line.substring(6);
                        try {
                            const event = JSON.parse(rawData);
                            handleStreamEvent(event);
                        } catch (err) {
                            appendLog(rawData);
                        }
                    }
                }
            }

        } catch (err) {
            appendLog(`[ERROR] Execution failed: ${err.message}`, "log-err");
            showToast(`Execution error: ${err.message}`, "error");
        } finally {
            isRunning = false;
            startBtn.disabled = false;
            startBtn.querySelector(".btn-text").textContent = "Launch 9-Agent Master Crew";
            stopTimer();
        }
    });

    function handleStreamEvent(event) {
        if (event.type === "log") {
            appendLog(event.message, event.level || "");
            const msg = event.message.toLowerCase();
            
            // 9-Agent Pipeline state transitions & Dialogue Inspector
            if (msg.includes("youtube content") || msg.includes("transcript researcher") || msg.includes("task 1")) {
                setNodeState(nodeResearcher, "node-active", "Extracting Video");
                appendDialogueMsg("Researcher Agent", "Extracting spoken transcript, core thesis, and terminology from YouTube...", "🔍");
            } else if (msg.includes("cross-verification") || msg.includes("cross-verifier") || msg.includes("task 2")) {
                setNodeState(nodeResearcher, "node-complete", "Complete");
                setNodeState(nodeCrossVerifier, "node-active", "Benchmarking");
                appendDialogueMsg("Cross-Verifier Agent", "Cross-checking video claims against official docs, benchmarks, and SOTA papers.", "🌐");
            } else if (msg.includes("master content writer") || msg.includes("technical storyteller") || msg.includes("task 3")) {
                setNodeState(nodeResearcher, "node-complete", "Complete");
                setNodeState(nodeCrossVerifier, "node-complete", "Complete");
                setNodeState(nodeWriter, "node-active", "Drafting Master Post");
                appendDialogueMsg("Master Writer", "Composing full-length architectural article with code patterns and deep takeaways.", "✍️");
            } else if (msg.includes("visual flow designer") || msg.includes("diagrammer") || msg.includes("task 4")) {
                setNodeState(nodeWriter, "node-complete", "Complete");
                setNodeState(nodeDiagrammer, "node-active", "Rendering Mermaid");
                appendDialogueMsg("Visual Architect", "Generating responsive Mermaid.js flowchart and component architecture diagram.", "📊");
            } else if (msg.includes("code quality inspector") || msg.includes("qa sandbox") || msg.includes("task 5")) {
                setNodeState(nodeDiagrammer, "node-complete", "Complete");
                setNodeState(nodeCodeQa, "node-active", "Testing Code & Syntax");
                appendDialogueMsg("Code QA Inspector", "Validating code syntax, imports, type safety, and docstrings.", "💻");
            } else if (msg.includes("editor-in-chief") || msg.includes("technical reviewer") || msg.includes("task 6")) {
                setNodeState(nodeCodeQa, "node-complete", "Complete");
                setNodeState(nodeEditor, "node-active", "Synthesizing Article");
                appendDialogueMsg("Editor-in-Chief", "Polishing voice, formatting tables, embedding diagrams, and producing final master markdown.", "🛡️");
            } else if (msg.includes("seo & social media") || msg.includes("growth strategist") || msg.includes("task 7")) {
                setNodeState(nodeEditor, "node-complete", "Complete");
                setNodeState(nodeSeo, "node-active", "SEO & Viral Hooks");
                appendDialogueMsg("SEO Strategist", "Crafting viral LinkedIn post, Twitter/X thread, and high-ranking search metadata.", "📈");
            } else if (msg.includes("podcast") || msg.includes("audio producer") || msg.includes("task 8")) {
                setNodeState(nodeSeo, "node-complete", "Complete");
                setNodeState(nodePodcast, "node-active", "Writing 2-Host Audio");
                appendDialogueMsg("Podcast Producer", "Writing dynamic 2-host conversational dialogue (Alex & Sam) and narration script.", "🎙️");
            } else if (msg.includes("newsletter") || msg.includes("email marketing") || msg.includes("task 9")) {
                setNodeState(nodePodcast, "node-complete", "Complete");
                setNodeState(nodeNewsletter, "node-active", "Crafting Edition");
                appendDialogueMsg("Newsletter Specialist", "Structuring Substack/Beehiiv edition with A/B subject lines and reader engagement polls.", "📧");
            }
        } else if (event.type === "complete") {
            // Set all nodes complete
            setNodeState(nodeResearcher, "node-complete", "Complete");
            setNodeState(nodeCrossVerifier, "node-complete", "Complete");
            setNodeState(nodeWriter, "node-complete", "Complete");
            setNodeState(nodeDiagrammer, "node-complete", "Complete");
            setNodeState(nodeCodeQa, "node-complete", "Complete");
            setNodeState(nodeEditor, "node-complete", "Complete");
            setNodeState(nodeSeo, "node-complete", "Complete");
            setNodeState(nodePodcast, "node-complete", "Complete");
            setNodeState(nodeNewsletter, "node-complete", "Complete");
            setNodeState(nodeOutput, "node-complete", "Ready");

            appendLog("\n✨ All 9 Agents Finished! Master Publishing Kit is Ready.", "log-success");
            appendDialogueMsg("Master Coordinator", "All 9 agent tasks finalized. Master kit (Article, Cover, Social, Podcast, Newsletter) ready for dispatch.", "✨", true);
            
            currentMarkdown = event.result || "";
            currentSocialMarkdown = event.social || "";
            currentPodcastMarkdown = event.podcast || "";
            currentNewsletterMarkdown = event.newsletter || "";
            const displayTopic = event.resolved_topic || (detectedVideoData ? detectedVideoData.title : topicInput.value);

            if (event.cover_url) {
                renderCover(event.cover_url, displayTopic);
            }

            renderArticle(currentMarkdown, displayTopic);
            renderSocialKit(currentSocialMarkdown);
            renderPodcast(currentPodcastMarkdown, displayTopic);
            renderNewsletter(currentNewsletterMarkdown);

            showToast("All 9 Agents Finished Successfully! Master Kit Ready.", "success");

            // Switch to Article Tab
            document.querySelector('[data-tab="articleTab"]').click();
        } else if (event.type === "error") {
            appendLog(`[ERROR] ${event.message}`, "log-err");
            appendDialogueMsg("System Alert", `Error during pipeline run: ${event.message}`, "❌", true);
            showToast(event.message, "error");
        }
    }

    function appendLog(text, level = "") {
        const span = document.createElement("div");
        if (level) span.classList.add(level);
        span.textContent = text;
        terminalLogs.appendChild(span);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    }

    function setNodeState(node, stateClass, badgeText) {
        if (!node) return;
        node.className = "pipeline-node " + stateClass;
        node.querySelector(".node-status-badge").textContent = badgeText;
    }

    function renderArticle(markdownText, topic) {
        if (!markdownText) return;
        currentMarkdown = markdownText;

        markdownOutput.innerHTML = marked.parse(markdownText);

        // Highlight code blocks
        if (window.hljs) {
            markdownOutput.querySelectorAll("pre code").forEach((el) => {
                if (!el.classList.contains("language-mermaid")) {
                    hljs.highlightElement(el);
                }
            });
        }

        // Render Mermaid Diagrams if present
        if (window.mermaid) {
            try {
                const mermaidBlocks = markdownOutput.querySelectorAll("pre code.language-mermaid");
                mermaidBlocks.forEach((block, idx) => {
                    const code = block.textContent;
                    const container = document.createElement("div");
                    container.className = "mermaid-diagram";
                    container.id = `mermaid-${idx}`;
                    block.parentElement.replaceWith(container);
                    mermaid.render(`mermaid-svg-${idx}`, code).then(({ svg }) => {
                        container.innerHTML = svg;
                    }).catch(err => {
                        console.log("Mermaid parse error:", err);
                        container.innerHTML = `<pre><code>${code}</code></pre>`;
                    });
                });
            } catch (err) {
                console.log("Mermaid rendering failed:", err);
            }
        }

        // Update Meta Bar
        const wordCount = markdownText.trim().split(/\s+/).length;
        const readTime = Math.max(1, Math.round(wordCount / 200));

        metaTopic.textContent = topic || "YouTube Master Insights";
        metaWordCount.textContent = `${wordCount.toLocaleString()} words`;
        metaReadTime.textContent = `${readTime} min read`;
        articleMetaBar.style.display = "flex";
    }

    function renderSocialKit(socialText) {
        if (!socialText) return;
        currentSocialMarkdown = socialText;

        socialKitContainer.innerHTML = `
            <div class="social-grid">
                <!-- LinkedIn Card -->
                <div class="social-card">
                    <div class="social-card-header">
                        <div class="social-card-title">
                            <span class="social-card-icon">💼</span>
                            <span>LinkedIn Authority Post</span>
                        </div>
                        <button class="social-copy-btn" id="copyLinkedInBtn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy Post</span>
                        </button>
                    </div>
                    <div class="social-card-body" id="linkedInBody">
                        ${marked.parse(extractSection(socialText, "LinkedIn") || socialText)}
                    </div>
                </div>

                <!-- Twitter / X Card -->
                <div class="social-card">
                    <div class="social-card-header">
                        <div class="social-card-title">
                            <span class="social-card-icon">🐦</span>
                            <span>Twitter / X Viral Thread</span>
                        </div>
                        <button class="social-copy-btn" id="copyTwitterBtn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy Thread</span>
                        </button>
                    </div>
                    <div class="social-card-body" id="twitterBody">
                        ${marked.parse(extractSection(socialText, "Twitter") || extractSection(socialText, "X") || socialText)}
                    </div>
                </div>

                <!-- SEO Metadata Card -->
                <div class="social-card" style="grid-column: 1 / -1;">
                    <div class="social-card-header">
                        <div class="social-card-title">
                            <span class="social-card-icon">🔍</span>
                            <span>SEO Metadata & High-Intent Keywords</span>
                        </div>
                        <button class="social-copy-btn" id="copySeoBtn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy SEO</span>
                        </button>
                    </div>
                    <div class="social-card-body" id="seoBody">
                        ${marked.parse(extractSection(socialText, "SEO") || socialText)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById("copyLinkedInBtn")?.addEventListener("click", () => {
            const raw = extractSection(socialText, "LinkedIn") || socialText;
            navigator.clipboard.writeText(raw);
            showToast("LinkedIn post copied!", "success");
            flashButtonText(document.getElementById("copyLinkedInBtn"), "Copied!");
        });

        document.getElementById("copyTwitterBtn")?.addEventListener("click", () => {
            const raw = extractSection(socialText, "Twitter") || extractSection(socialText, "X") || socialText;
            navigator.clipboard.writeText(raw);
            showToast("Twitter / X thread copied!", "success");
            flashButtonText(document.getElementById("copyTwitterBtn"), "Copied!");
        });

        document.getElementById("copySeoBtn")?.addEventListener("click", () => {
            const raw = extractSection(socialText, "SEO") || socialText;
            navigator.clipboard.writeText(raw);
            showToast("SEO tags copied!", "success");
            flashButtonText(document.getElementById("copySeoBtn"), "Copied!");
        });
    }

    function renderPodcast(podcastText, topic) {
        if (!podcastText) return;
        currentPodcastMarkdown = podcastText;

        if (podcastPlayerTitle) {
            podcastPlayerTitle.textContent = `${topic || "AI"} • Alex & Sam Deep Dive`;
        }

        podcastContainer.innerHTML = `
            <div class="social-grid">
                <div class="social-card" style="grid-column: 1 / -1;">
                    <div class="social-card-header">
                        <div class="social-card-title">
                            <span class="social-card-icon">🎙️</span>
                            <span>2-Host Conversational Dialogue & Voiceover Narration</span>
                        </div>
                        <button class="social-copy-btn" id="copyPodcastBtn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy Podcast Script</span>
                        </button>
                    </div>
                    <div class="social-card-body" style="line-height: 1.8;">
                        ${marked.parse(podcastText)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById("copyPodcastBtn")?.addEventListener("click", () => {
            navigator.clipboard.writeText(podcastText);
            showToast("Podcast script copied to clipboard!", "success");
            flashButtonText(document.getElementById("copyPodcastBtn"), "Copied Script!");
        });
    }

    function renderNewsletter(newsletterText) {
        if (!newsletterText) return;
        currentNewsletterMarkdown = newsletterText;

        newsletterContainer.innerHTML = `
            <div class="social-grid">
                <div class="social-card" style="grid-column: 1 / -1;">
                    <div class="social-card-header">
                        <div class="social-card-title">
                            <span class="social-card-icon">📧</span>
                            <span>Substack & Beehiiv Publication Edition</span>
                        </div>
                        <button class="social-copy-btn" id="copyNewsletterBtn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy Newsletter</span>
                        </button>
                    </div>
                    <div class="social-card-body" style="line-height: 1.8;">
                        ${marked.parse(newsletterText)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById("copyNewsletterBtn")?.addEventListener("click", () => {
            navigator.clipboard.writeText(newsletterText);
            showToast("Newsletter copied to clipboard!", "success");
            flashButtonText(document.getElementById("copyNewsletterBtn"), "Copied Newsletter!");
        });
    }

    function extractSection(markdown, sectionTitle) {
        if (!markdown) return "";
        const lines = markdown.split("\n");
        let capturing = false;
        const result = [];

        for (const line of lines) {
            if (line.match(new RegExp(`^#+\\s*.*${sectionTitle}`, "i"))) {
                capturing = true;
                result.push(line);
                continue;
            }
            if (capturing && line.match(/^#+\s+/)) {
                break;
            }
            if (capturing) {
                result.push(line);
            }
        }
        return result.length > 0 ? result.join("\n").trim() : "";
    }

    function flashButtonText(btn, msg) {
        const textSpan = btn.querySelector("span") || btn;
        const originalText = textSpan.textContent;
        textSpan.textContent = msg;
        setTimeout(() => {
            textSpan.textContent = originalText;
        }, 2000);
    }

    function updateMemoryBadge(enabled, provider = "onnx") {
        if (!memoryStatusBadge || !memoryStatusText) return;
        if (enabled) {
            memoryStatusBadge.className = "memory-badge active";
            memoryStatusText.textContent = `Memory: ON (${provider.toUpperCase()})`;
            memoryStatusBadge.title = `Contextual Memory Active: ${provider.toUpperCase()} Embeddings + Multi-Tier Storage`;
        } else {
            memoryStatusBadge.className = "memory-badge disabled";
            memoryStatusText.textContent = "Memory: OFF";
            memoryStatusBadge.title = "Contextual Memory is Disabled";
        }
    }

    async function fetchSettings() {
        try {
            const res = await fetch("/api/settings");
            const data = await res.json();
            if (data.api_key) {
                modalApiKey.value = data.api_key;
            }
            if (data.model_name) {
                modalModelSelect.value = data.model_name;
                if (headerModelText) headerModelText.textContent = data.model_name.split("/").pop().replace(":free", "");
                
                quickModelChips.forEach(chip => {
                    if (chip.getAttribute("data-model") === data.model_name) {
                        quickModelChips.forEach(c => c.classList.remove("active"));
                        chip.classList.add("active");
                    }
                });
            }
            if (modalMemoryToggle && data.memory_enabled !== undefined) {
                modalMemoryToggle.checked = Boolean(data.memory_enabled);
                if (embedderGroup) {
                    embedderGroup.style.display = data.memory_enabled ? "block" : "none";
                }
            }
            if (modalEmbedderSelect && data.embedder_provider) {
                modalEmbedderSelect.value = data.embedder_provider;
            }
            updateMemoryBadge(data.memory_enabled !== false, data.embedder_provider || "onnx");
        } catch (err) {
            console.log("Could not load initial settings:", err);
        }
    }

    function renderCover(imageUrl, topic) {
        if (!imageUrl) return;
        currentCoverUrl = imageUrl;
        const displayUrl = `${imageUrl}?t=${Date.now()}`;

        if (studioCoverImg) {
            studioCoverImg.src = displayUrl;
        }
        if (articleCoverImg && articleCoverContainer) {
            articleCoverImg.src = displayUrl;
            articleCoverContainer.style.display = "block";
        }
        if (coverTopicLabel) {
            coverTopicLabel.textContent = topic || "AI & Data Science Insights";
        }
    }

    async function fetchExistingArticle() {
        try {
            const res = await fetch("/api/article");
            const data = await res.json();
            if (data.content) {
                renderArticle(data.content, "AI vs ML vs Data Science");
                setNodeState(nodeOutput, "node-complete", "Ready");
            }
            if (data.social) {
                renderSocialKit(data.social);
                setNodeState(nodeSeo, "node-complete", "Ready");
            }
            if (data.podcast) {
                renderPodcast(data.podcast, "AI vs ML vs Data Science");
                setNodeState(nodePodcast, "node-complete", "Ready");
            }
            if (data.newsletter) {
                renderNewsletter(data.newsletter);
                setNodeState(nodeNewsletter, "node-complete", "Ready");
            }

            const coverRes = await fetch("/api/latest-cover");
            const coverData = await coverRes.json();
            if (coverData.exists && coverData.image_url) {
                renderCover(coverData.image_url, "AI vs ML vs Data Science");
            }
        } catch (err) {
            // No existing deliverables
        }
    }
});
