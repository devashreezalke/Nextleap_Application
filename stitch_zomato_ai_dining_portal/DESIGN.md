---
name: Obsidian Crimson AI
colors:
  surface: '#121316'
  surface-dim: '#121316'
  surface-bright: '#38393c'
  surface-container-lowest: '#0d0e11'
  surface-container-low: '#1b1b1f'
  surface-container: '#1f1f23'
  surface-container-high: '#292a2d'
  surface-container-highest: '#343538'
  on-surface: '#e3e2e6'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#e3e2e6'
  inverse-on-surface: '#303034'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#121316'
  on-background: '#e3e2e6'
  surface-variant: '#343538'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-sm:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1200px
  gutter: 24px
---

## Brand & Style
The design system is engineered to evoke a sense of high-end exclusivity and technological sophistication. It targets food enthusiasts who value curated, AI-driven insights over cluttered search results. 

The aesthetic is a fusion of **Modern Minimalism** and **Glassmorphism**. By utilizing a "Deep Obsidian" base, the interface allows food photography and "Zomato Red" accents to pop with high-intensity vibrance. The emotional response is one of trust, premium quality, and cutting-edge intelligence. UI elements are layered using translucent glass textures to create a sense of physical depth and digital lightness within a dark environment.

## Colors
This design system utilizes a high-contrast dark palette to maintain focus on visual content and AI recommendations.

- **Primary (Zomato Red):** Used for critical calls to action, brand identifiers, and active states. It should be applied with a subtle outer glow in high-impact areas.
- **Secondary (Emerald):** Reserved exclusively for positive ratings and "Open Now" indicators.
- **Tertiary (Amber):** Used for rankings, star icons, and "Must Try" badges.
- **Neutral (Obsidian):** The foundation of the UI. Backgrounds use a subtle radial gradient starting from `#12141A` at the center to `#0A0B0E` at the edges to prevent a flat appearance.
- **Surfaces:** Use translucent layers with a 15px backdrop blur to maintain legibility over background photography.

## Typography
The typographic strategy balances editorial elegance with functional clarity.

- **Headlines:** 'Playfair Display' provides a literary, authoritative feel for restaurant names and AI-generated summaries. It should be used with tight letter-spacing for large titles.
- **UI & Body:** 'Outfit' is chosen for its geometric purity and modern proportions. It ensures high legibility for menu items, distances, and technical details.
- **Hierarchy:** Use 'Playfair Display' for storytelling and 'Outfit' for all data-driven interactions. Mobile sizes are strictly enforced to maintain a maximum of 32px for titles to ensure visual balance on narrow viewports.

## Layout & Spacing
The system employs a **Fluid Grid** approach with a 12-column structure for desktop and a 4-column structure for mobile.

- **Margins:** Desktop utilizes 48px side margins, while mobile scales down to 16px.
- **Rhythm:** An 8px base grid drives all vertical spacing. Elements like cards use "md" (24px) padding to provide breathing room for glass textures.
- **Container:** Main content is capped at 1200px to maintain readability of AI summaries.
- **Transitions:** Layout shifts between viewports should use smooth CSS transitions (300ms) to maintain the premium feel.

## Elevation & Depth
Depth is created through **Glassmorphism** and tonal stacking rather than traditional black shadows.

1.  **Level 0 (Base):** Deep Obsidian (#0A0B0E).
2.  **Level 1 (Cards):** Translucent Charcoal Glass (70% opacity) with a 15px backdrop blur and a 1px border at 5% white.
3.  **Level 2 (Modals/Popovers):** Higher opacity glass (85%) with a subtle inner glow (#FFFFFF 0.03) to simulate a light source from the top-left.
4.  **Interaction:** When hovered, cards should scale by 1.02x and the border opacity should increase to 15%, accompanied by a faint Zomato Red outer glow (blur: 20px, spread: -5px).

## Shapes
The shape language is "Rounded," striking a balance between organic comfort and geometric precision.

- **Cards:** Use 1rem (16px) corner radius.
- **Buttons & Tags:** Use pill-shaped (full-round) geometry to differentiate interactive elements from informational containers.
- **Inputs:** Utilize the standard 0.5rem (8px) radius to maintain a structural, reliable appearance.

## Components
- **Buttons:** Primary buttons use a linear gradient (Zomato Red to a slightly darker Crimson). Text is white with a slight semi-bold weight. Secondary buttons are "Ghost" style with a glass background and red border.
- **Glassmorphic Cards:** Feature a high-contrast image at the top with a gradient overlay that transitions into the glass surface. Text within cards uses white at 90% opacity for primary info and 60% for secondary metadata.
- **Custom Range Sliders:** The track is a muted dark charcoal. The "active" portion of the track and the thumb should be Zomato Red. The thumb features a subtle glow effect.
- **AI Summary Chips:** Small, pill-shaped tags with a subtle red-to-purple gradient border to denote "AI Intelligence."
- **Rating Badges:** Solid background blocks (Emerald for 4+, Amber for 3+) with white text, positioned at the top-right of restaurant cards.
- **Input Fields:** Dark glass backgrounds with a 1px border. On focus, the border transitions to Zomato Red with a 2px outer glow.