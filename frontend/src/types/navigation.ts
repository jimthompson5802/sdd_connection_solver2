/**
 * Navigation types for UI Refactor - Persistent Navigation Layout
 * 
 * These TypeScript types define the navigation state and actions for the
 * new three-region layout with persistent sidebar navigation.
 */

/**
 * Application view states for routing main area content
 */
export type AppView = 
  | 'initial'          // First load, no action taken - shows welcome message
  | 'file-upload'      // File upload interface showing in main area
  | 'image-setup'      // Image upload/paste interface showing in main area
  | 'puzzle-active'    // Game in progress - EnhancedPuzzleInterface showing
  | 'puzzle-complete'; // Game finished (won/lost) - EnhancedPuzzleInterface with GameSummary

/**
 * Navigation actions that can be triggered from the sidebar
 */
export type NavigationAction = 
  | { type: 'from-file' }                    // User clicked "From File" menu item
  | { type: 'from-image' }                   // User clicked "From Image" menu item
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