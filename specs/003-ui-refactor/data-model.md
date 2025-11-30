# Phase 1: Data Model & Component Contracts

**Feature**: UI Refactor - Persistent Navigation Layout  
**Date**: November 29, 2025

## Component Data Model

### 1. Application State (App.tsx)

**Current State** (preserved):
```typescript
interface PuzzleState {
  words: string[];
  currentRecommendation: string[];
  recommendationConnection: string;
  correctCount: number;
  mistakeCount: number;
  gameStatus: 'waiting' | 'active' | 'won' | 'lost';
  isLoading: boolean;
  error: string | null;
  previousResponses: PreviousResponse[];
}
```

**New State** (additions):
```typescript
// Navigation state
type AppView = 'initial' | 'file-upload' | 'puzzle-active' | 'puzzle-complete';

interface AppLayoutState {
  currentView: AppView;
  sidebarExpanded: boolean;  // Track "Start New Game" expansion state
}
```

**State Transitions**:
```
initial → file-upload (user clicks "From File")
file-upload → puzzle-active (file uploaded successfully)
puzzle-active → puzzle-complete (game won or lost)
puzzle-complete → file-upload (user clicks "From File" again)
```

### 2. Sidebar Component

**Props Interface**:
```typescript
interface SidebarProps {
  currentView: AppView;
  onNavigationAction: (action: NavigationAction) => void;
}

type NavigationAction = 
  | { type: 'from-file' }
  | { type: 'toggle-menu'; menu: string };
```

**Internal State**:
```typescript
interface SidebarState {
  expandedMenus: Set<string>;  // Track which menus are expanded
}
```

**Behavior**:
- Renders navigation hierarchy ("Start New Game" → "From File")
- "Start New Game" defaults to expanded (per clarification #5)
- Clicking "From File" triggers `onNavigationAction({ type: 'from-file' })`
- Clicking "Start New Game" toggles expansion of sub-items

### 3. NavigationItem Component

**Props Interface**:
```typescript
interface NavigationItemProps {
  label: string;
  isExpanded: boolean;
  onToggle?: () => void;
  children?: React.ReactNode;
  level: number;  // 0 = top-level, 1 = sub-item
}
```

**Behavior**:
- Top-level items (level=0) are expandable/collapsible if they have children
- Sub-items (level=1) are clickable actions
- Visual indicator (chevron) shows expansion state
- Respects `aria-expanded` for accessibility

### 4. Modified FileUpload Component

**No Props Changes** - continues to receive:
```typescript
interface FileUploadProps {
  onFileUpload: (content: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}
```

**Behavior Changes**:
- Remove internal "Upload New Puzzle" button (moved to Sidebar)
- Remove header/title rendering (moved to App title bar)
- Focus solely on file selection and upload logic

### 5. EnhancedPuzzleInterface Component

**No Changes** - continues to receive all existing props:
```typescript
interface EnhancedPuzzleInterfaceProps {
  words: string[];
  recommendation: string[];
  recommendationConnection: string;
  correctCount: number;
  mistakeCount: number;
  gameStatus: 'waiting' | 'active' | 'won' | 'lost';
  isLoading: boolean;
  error: string | null;
  onRecordResponse: (type, color?, attemptWords?) => Promise<void>;
  previousResponses: PreviousResponse[];
  llmProvider: LLMProvider | null;
  onProviderChange: (provider: LLMProvider) => void;
  showProviderControls: boolean;
  puzzleContext: string;
  previousGuesses: string[][];
}
```

**Behavior**: Completely unchanged - reused as-is in main area

## Layout Data Model

### Grid Template Areas

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

.App-header {
  grid-area: header;
}

.App-sidebar {
  grid-area: sidebar;
}

.App-main {
  grid-area: main;
}
```

### Main Area Content Mapping

| AppView | Content Component | Props Source |
|---------|-------------------|--------------|
| `initial` | WelcomeMessage (inline) | Static text: "Select action in Left Side Bar" |
| `file-upload` | FileUpload | `handleFileUpload`, `puzzleState.isLoading`, `puzzleState.error` |
| `puzzle-active` | EnhancedPuzzleInterface | All current puzzle state + callbacks |
| `puzzle-complete` | EnhancedPuzzleInterface | Same as puzzle-active (component handles both) |

## Type Definitions

### New Types File: `frontend/src/types/navigation.ts`

```typescript
/**
 * Application view states for layout routing
 */
export type AppView = 
  | 'initial'          // First load, no action taken
  | 'file-upload'      // File upload interface showing
  | 'puzzle-active'    // Game in progress
  | 'puzzle-complete'; // Game finished (won/lost)

/**
 * Navigation actions triggered by sidebar
 */
export type NavigationAction = 
  | { type: 'from-file' }
  | { type: 'toggle-menu'; menu: string };

/**
 * Sidebar navigation state
 */
export interface SidebarState {
  expandedMenus: Set<string>;
}

/**
 * Props for Sidebar component
 */
export interface SidebarProps {
  currentView: AppView;
  onNavigationAction: (action: NavigationAction) => void;
}

/**
 * Props for NavigationItem component
 */
export interface NavigationItemProps {
  label: string;
  isExpanded: boolean;
  onToggle?: () => void;
  onClick?: () => void;
  children?: React.ReactNode;
  level: number;
}
```

## Component Hierarchy

```
App (grid container)
├── header (grid area: header)
│   └── h1: "NYT Connections Puzzle Assistant"
├── Sidebar (grid area: sidebar)
│   └── NavigationItem (label="Start New Game", isExpanded=true)
│       └── NavigationItem (label="From File", level=1, onClick=fromFileHandler)
└── main (grid area: main)
    └── [Dynamic based on currentView]
        ├── WelcomeMessage (currentView='initial')
        ├── FileUpload (currentView='file-upload')
        └── EnhancedPuzzleInterface (currentView='puzzle-active' or 'puzzle-complete')
```

## State Flow Diagram

```
User Actions → Sidebar → App.tsx → Main Area Update

1. Initial Load:
   currentView = 'initial'
   → Main shows "Select action in Left Side Bar"

2. Click "From File":
   onNavigationAction({ type: 'from-file' })
   → App sets currentView = 'file-upload'
   → Main shows FileUpload component

3. Upload CSV:
   handleFileUpload(content)
   → apiService.setupPuzzle(content)
   → App sets currentView = 'puzzle-active'
   → Main shows EnhancedPuzzleInterface

4. Game Ends:
   puzzleState.gameStatus = 'won' | 'lost'
   → currentView remains 'puzzle-active' (component handles display)
   → GameSummary shown in same position

5. New Game:
   Click "From File" again
   → App sets currentView = 'file-upload'
   → Cycle repeats
```

## Validation Rules

### Sidebar
- Must always render "Start New Game" item
- "Start New Game" must default to expanded=true
- Must call onNavigationAction for "From File" clicks
- Must not modify application state directly

### NavigationItem
- Level 0 items with children must be expandable
- Level 1 items must be clickable (not expandable)
- Must maintain aria-expanded attribute when expandable
- Must show visual indicator (chevron) for expandable items

### App Layout
- Title must always be visible in header area
- Sidebar must always be visible (min-width enforced)
- Main area must display exactly one component at a time
- No content overlapping between grid areas

## CSS Custom Properties

```css
:root {
  --sidebar-min-width: 180px;
  --sidebar-max-width: 20%;
  --header-bg-color: #2c3e50;
  --header-text-color: white;
  --sidebar-bg-color: #ecf0f1;
  --transition-duration: 0.3s;
}
```

## Summary

**Core Entities**:
1. AppView - routing state for main area content
2. NavigationAction - user commands from sidebar
3. SidebarProps - sidebar component contract
4. NavigationItemProps - navigation item contract

**State Ownership**:
- App.tsx owns currentView and puzzleState
- Sidebar owns internal expandedMenus tracking
- All child components receive props (no Context API)

**Data Flow**:
- Unidirectional: User → Sidebar → App → Main Area
- Callbacks for actions: onNavigationAction, onFileUpload, onRecordResponse
- No direct state mutation - all via setState calls in App.tsx
