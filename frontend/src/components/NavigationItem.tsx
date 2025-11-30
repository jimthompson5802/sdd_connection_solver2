import React from 'react';
import { NavigationItemProps, isExpandableItem, isActionItem } from '../types/navigation';
import './NavigationItem.css';

/**
 * NavigationItem component for hierarchical sidebar navigation.
 * 
 * Supports both expandable menu items (with children) and action items (clickable).
 * Provides proper ARIA attributes for accessibility and keyboard navigation support.
 * 
 * @param label - Display text for the navigation item
 * @param isExpanded - Whether expandable item's children are visible
 * @param onToggle - Callback for expandable items when toggled
 * @param onClick - Callback for action items when clicked
 * @param children - Child navigation items (for expandable items)
 * @param level - Hierarchy depth (0=top-level, 1=sub-item) for styling
 * @returns JSX element representing a navigation item
 */
const NavigationItem: React.FC<NavigationItemProps> = ({
  label,
  isExpanded,
  onToggle,
  onClick,
  children,
  level,
}) => {
  const expandable = isExpandableItem({ label, isExpanded, onToggle, onClick, children, level });
  const actionItem = isActionItem({ label, isExpanded, onToggle, onClick, children, level });

  const handleClick = () => {
    if (expandable && onToggle) {
      onToggle();
    } else if (actionItem && onClick) {
      onClick();
    }
  };

  const itemClass = [
    'navigation-item',
    `level-${level}`,
    expandable ? 'expandable' : '',
    actionItem ? 'action-item' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={itemClass}>
      <button
        type="button"
        className="navigation-item-button"
        onClick={handleClick}
        aria-expanded={expandable ? isExpanded : undefined}
      >
        <span className="navigation-item-label">{label}</span>
        {expandable && (
          <span className={`navigation-item-chevron ${isExpanded ? 'expanded' : ''}`}>
            ▶
          </span>
        )}
      </button>
      {expandable && children && isExpanded && (
        <div className="navigation-item-children expanded">
          {children}
        </div>
      )}
    </div>
  );
};

export default NavigationItem;