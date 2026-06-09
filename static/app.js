document.addEventListener("DOMContentLoaded", () => {
    // DOM Selectors
    const form = document.getElementById("preferences-form");
    const locationInput = document.getElementById("location-input");
    const cuisineInput = document.getElementById("cuisine-input");
    const budgetInput = document.getElementById("budget-input");
    const ratingInput = document.getElementById("rating-input");
    const topkInput = document.getElementById("topk-input");
    const additionalInput = document.getElementById("additional-input");
    
    const ratingDisplay = document.getElementById("rating-val-display");
    const topkDisplay = document.getElementById("topk-val-display");
    const charCounter = document.getElementById("char-counter");
    
    // Budget Toggle Buttons
    const budgetChips = document.querySelectorAll(".budget-chip");
    
    // View state containers
    const emptyState = document.getElementById("empty-state");
    const loadingState = document.getElementById("loading-state");
    const loadingMsg = document.getElementById("loading-msg");
    const fallbackBanner = document.getElementById("fallback-banner");
    const resultsContent = document.getElementById("results-content");
    const aiSummaryText = document.getElementById("ai-summary-text");
    const recommendationsGrid = document.getElementById("recommendations-grid");
    
    // Datalists
    const locationsDatalist = document.getElementById("locations-list");
    const cuisinesDatalist = document.getElementById("cuisines-list");

    // Initialize Autocomplete Metadata
    initMetadata();

    // Event Handlers for sliders
    ratingInput.addEventListener("input", (e) => {
        ratingDisplay.textContent = `${parseFloat(e.target.value).toFixed(1)} ★`;
    });

    topkInput.addEventListener("input", (e) => {
        topkDisplay.textContent = e.target.value;
    });

    // Character Counter for Textarea
    additionalInput.addEventListener("input", (e) => {
        const count = e.target.value.length;
        charCounter.textContent = `${count} / 300`;
    });

    // Budget chip selection
    budgetChips.forEach(chip => {
        chip.addEventListener("click", () => {
            budgetChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            budgetInput.value = chip.dataset.value;
        });
    });

    // Fetch and populate Autocomplete lists
    async function initMetadata() {
        try {
            const [locRes, cuisRes] = await Promise.all([
                fetch("/api/v1/metadata/locations"),
                fetch("/api/v1/metadata/cuisines")
            ]);

            if (locRes.ok) {
                const locations = await locRes.json();
                locationsDatalist.innerHTML = locations.map(loc => `<option value="${loc}">`).join("");
            }
            if (cuisRes.ok) {
                const cuisines = await cuisRes.json();
                cuisinesDatalist.innerHTML = cuisines.map(c => `<option value="${c}">`).join("");
            }
        } catch (err) {
            console.warn("Failed to retrieve autocomplete metadata lists.", err);
        }
    }

    // Dynamic message rotator for loading state
    let messageInterval;
    const loadingMessages = [
        "Consulting local Zomato records...",
        "Applying structural criteria filters...",
        "Formulating candidate context table...",
        "Orchestrating recommendations with Groq LLM...",
        "Generating personalized explanation metrics..."
    ];

    function startLoadingSequence() {
        let idx = 0;
        loadingMsg.textContent = loadingMessages[0];
        messageInterval = setInterval(() => {
            idx = (idx + 1) % loadingMessages.length;
            loadingMsg.textContent = loadingMessages[idx];
        }, 1800);
    }

    function stopLoadingSequence() {
        clearInterval(messageInterval);
    }

    // Form Submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // 1. Setup view states
        emptyState.classList.add("hidden");
        resultsContent.classList.add("hidden");
        fallbackBanner.classList.add("hidden");
        loadingState.classList.remove("hidden");
        recommendationsGrid.innerHTML = "";
        
        startLoadingSequence();

        // 2. Build payload preferences object
        const preferences = {
            location: locationInput.value,
            cuisine: cuisineInput.value || null,
            budget: budgetInput.value,
            min_rating: parseFloat(ratingInput.value),
            additional_preferences: additionalInput.value || null,
            top_k: parseInt(topkInput.value, 10)
        };

        try {
            const response = await fetch("/api/v1/recommendations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(preferences)
            });

            stopLoadingSequence();
            loadingState.classList.add("hidden");

            if (!response.ok) {
                const errData = await response.json();
                alert(`Error: ${errData.detail || "Failed to retrieve recommendations."}`);
                emptyState.classList.remove("hidden");
                return;
            }

            const data = await response.json();

            // 3. Render Results
            if (data.recommendations.length === 0) {
                // Empty set scenario
                aiSummaryText.textContent = data.summary || "No matching restaurants found.";
                resultsContent.classList.remove("hidden");
                return;
            }

            // Show fallback warning if LLM failed and we serve pre-sorted listings directly
            if (data.meta && data.meta.fallback) {
                fallbackBanner.classList.remove("hidden");
            }

            aiSummaryText.textContent = data.summary;

            // Generate card list
            data.recommendations.forEach(item => {
                const card = createRecommendationCard(item);
                recommendationsGrid.appendChild(card);
            });

            resultsContent.classList.remove("hidden");

        } catch (err) {
            stopLoadingSequence();
            loadingState.classList.add("hidden");
            emptyState.classList.remove("hidden");
            alert("Connection error: Unable to contact recommendation backend.");
            console.error(err);
        }
    });

    // Helper to generate dynamic HTML components representing the cards
    function createRecommendationCard(item) {
        const rest = item.restaurant;
        
        // Cuisine list formatting
        const cuisinesHTML = rest.cuisines
            .map(c => `<span class="cuisine-tag">${c}</span>`)
            .join("");

        // Budget format
        const budgetCurrency = rest.budget_band === "low" ? "₹" : rest.budget_band === "medium" ? "₹₹" : "₹₹₹";

        const cardEl = document.createElement("div");
        cardEl.className = "recommendation-card card-surface";
        cardEl.innerHTML = `
            <div class="rank-indicator">
                <div class="rank-number">#${item.rank}</div>
                <div class="rank-label">Rank</div>
            </div>
            <div class="card-main">
                <div class="card-header-row">
                    <h3 class="restaurant-name">${rest.name}</h3>
                    <div class="meta-badges">
                        <div class="rating-badge">${rest.rating.toFixed(1)} ★</div>
                        <span class="votes-count">(${rest.votes} reviews)</span>
                    </div>
                </div>
                
                <div class="info-details">
                    <div class="info-item">
                        <span class="icon">📍</span>
                        <span>${rest.location}</span>
                    </div>
                    <div class="info-item">
                        <span class="icon">💰</span>
                        <span>Cost for two: Rs. ${rest.estimated_cost} (${budgetCurrency})</span>
                    </div>
                </div>

                <div class="cuisines-row">
                    ${cuisinesHTML}
                </div>

                <div class="ai-reasoning-panel">
                    <p>${item.explanation}</p>
                </div>
            </div>
        `;

        return cardEl;
    }
});
