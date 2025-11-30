# Phase 0: Research & Technology Decisions

**Feature**: UI Refactor - Persistent Navigation Layout  
**Date**: November 29, 2025

## Overview

This document captures technology choices, layout patterns, and best practices research for implementing the persistent three-region layout in the React frontend.

## Layout Pattern Research

### Decision: CSS Grid for Top-Level Layout

**Chosen Approach**: CSS Grid with named template areas

```css
.App {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main";
  grid-template-columns: minmax(180px, 20%) 1fr;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
}
```

**Rationale**:
- Native browser support (no framework dependencies)
- Clean semantic areas (header, sidebar, main)
- Responsive column sizing with minmax()
- Simpler than Flexbox for 2D layouts
- Maintains current simplicity (no CSS frameworks needed)

**Alternatives Considered**:
1. **Flexbox** - More verbose for 2D layouts, requires nested containers
2. **CSS Framework (Bootstrap/Tailwind)** - Violates "no new frameworks" assumption
3. **Absolute Positioning** - Brittle, poor responsive behavior

### Decision: Static Positioning for Title (No Sticky/Fixed)

**Chosen Approach**: Static position at document top (per clarification #3)

**Rationale**:
- Simpler implementation (no z-index management)
- Less intrusive user experience
- Avoids content jumping on scroll
- Matches desktop application patterns

## Component Architecture Research

### Decision: Controlled Component Pattern for Sidebar

**Chosen Approach**: Sidebar receives state and callbacks from App.tsx

```typescript
interface SidebarProps {
  onNavigationAction: (action: NavigationAction) => void;
  currentView: AppView;
}
```

**Rationale**:
- Single source of truth (App.tsx owns state)
- Easier testing (props in, callbacks out)
- Matches existing FileUpload pattern
- Follows React best practices

### Decision: Compound Component Pattern for NavigationItem

**Chosen Approach**: Self-contained expandable/collapsible component

```typescript
interface NavigationItemProps {
  label: string;
  children?: React.ReactNode;
  defaultExpanded?: boolean;
  onClick?: () => void;
}
```

**Rationale**:
- Reusable for future navigation items
- Encapsulates expand/collapse logic
- Clear separation of concerns
- Testable in isolation

## State Management Research

### Decision: Local React State (useState) - No Context API

**Chosen Approach**: Continue using useState in App.tsx for application state

**Rationale**:
- Current pattern already works well
- Only 2 components need state (App → Sidebar)
- Prop drilling is minimal (1 level deep)
- Context API adds unnecessary complexity for this scale

**Alternatives Considered**:
1. **Context API** - Overkill for single-level prop passing
2. **Redux/Zustand** - Violates "no new frameworks" principle

## Responsive Design Research

### Decision: Desktop-First with Min-Width Constraint

**Chosen Approach**: Sidebar min-width 180px, max-width 20% of viewport (per clarification #1)

**Rationale**:
- Prevents sidebar from being too narrow (readability)
- Prevents sidebar from consuming too much space (usability)
- Desktop-first per spec assumptions
- Mobile optimization out of scope

## Accessibility Research

### Decision: Maintain Existing ARIA Attributes

**Chosen Approach**: 
- Use semantic HTML (`<nav>`, `<header>`, `<main>`)
- Add `aria-label` to sidebar navigation
- Maintain existing `aria-live` on GameSummary
- Add `aria-expanded` to NavigationItem

**Rationale**:
- Semantic HTML provides baseline accessibility
- Screen reader navigation support
- Keyboard navigation works by default
- No need for advanced ARIA patterns (simple hierarchy)

## Animation/Transition Research

### Decision: CSS Transitions for Expand/Collapse Only

**Chosen Approach**: Simple max-height transition for NavigationItem

```css
.navigation-item-children {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.navigation-item-children.expanded {
  max-height: 500px;
}
```

**Rationale**:
- Smooth user feedback for expand/collapse
- Respects `prefers-reduced-motion` media query
- No animations for layout transitions (per spec)
- Minimal CSS, no JS animation libraries

## Testing Strategy Research

### Decision: React Testing Library with User Event

**Chosen Approach**: Continue using RTL for component testing

**Test Coverage Plan**:
1. **Unit Tests** (Sidebar, NavigationItem components)
   - Render tests
   - Click interaction tests
   - Expand/collapse state tests
   - Prop validation tests

2. **Integration Tests** (Full layout flow)
   - Initial render with 3 regions
   - Sidebar navigation triggers main area updates
   - FileUpload → Puzzle interface transition
   - End-game display in main area

3. **Visual Regression** (Manual - no new tools)
   - Screenshot comparison of layout states
   - Browser dev tools for layout verification

**Coverage Target**: Maintain >80% per constitution

## Performance Considerations

### Decision: No Performance Optimizations Needed

**Analysis**:
- Static layout (no dynamic calculations)
- Minimal re-renders (state changes at App level only)
- CSS Grid is performant (GPU-accelerated)
- No large lists or heavy computations

**Monitoring**: 
- Chrome DevTools Performance tab for initial render
- React DevTools Profiler for re-render checks
- Target: <2s initial render, <300ms transitions (per tech context)

## Browser Compatibility

### Decision: Modern Browsers Only (ES2020+)

**Supported Browsers**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**CSS Features Used**:
- CSS Grid (supported since 2017)
- CSS Custom Properties (supported)
- minmax() function (supported)
- Flexbox fallback (not needed)

**Rationale**: Per tech context, targeting modern browsers. No polyfills required.

## Summary of Key Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Layout Pattern** | CSS Grid with named areas | Semantic, responsive, no framework needed |
| **Title Positioning** | Static (not sticky/fixed) | Simpler, less intrusive per clarification |
| **Component Pattern** | Controlled components | Single source of truth, easier testing |
| **State Management** | Local React state (useState) | Sufficient for scale, matches existing pattern |
| **Sidebar Width** | min 180px, max 20% viewport | Readability + space efficiency per clarification |
| **Navigation Behavior** | Expandable/collapsible | Per clarification #4, default expanded |
| **Transitions** | CSS only (max-height) | Smooth UX, respects reduced-motion |
| **Testing** | RTL + User Event | Existing stack, >80% coverage |
| **Browser Support** | Modern browsers (ES2020+) | Per tech context specification |

## Open Questions / Risks

**None identified** - All clarifications resolved during spec phase. Implementation path is clear.
