import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import NavigationItem from './NavigationItem';

describe('NavigationItem', () => {
  test('renders label text', () => {
    render(<NavigationItem label="Test Item" isExpanded={false} level={0} />);
    expect(screen.getByText('Test Item')).toBeInTheDocument();
  });

  test('shows chevron when expandable', () => {
    render(
      <NavigationItem label="Expandable" isExpanded={false} level={0}>
        <div>Child</div>
      </NavigationItem>
    );
    
    // Should have a chevron indicator for expandable items
    const item = screen.getByText('Expandable').closest('.navigation-item');
    expect(item).toHaveClass('expandable');
  });

  test('calls onToggle when expandable item is clicked', () => {
    const handleToggle = jest.fn();
    render(
      <NavigationItem 
        label="Expandable" 
        isExpanded={false} 
        level={0}
        onToggle={handleToggle}
      >
        <div>Child</div>
      </NavigationItem>
    );
    
    fireEvent.click(screen.getByText('Expandable'));
    expect(handleToggle).toHaveBeenCalledTimes(1);
  });

  test('calls onClick when action item is clicked', () => {
    const handleClick = jest.fn();
    render(
      <NavigationItem 
        label="Action Item" 
        isExpanded={false} 
        level={1}
        onClick={handleClick}
      />
    );
    
    fireEvent.click(screen.getByText('Action Item'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('shows children when expanded', () => {
    render(
      <NavigationItem label="Parent" isExpanded={true} level={0}>
        <NavigationItem label="Child" isExpanded={false} level={1} />
      </NavigationItem>
    );
    
    expect(screen.getByText('Child')).toBeVisible();
  });

  test('hides children when collapsed', () => {
    render(
      <NavigationItem label="Parent" isExpanded={false} level={0}>
        <div data-testid="child">Child</div>
      </NavigationItem>
    );
    
    expect(screen.queryByTestId('child')).not.toBeInTheDocument();
  });

  test('sets aria-expanded attribute for expandable items', () => {
    const { rerender } = render(
      <NavigationItem label="Expandable" isExpanded={false} level={0}>
        <div>Child</div>
      </NavigationItem>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-expanded', 'false');
    
    rerender(
      <NavigationItem label="Expandable" isExpanded={true} level={0}>
        <div>Child</div>
      </NavigationItem>
    );
    
    expect(button).toHaveAttribute('aria-expanded', 'true');
  });

  test('applies correct level styling', () => {
    const { rerender } = render(
      <NavigationItem label="Level 0" isExpanded={false} level={0} />
    );
    
    let item = screen.getByText('Level 0').closest('.navigation-item');
    expect(item).toHaveClass('level-0');
    
    rerender(<NavigationItem label="Level 1" isExpanded={false} level={1} />);
    
    item = screen.getByText('Level 1').closest('.navigation-item');
    expect(item).toHaveClass('level-1');
  });
});