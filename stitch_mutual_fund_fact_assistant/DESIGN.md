---
name: Luminous Finance
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#3c4a43'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#6b7b72'
  outline-variant: '#bacac1'
  surface-tint: '#006c4f'
  primary: '#006c4f'
  on-primary: '#ffffff'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#2fe0aa'
  secondary: '#545f73'
  on-secondary: '#ffffff'
  secondary-container: '#d5e0f8'
  on-secondary-container: '#586377'
  tertiary: '#505f76'
  on-tertiary: '#ffffff'
  tertiary-container: '#a8b9d2'
  on-tertiary-container: '#3a495f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0.01em
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
  xl: 48px
  container-max: 1200px
  gutter: 20px
---

## Brand & Style
The design system is engineered for the modern investor, blending the transparency of high-growth fintech with the stability of traditional wealth management. The brand personality is optimistic yet disciplined, evoking a sense of clarity and effortless control over complex financial data.

The aesthetic follows a **Modern Minimalist** movement with **Glassmorphic** accents. It prioritizes high-density information through generous whitespace and a strictly governed color application. The user experience should feel "light" and "breathable," utilizing subtle depth and translucency to suggest a multi-layered, sophisticated financial environment without visual clutter.

## Colors
The palette is anchored by a high-vibrancy **Emerald Green** (#00D09C) which symbolizes growth and action. This primary accent is reserved for interactive elements, success states, and key financial indicators.

The canvas uses a layered approach:
- **Base Layer:** Pure #FFFFFF for primary containers and chat bubbles.
- **Surface Layer:** #F8FAFC for background contrast to distinguish between navigation and content.
- **Typography:** #1E293B (Slate-900) ensures AAA accessibility and a premium, weighted feel for headings, while #64748B is used for secondary metadata.
- **Dividers:** Soft #E2E8F0 borders maintain structure without creating visual "boxes."

## Typography
This design system utilizes a dual-font strategy. **Outfit** is used for headings to provide a geometric, modern, and welcoming character. **Inter** is utilized for body text and UI labels due to its exceptional legibility in data-heavy environments.

Tracking (letter-spacing) is slightly increased for body text to improve scanning speed. Display sizes use negative tracking to maintain a tight, professional editorial look. Ensure a "Generous Tracking" philosophy is applied to labels to emphasize the premium nature of the interface.

## Layout & Spacing
The layout relies on a **12-column fluid grid** for desktop and a **4-column grid** for mobile. A strict 8px spacing rhythm (8, 16, 24, 32, 48) ensures mathematical harmony.

- **Margins:** 24px on mobile, 48px on desktop.
- **Chat Interface:** Centralized column layout (max-width 800px) to maintain focus and readability.
- **Safe Areas:** Generous internal padding (24px) within cards to prevent data from feeling cramped.

## Elevation & Depth
Depth is created through light and translucency rather than heavy shadows.

1.  **Glassmorphism:** The header and main input areas use a `backdrop-filter: blur(12px)` with a 70% opaque white background and a 1px border (#E2E8F0).
2.  **Ambient Shadows:** Primary cards use a very soft, diffused shadow: `0 4px 20px rgba(30, 41, 59, 0.05)`.
3.  **Chat Bubbles:** Assistant bubbles have a subtle 2px blur shadow to lift them from the background, while User bubbles remain flat to indicate they are "sent" and "grounded."

## Shapes
The shape language is predominantly rounded to reduce cognitive friction and appear approachable. 
- **Large Containers:** 24px (cards, main chat areas).
- **Interactive Elements:** 12px (buttons, inputs).
- **Pill Elements:** Full radius (chips, status indicators, user chat bubbles).
- **Selection States:** 8px (list item highlights).

## Components
- **Buttons:** Primary buttons are #00D09C with white text and 12px corners. Hover states should brighten the color by 5% and add a subtle transform (translateY -1px).
- **Chat Bubbles:** 
    - *User:* Light Blue/Gray tint (#F1F5F9), pill-shaped with 16px padding.
    - *Assistant:* White (#FFFFFF), 24px rounded corners (not pill-shaped), with a 1px border (#E2E8F0).
- **Suggestion Chips:** Pill-shaped, #FFFFFF background, #E2E8F0 border, #1E293B text. On hover, the border changes to #00D09C.
- **Input Fields:** Glassmorphic background with 12px rounded corners. Focused states feature a 2px outer glow of #00D09C at 20% opacity.
- **Disclaimer Banner:** Fixed to bottom, using #F8FAFC background, #64748B text, 12px font-size, and a top border of #E2E8F0.
- **Typing Indicator:** Three 6px dots in #00D09C with a staggered "breathing" opacity animation.
- **Checkboxes/Radios:** Rounded style with #00D09C fill upon selection.