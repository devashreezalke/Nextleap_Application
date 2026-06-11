import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';

// Type definitions matching the backend Pydantic models
interface Restaurant {
  id: string;
  name: string;
  location: string;
  cuisines: string[];
  rating: number;
  estimated_cost: number;
  budget_band: "low" | "medium" | "high";
  votes: number;
  address: string;
}

interface Recommendation {
  rank: number;
  restaurant: Restaurant;
  explanation: string;
}

interface RecommendationsMeta {
  candidates_considered?: number;
  filters_applied?: string[];
  fallback?: boolean;
}

interface RecommendationsResponse {
  summary: string | null;
  recommendations: Recommendation[];
  meta?: RecommendationsMeta;
}

// Moody premium restaurant/food stock images to map dynamically to recommendations
const STOCK_IMAGES = [
  "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1544148103-0773bf10d330?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1565958011703-44f9829ba187?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1484723091739-30a097e8f929?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=600&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=600&auto=format&fit=crop"
];

// Loading messages sequence
const LOADING_MESSAGES = [
  "Consulting local Zomato records...",
  "Applying structural criteria filters...",
  "Formulating candidate context table...",
  "Orchestrating recommendations with Groq LLM...",
  "Generating personalized explanation metrics..."
];

export default function App() {
  // Input fields states
  const [location, setLocation] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [budgetTier, setBudgetTier] = useState<'low' | 'medium' | 'high'>('medium');
  const [minRating, setMinRating] = useState(3.5);
  const [vibe, setVibe] = useState('');

  // Auto-complete metadata lists
  const [locationsList, setLocationsList] = useState<string[]>([]);
  const [cuisinesList, setCuisinesList] = useState<string[]>([]);

  // Response/UI states
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0]);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState('');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isFallback, setIsFallback] = useState(false);

  // Fetch metadata lists on mount
  useEffect(() => {
    async function fetchMetadata() {
      try {
        const [locRes, cuisRes] = await Promise.all([
          fetch("/api/v1/metadata/locations"),
          fetch("/api/v1/metadata/cuisines")
        ]);
        if (locRes.ok) {
          const locData = await locRes.json();
          setLocationsList(locData);
        }
        if (cuisRes.ok) {
          const cuisData = await cuisRes.json();
          setCuisinesList(cuisData);
        }
      } catch (err) {
        console.warn("Failed to retrieve autocomplete metadata lists.", err);
      }
    }
    fetchMetadata();
  }, []);

  // Loading message rotator
  useEffect(() => {
    if (!loading) return;
    let idx = 0;
    setLoadingMsg(LOADING_MESSAGES[0]);
    const interval = setInterval(() => {
      idx = (idx + 1) % LOADING_MESSAGES.length;
      setLoadingMsg(LOADING_MESSAGES[idx]);
    }, 1800);
    return () => clearInterval(interval);
  }, [loading]);

  // Form submission handler
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!location.trim()) {
      alert("Please specify a location!");
      return;
    }

    setLoading(true);
    setSubmitted(true);
    setError(null);
    setRecommendations([]);
    setSummary('');
    setIsFallback(false);

    try {
      const payload = {
        location: location.trim(),
        cuisine: cuisine.trim() || null,
        budget: budgetTier,
        min_rating: minRating,
        additional_preferences: vibe.trim() || null,
        top_k: 5
      };

      const response = await fetch("/api/v1/recommendations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      setLoading(false);

      if (!response.ok) {
        const errData = await response.json();
        setError(errData.detail || "Failed to retrieve recommendations.");
        return;
      }

      const data: RecommendationsResponse = await response.json();

      if (data.recommendations.length === 0) {
        setSummary(data.summary || "No matching restaurants found in this location.");
        setRecommendations([]);
        return;
      }

      if (data.meta && data.meta.fallback) {
        setIsFallback(true);
      }

      setSummary(data.summary || '');
      setRecommendations(data.recommendations);

    } catch (err) {
      setLoading(false);
      setError("Connection error: Unable to contact recommendation backend.");
      console.error(err);
    }
  };

  // Reset form filters
  const handleReset = () => {
    setLocation('');
    setCuisine('');
    setBudgetTier('medium');
    setMinRating(3.5);
    setVibe('');
    setSubmitted(false);
    setError(null);
    setRecommendations([]);
    setSummary('');
    setIsFallback(false);
  };

  // Helper to get a deterministic stock image for a restaurant based on its name/id
  const getRestaurantImage = (name: string, id: string): string => {
    const hashStr = name + id;
    let hash = 0;
    for (let i = 0; i < hashStr.length; i++) {
      hash = hashStr.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash) % STOCK_IMAGES.length;
    return STOCK_IMAGES[index];
  };

  return (
    <>
      {/* Sticky Header */}
      <header className="app-header fixed top-0 w-full z-50 bg-background/70 backdrop-blur-md border-b border-white/5 shadow-xl flex justify-between items-center h-20 px-gutter max-w-container-max mx-auto left-0 right-0">
        <div className="flex items-center gap-sm">
          <h1 className="font-headline-md text-headline-md font-black tracking-tighter text-on-surface" id="app-title">
            Zomato <span className="text-crimson">AI</span>
          </h1>
          <span 
            className="material-symbols-outlined text-crimson" 
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            auto_awesome
          </span>
        </div>
        
        <div className="hidden md:flex gap-lg h-full items-center">
          <a className="h-full flex items-center text-crimson font-bold border-b-2 border-crimson text-label-md font-label-md" href="#">Discover</a>
          <a className="h-full flex items-center text-on-surface/60 font-medium hover:text-on-surface transition-colors text-label-md font-label-md" href="#">Trending</a>
          <a className="h-full flex items-center text-on-surface/60 font-medium hover:text-on-surface transition-colors text-label-md font-label-md" href="#">Saved</a>
          <a className="h-full flex items-center text-on-surface/60 font-medium hover:text-on-surface transition-colors text-label-md font-label-md" href="#">History</a>
        </div>

        <div className="flex items-center gap-md">
          <span className="tagline hidden lg:block text-on-surface-variant font-label-sm text-label-sm italic opacity-80">
            Personalized Dining Recommendations Powered by Llama-3
          </span>
          <button className="hidden md:block text-on-surface font-label-md text-label-md px-sm py-xs hover:bg-white/5 rounded-lg transition-all duration-300">Sign In</button>
          <button className="gradient-crimson text-white font-label-md text-label-md px-md py-sm rounded-lg hover:opacity-90 transition-opacity font-semibold shadow-lg shadow-crimson/20">
            Try Llama-3
          </button>
          <img 
            alt="User profile" 
            className="w-10 h-10 rounded-full border border-white/10 ml-sm hidden sm:block"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAIxy0jC3z6oyoU_CCWKq1oGmjLUhsAqWN4k03iNBPVOUjq7xrqwK2qMXhZYqAQDQtBIVIHE4FEGJju-CihruEsMLPM9gKWwsVTAqRpTy4sfhihJJabaDeO7B01sH1YladEJm6_vtdvPzf_czsf5fiyzA4wPNijv0m6RgWVpfBsUpeXmfFEIOL2MH2e2KjBGF3uKoEre93-uHkjSYvumU-7eg59LwjN4LMiImQ-yno6fIwXiy7xPmHgyFtXiv-6MyGUvYIbyyLrS28" 
          />
        </div>
      </header>

      {/* Main Container */}
      <main className="main-container flex-grow pt-24 pb-lg px-gutter max-w-container-max mx-auto w-full flex flex-col lg:flex-row gap-lg">
        {/* Left Side: Preferences Aside */}
        <aside className="w-full lg:w-[420px] shrink-0">
          <form 
            onSubmit={handleSubmit}
            className="card-surface glass-panel rounded-xl p-md flex flex-col gap-base sticky top-28 shadow-2xl max-h-[calc(100vh-120px)] overflow-y-auto" 
            id="preferences-form"
          >
            <div className="mb-sm">
              <h2 className="font-headline-sm text-headline-sm text-on-surface flex items-center gap-xs">
                <span className="material-symbols-outlined">tune</span>
                Dining Profile
              </h2>
              <p className="text-on-surface-variant font-label-sm text-label-sm mt-xs">Powered by Llama-3</p>
            </div>

            {/* Location Input */}
            <div className="flex flex-col gap-xs">
              <label htmlFor="location-input" className="text-on-surface-variant font-label-sm text-label-sm ml-xs">Location</label>
              <div className="glass-input rounded-lg flex items-center px-sm py-sm gap-sm">
                <span className="material-symbols-outlined text-on-surface/50">location_on</span>
                <input 
                  id="location-input"
                  list="locations-list"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="bg-transparent border-none outline-none text-on-surface font-body-md text-body-md w-full placeholder-on-surface/30 focus:ring-0 p-0" 
                  placeholder="e.g. Koramangala, Indiranagar" 
                  type="text"
                  required
                  autoComplete="off"
                />
                <datalist id="locations-list">
                  {locationsList.map((loc) => (
                    <option key={loc} value={loc} />
                  ))}
                </datalist>
              </div>
            </div>

            {/* Cuisine Input */}
            <div className="flex flex-col gap-xs mt-sm">
              <label htmlFor="cuisine-input" className="text-on-surface-variant font-label-sm text-label-sm ml-xs">Cuisine</label>
              <div className="glass-input rounded-lg flex items-center px-sm py-sm gap-sm">
                <span className="material-symbols-outlined text-on-surface/50">restaurant</span>
                <input 
                  id="cuisine-input"
                  list="cuisines-list"
                  value={cuisine}
                  onChange={(e) => setCuisine(e.target.value)}
                  className="bg-transparent border-none outline-none text-on-surface font-body-md text-body-md w-full placeholder-on-surface/30 focus:ring-0 p-0" 
                  placeholder="e.g. Japanese, Italian, Chinese" 
                  type="text"
                  autoComplete="off"
                />
                <datalist id="cuisines-list">
                  {cuisinesList.map((cuis) => (
                    <option key={cuis} value={cuis} />
                  ))}
                </datalist>
              </div>
            </div>

            {/* Budget */}
            <div className="flex flex-col gap-xs mt-sm">
              <label className="text-on-surface-variant font-label-sm text-label-sm ml-xs">Budget Band</label>
              <div className="flex gap-sm" id="budget-container">
                <button 
                  type="button"
                  onClick={() => setBudgetTier('low')}
                  className={`budget-chip flex-1 py-xs rounded-lg border transition-all font-label-md text-label-md ${
                    budgetTier === 'low' 
                      ? 'border-crimson bg-crimson/10 text-crimson active' 
                      : 'border-white/10 text-on-surface/70 hover:bg-white/5'
                  }`}
                >
                  ₹
                  <span className="block text-[9px] opacity-65">&le; 500</span>
                </button>
                <button 
                  type="button"
                  onClick={() => setBudgetTier('medium')}
                  className={`budget-chip flex-1 py-xs rounded-lg border transition-all font-label-md text-label-md ${
                    budgetTier === 'medium' 
                      ? 'border-crimson bg-crimson/10 text-crimson active' 
                      : 'border-white/10 text-on-surface/70 hover:bg-white/5'
                  }`}
                >
                  ₹₹
                  <span className="block text-[9px] opacity-65">501-1500</span>
                </button>
                <button 
                  type="button"
                  onClick={() => setBudgetTier('high')}
                  className={`budget-chip flex-1 py-xs rounded-lg border transition-all font-label-md text-label-md ${
                    budgetTier === 'high' 
                      ? 'border-crimson bg-crimson/10 text-crimson active' 
                      : 'border-white/10 text-on-surface/70 hover:bg-white/5'
                  }`}
                >
                  ₹₹₹
                  <span className="block text-[9px] opacity-65">&gt; 1500</span>
                </button>
              </div>
            </div>

            {/* Rating Slider */}
            <div className="flex flex-col gap-xs mt-sm">
              <div className="flex justify-between items-center ml-xs mr-xs">
                <label className="text-on-surface-variant font-label-sm text-label-sm">Minimum Rating</label>
                <span className="font-label-md text-label-md text-crimson font-bold" id="rating-val-display">
                  {minRating.toFixed(1)}+ ★
                </span>
              </div>
              <div className="px-xs mt-xs">
                <input 
                  id="rating-input" 
                  max="5.0" 
                  min="1.0" 
                  step="0.1" 
                  type="range" 
                  value={minRating}
                  onChange={(e) => setMinRating(parseFloat(e.target.value))}
                />
              </div>
            </div>

            {/* Vibe input */}
            <div className="flex flex-col gap-xs mt-sm">
              <div className="flex justify-between items-center ml-xs mr-xs">
                <label className="text-on-surface-variant font-label-sm text-label-sm">Atmosphere &amp; Vibe</label>
                <span className={`font-label-sm text-label-sm ${vibe.length > 300 ? 'text-crimson' : 'text-on-surface/40'}`} id="char-counter">
                  {vibe.length}/300
                </span>
              </div>
              <textarea 
                id="additional-input"
                value={vibe}
                onChange={(e) => setVibe(e.target.value.slice(0, 300))}
                className="glass-input rounded-lg bg-transparent text-on-surface font-body-md text-body-md w-full placeholder-on-surface/30 focus:ring-0 p-sm resize-none" 
                placeholder="Describe the vibe... e.g. 'Cozy date night with dim lighting and jazz music, outdoor seating'" 
                rows={3}
              />
            </div>

            {/* Action buttons */}
            <button 
              type="submit"
              disabled={loading}
              className="submit-btn gradient-crimson text-white font-label-md text-label-md font-semibold py-sm rounded-lg mt-md shadow-lg shadow-crimson/20 hover:shadow-crimson/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 flex justify-center items-center gap-xs disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[18px]">magic_button</span>
              Generate Recommendations
            </button>
            
            <button 
              type="button"
              onClick={handleReset}
              className="text-on-surface-variant font-label-sm text-label-sm mt-xs hover:text-on-surface transition-colors underline underline-offset-4"
            >
              Reset Filters
            </button>
          </form>
        </aside>

        {/* Right Side: Results Section */}
        <section className="flex-grow flex flex-col gap-md min-h-[600px]" id="results-container">
          {/* Default Empty State */}
          {!submitted && (
            <div className="flex-grow flex flex-col items-center justify-center opacity-50 py-16" id="empty-state">
              <span className="material-symbols-outlined text-[80px] text-on-surface/20 mb-md">restaurant_menu</span>
              <h3 className="font-headline-md text-headline-md text-on-surface/50 text-center">Hungry for Recommendations?</h3>
              <p className="font-body-lg text-body-lg text-on-surface/40 mt-sm text-center max-w-md">
                Adjust your preferences on the left and let our AI curate the perfect dining experience for you.
              </p>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div id="loading-state" className="w-full flex flex-col gap-md py-8">
              <div className="flex items-center gap-sm text-crimson font-label-md text-label-md mb-sm">
                <span 
                  className="material-symbols-outlined animate-spin loading-spinner"
                  style={{ fontVariationSettings: "'FILL' 0" }}
                >
                  progress_activity
                </span>
                {loadingMsg}
              </div>
              
              <div className="glass-card rounded-xl p-md skeleton-card">
                <div className="h-6 w-1/3 skeleton-shimmer rounded mb-sm"></div>
                <div className="h-4 w-full skeleton-shimmer rounded mb-xs"></div>
                <div className="h-4 w-5/6 skeleton-shimmer rounded"></div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-md mt-md">
                <div className="glass-card rounded-xl h-64 skeleton-card skeleton-shimmer"></div>
                <div className="glass-card rounded-xl h-64 skeleton-card skeleton-shimmer"></div>
              </div>
            </div>
          )}

          {/* Error panel */}
          {!loading && submitted && error && (
            <div className="glass-card border-l-[4px] border-error rounded-xl p-md flex items-start gap-md">
              <div className="bg-error-container/20 p-sm rounded-lg text-error shrink-0">
                <span className="material-symbols-outlined">error</span>
              </div>
              <div>
                <h3 className="font-headline-sm text-headline-sm text-error mb-xs">Search Failed</h3>
                <p className="text-on-surface-variant font-body-md text-body-md leading-relaxed">
                  {error}
                </p>
              </div>
            </div>
          )}

          {/* Fallback Warning Banner */}
          {!loading && submitted && isFallback && (
            <div className="fallback-banner flex gap-sm items-center bg-amber-500/10 border border-amber-500/30 text-amber-500 rounded-xl p-md mb-xs">
              <span className="material-symbols-outlined shrink-0 text-amber-500">warning</span>
              <div className="fallback-content">
                <h4 className="font-bold font-headline-sm text-[15px] mb-xs">Generative AI Engine Offline</h4>
                <p className="text-on-surface-variant text-[13px] leading-relaxed">
                  We are serving pre-filtered database records sorted by rating directly. Review explanations may be generic.
                </p>
              </div>
            </div>
          )}

          {/* Recommendations content */}
          {!loading && submitted && !error && (
            <>
              {/* AI synthesis / Welcome Summary */}
              {summary && (
                <div id="ai-summary-card" className="glass-card rounded-xl p-md relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1 h-full gradient-crimson"></div>
                  <div className="flex items-start gap-md relative z-10">
                    <div className="bg-crimson/10 p-sm rounded-lg text-crimson shrink-0">
                      <span className="material-symbols-outlined">auto_awesome</span>
                    </div>
                    <div>
                      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-xs">AI Synthesis</h3>
                      <p id="ai-summary-text" className="font-headline-md text-[18px] md:text-[20px] italic text-on-surface/90 leading-relaxed">
                        "{summary}"
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Cards Grid */}
              {recommendations.length > 0 && (
                <div id="recommendations-grid" className="grid grid-cols-1 xl:grid-cols-2 gap-md mt-sm">
                  {recommendations.map((item) => {
                    const rest = item.restaurant;
                    const cardImg = getRestaurantImage(rest.name, rest.id);
                    const budgetCurrency = rest.budget_band === 'low' ? '₹' : rest.budget_band === 'medium' ? '₹₹' : '₹₹₹';

                    return (
                      <article key={rest.id} className="recommendation-card glass-card rounded-xl overflow-hidden flex flex-col group">
                        <div 
                          className="relative h-48 w-full bg-surface-container-high" 
                          style={{ 
                            backgroundImage: `url('${cardImg}')`, 
                            backgroundSize: 'cover', 
                            backgroundPosition: 'center' 
                          }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent opacity-90"></div>
                          <div className="absolute top-sm left-sm bg-crimson text-white font-label-md text-label-md font-bold px-sm py-xs rounded-lg shadow-lg flex items-center gap-xs">
                            <span className="material-symbols-outlined text-[16px]">trophy</span> #{item.rank} Match
                          </div>
                          <div className="absolute top-sm right-sm bg-secondary-container text-white font-label-sm text-label-sm font-bold px-sm py-xs rounded-lg shadow-lg flex items-center gap-xs rating-badge">
                            {rest.rating.toFixed(1)} 
                            <span 
                              className="material-symbols-outlined text-[14px]" 
                              style={{ fontVariationSettings: "'FILL' 1" }}
                            >
                              star
                            </span>
                          </div>
                        </div>
                        
                        <div className="p-md flex flex-col flex-grow z-10 -mt-10">
                          <h4 className="font-headline-sm text-headline-sm text-on-surface mb-xs drop-shadow-md">
                            {rest.name}
                          </h4>
                          
                          <div className="flex items-center gap-sm text-on-surface/60 font-label-sm text-label-sm mb-md">
                            <span className="flex items-center gap-[2px]">
                              <span className="material-symbols-outlined text-[16px]">location_on</span> 
                              {rest.location}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-[2px] text-crimson font-bold">
                              <span className="material-symbols-outlined text-[16px]">payments</span>
                              Cost: Rs. {rest.estimated_cost} ({budgetCurrency})
                            </span>
                            <span>•</span>
                            <span>{rest.votes} Reviews</span>
                          </div>

                          <div className="flex gap-xs mb-md flex-wrap">
                            {rest.cuisines.map((c) => (
                              <span 
                                key={c}
                                className="cuisine-tag text-[11px] font-semibold tracking-wider uppercase px-sm py-xs rounded-full border border-white/10 bg-white/5 text-on-surface/80"
                              >
                                {c}
                              </span>
                            ))}
                          </div>

                          <div className="ai-reasoning-panel mt-auto bg-surface-container/50 border-l-[3px] border-crimson p-sm rounded-r-lg">
                            <p className="font-body-sm text-[13px] text-on-surface/80 leading-relaxed">
                              <span className="font-bold text-crimson mr-xs">Why this fits:</span> 
                              {item.explanation}
                            </p>
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full py-lg mt-xl bg-surface-dim border-t border-white/5">
        <div className="flex flex-col md:flex-row justify-between items-center px-gutter max-w-container-max mx-auto gap-md">
          <div className="font-label-md text-label-md font-bold text-crimson">Zomato AI</div>
          <div className="text-on-surface-variant font-label-sm text-label-sm">© 2026 Zomato AI. Intelligence by Meta Llama-3.</div>
          <div className="flex gap-md">
            <a className="text-on-surface/40 hover:text-on-surface transition-colors font-label-sm text-label-sm hover:underline underline-offset-4" href="#">Privacy Policy</a>
            <a className="text-on-surface/40 hover:text-on-surface transition-colors font-label-sm text-label-sm hover:underline underline-offset-4" href="#">Terms of Service</a>
            <a className="text-on-surface/40 hover:text-on-surface transition-colors font-label-sm text-label-sm hover:underline underline-offset-4" href="#">AI Ethics</a>
          </div>
        </div>
      </footer>
    </>
  );
}
