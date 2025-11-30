/**
 * Component Contracts for UI Refactor - Persistent Navigation Layout
 * 
 * These TypeScript interfaces define the contracts for all components
 * involved in the layout refactor. Use these as the source of truth
 * for component props and state shapes.
 */

/**
 * Application view states for routing main area content
 */
export type AppView = 
  | 'initial'          // First load, no action taken - shows welcome message
  | 'file-upload'      // File upload interface showing in main area
  | 'puzzle-active'    // Game in progress - EnhancedPuzzleInterface showing
  | 'puzzle-complete'; // Game finished (won/lost) - EnhancedPuzzleInterface with GameSummary

/**
 * Navigation actions that can be triggered from the sidebar
 */
export type NavigationAction = 
  | { type: 'from-file' }                    // User clicked "From File" menu item
  | { type: 'toggle-menu'; menu: string };   // User clicked expandable menu header

/**
 * Props for the Sidebar component
 * 
 * @property currentView - Current application view state (for conditional styling)
 * @property onNavigationAction - Callback when user performs navigation action
 */
export interface SidebarProps {
  currentView: AppView;
  onNavigationAction: (action: NavigationAction) => void;
}

/**
 * Props for the NavigationItem component
 * 
 * @property label - Display text for the navigation item
 * @property isExpanded - Whether the item's children are visible (for expandable items)
 * @property onToggle - Callback when user clicks to expand/collapse (optional, for expandable items)
 * @property onClick - Callback when user clicks the item itself (optional, for action items)
 * @property children - Child navigation items (optional, for expandable items)
 * @property level - Hierarchy depth (0=top, 1=sub-item) for styling
 */
export interface NavigationItemProps {
  label: string;
  isExpanded: boolean;
  onToggle?: () => void;
  onClick?: () => void;
  children?: React.ReactNode;
  level: number;
}

/**
 * Internal state for Sidebar component
 * 
 * @property expandedMenus - Set of menu identifiers that are currently expanded
 */
export interface SidebarState {
  expandedMenus: Set<string>;
}

/**
 * Layout state managed by App.tsx
 * 
 * @property currentView - Current view being displayed in main area
 */
export interface AppLayoutState {
  currentView: AppView;
}

// ============================================================================
// EXISTING INTERFACES (preserved for reference - no changes)
// ============================================================================

/**
 * Props for FileUpload component (UNCHANGED)
 * 
 * @property onFileUpload - Callback when file is selected and read
 * @property isLoading - Whether upload is in progress
 * @property error - Error message to display, or null
 */
export interface FileUploadProps {
  onFileUpload: (content: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

/**
 * Puzzle state managed by App.tsx (UNCHANGED)
 * 
 * Note: This interface remains unchanged but is referenced here for completeness
 */
export interface PuzzleState {
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

/**
 * Previous response record (UNCHANGED)
 */
export interface PreviousResponse {
  type: 'correct' | 'incorrect' | 'one-away';
  color?: string;
  words: string[];
  timestamp: Date;
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard to check if a NavigationItem is expandable
 */
export function isExpandableItem(props: NavigationItemProps): boolean {
  return props.children !== undefined && props.children !== null;
}

/**
 * Type guard to check if a NavigationItem is an action item
 */
export function isActionItem(props: NavigationItemProps): boolean {
  return props.onClick !== undefined;
}

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Navigation menu identifiers
 */
export const NAVIGATION_MENUS = {
  START_NEW_GAME: 'start-new-game',
} as const;

/**
 * Navigation action items
 */
export const NAVIGATION_ACTIONS = {
  FROM_FILE: 'from-file',
} as const;
