import React, { useState } from 'react';
import { SidebarProps, NAVIGATION_MENUS, NAVIGATION_ACTIONS } from '../types/navigation';
import NavigationItem from './NavigationItem';
import './Sidebar.css';

/**
 * Sidebar navigation component for the persistent layout.
 * 
 * Provides a hierarchical navigation structure with expandable/collapsible menus.
 * Supports "Start New Game" → "From File" navigation pattern as specified in the UI refactor.
 * 
 * @param currentView - Current application view state (for potential conditional styling)
 * @param onNavigationAction - Callback function for navigation actions (from-file, toggle-menu)
 * @returns JSX element representing the sidebar navigation
 */
const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigationAction }) => {
  const [expandedMenus, setExpandedMenus] = useState<Set<string>>(
    new Set([NAVIGATION_MENUS.START_NEW_GAME])
  );

  const handleMenuToggle = (menuId: string) => {
    const newExpanded = new Set(expandedMenus);
    if (newExpanded.has(menuId)) {
      newExpanded.delete(menuId);
    } else {
      newExpanded.add(menuId);
    }
    setExpandedMenus(newExpanded);
    
    // Notify parent about menu toggle action
    onNavigationAction({ type: 'toggle-menu', menu: menuId });
  };

  const handleFromFileClick = () => {
    onNavigationAction({ type: 'from-file' });
  };

  const isStartNewGameExpanded = expandedMenus.has(NAVIGATION_MENUS.START_NEW_GAME);

  return (
    <nav className="sidebar" aria-label="Main Navigation">
      <NavigationItem
        label="Start New Game"
        isExpanded={isStartNewGameExpanded}
        onToggle={() => handleMenuToggle(NAVIGATION_MENUS.START_NEW_GAME)}
        level={0}
      >
        <NavigationItem
          label="From File"
          isExpanded={false}
          onClick={handleFromFileClick}
          level={1}
        />
      </NavigationItem>
    </nav>
  );
};

export default Sidebar;