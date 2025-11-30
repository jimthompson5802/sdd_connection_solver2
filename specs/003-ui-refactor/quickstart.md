# Quickstart Guide: UI Refactor Implementation

**Feature**: UI Refactor - Persistent Navigation Layout  
**Branch**: `003-ui-refactor`  
**Last Updated**: November 29, 2025

## Prerequisites

- Node.js 18+ installed
- Repository cloned and on branch `003-ui-refactor`
- Familiar with React, TypeScript, CSS Grid
- Have read [spec.md](./spec.md) and [data-model.md](./data-model.md)

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Verify Current Tests Pass

Before making any changes, ensure all existing tests pass:

```bash
npm test
```

Expected: All tests should pass. If not, fix existing issues first.

### 3. Start Development Server

```bash
npm start
```

Application should open at `http://localhost:3000`

## Development Workflow (TDD)

This feature follows **Test-First Development** per the constitution. For each component:

### Step 1: Write Tests First

```bash
# Create test file
touch src/components/Sidebar.test.tsx

# Write failing tests (see Test Examples below)
# Run tests - they should FAIL
npm test -- Sidebar.test.tsx
```

### Step 2: Implement Component

```bash
# Create component file
touch src/components/Sidebar.tsx
touch src/components/Sidebar.css

# Implement minimum code to make tests pass
# Run tests - they should PASS
npm test -- Sidebar.test.tsx
```

### Step 3: Refactor

- Clean up code
- Add comments
- Ensure type safety
- Run tests again - should still PASS

## Implementation Order

Follow this sequence to build incrementally:

### Phase A: Create New Components (TDD)

1. **NavigationItem Component** (foundation)
   - Write tests: `NavigationItem.test.tsx`
   - Implement: `NavigationItem.tsx`, `NavigationItem.css`
   - Verify: Tests pass, storybook review (optional)

2. **Sidebar Component** (uses NavigationItem)
   - Write tests: `Sidebar.test.tsx`
   - Implement: `Sidebar.tsx`, `Sidebar.css`
   - Verify: Tests pass, renders navigation hierarchy

### Phase B: Modify Existing Components

3. **Update App.tsx Layout** (grid structure)
   - Write layout tests in `App.test.tsx`
   - Update `App.tsx` to use CSS Grid
   - Update `App.css` with grid template areas
   - Verify: Tests pass, visual inspection

4. **Modify FileUpload Component** (remove header)
   - Update tests in `FileUpload.test.tsx`
   - Remove "Upload New Puzzle" button logic
   - Adjust styles in `FileUpload.css`
   - Verify: Tests pass, upload still works

### Phase C: Integration Testing

5. **Full Layout Integration Test**
   - Write integration test: `test_layout_navigation.test.tsx`
   - Test full user flow: initial → file upload → puzzle
   - Verify: All acceptance scenarios pass

6. **Visual Regression Check**
   - Manual testing of all states
   - Check responsive behavior
   - Verify no layout shift/reflow

## Test Examples

### Example 1: NavigationItem Component Test

```typescript
// src/components/NavigationItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import NavigationItem from './NavigationItem';

describe('NavigationItem', () => {
  test('renders label text', () => {
    render(<NavigationItem label="Test Item" isExpanded={false} level={0} />);
    expect(screen.getByText('Test Item')).toBeInTheDocument();
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
    
    expect(screen.queryByTestId('child')).not.toBeVisible();
  });
});
```

### Example 2: Sidebar Component Test

```typescript
// src/components/Sidebar.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Sidebar from './Sidebar';

describe('Sidebar', () => {
  test('renders "Start New Game" menu', () => {
    const handleAction = jest.fn();
    render(<Sidebar currentView="initial" onNavigationAction={handleAction} />);
    
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
  });

  test('"Start New Game" is expanded by default', () => {
    const handleAction = jest.fn();
    render(<Sidebar currentView="initial" onNavigationAction={handleAction} />);
    
    expect(screen.getByText('From File')).toBeVisible();
  });

  test('clicking "From File" triggers navigation action', () => {
    const handleAction = jest.fn();
    render(<Sidebar currentView="initial" onNavigationAction={handleAction} />);
    
    fireEvent.click(screen.getByText('From File'));
    expect(handleAction).toHaveBeenCalledWith({ type: 'from-file' });
  });
});
```

### Example 3: App Layout Integration Test

```typescript
// src/tests/integration/test_layout_navigation.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../../App';

describe('Layout Navigation Integration', () => {
  test('complete user flow: initial → file upload → puzzle', async () => {
    render(<App />);
    
    // Initial state
    expect(screen.getByText('NYT Connections Puzzle Assistant')).toBeInTheDocument();
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
    
    // Click "From File"
    fireEvent.click(screen.getByText('From File'));
    
    // File upload interface appears
    expect(screen.getByText(/choose a csv file/i)).toBeInTheDocument();
    
    // Upload file (mock)
    const file = new File(['word1,word2,word3,word4'], 'puzzle.csv', { type: 'text/csv' });
    const input = screen.getByLabelText(/choose a csv file/i);
    fireEvent.change(input, { target: { files: [file] } });
    
    // Puzzle interface appears
    await waitFor(() => {
      expect(screen.getByText(/words remaining/i)).toBeInTheDocument();
    });
    
    // Sidebar and title still visible
    expect(screen.getByText('NYT Connections Puzzle Assistant')).toBeInTheDocument();
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
  });
});
```

## Running Tests

### Run All Tests
```bash
npm test
```

### Run Specific Test File
```bash
npm test -- Sidebar.test.tsx
```

### Run Tests in Watch Mode
```bash
npm test -- --watch
```

### Check Code Coverage
```bash
npm test -- --coverage
```

Target: >80% coverage on new components

## Visual Testing Checklist

After implementation, manually verify:

- [ ] Title "NYT Connections Puzzle Assistant" visible at top
- [ ] Sidebar visible on left with "Start New Game" expanded
- [ ] "From File" sub-item visible and clickable
- [ ] Main area shows "Select action in Left Side Bar" initially
- [ ] Clicking "From File" shows file upload interface
- [ ] Uploading file shows puzzle interface
- [ ] Sidebar does not overlap main content
- [ ] Layout is stable (no jumping/shifting)
- [ ] End-game message and GameSummary appear in same positions
- [ ] Sidebar width between 180px and 20% of viewport

## Debugging Tips

### Layout Issues

```bash
# Use Chrome DevTools
# Right-click → Inspect
# Select "App" div
# In Computed tab, verify:
#   - display: grid
#   - grid-template-areas: "header header" "sidebar main"
#   - grid-template-columns: minmax(180px, 20%) 1fr
```

### Component Not Rendering

```bash
# Check React DevTools
# Components tab → find your component
# Verify props are correct
# Check if component is in DOM but hidden (CSS issue)
```

### Tests Failing

```bash
# Run with verbose output
npm test -- --verbose

# Run single test
npm test -- --testNamePattern="renders label text"

# Check test snapshots
npm test -- -u  # Update snapshots if intentional changes
```

## File Checklist

Before submitting PR, ensure all files are created/modified:

### New Files Created
- [ ] `src/components/Sidebar.tsx`
- [ ] `src/components/Sidebar.css`
- [ ] `src/components/Sidebar.test.tsx`
- [ ] `src/components/NavigationItem.tsx`
- [ ] `src/components/NavigationItem.css`
- [ ] `src/components/NavigationItem.test.tsx`
- [ ] `src/types/navigation.ts`
- [ ] `tests/integration/test_layout_navigation.test.tsx`

### Files Modified
- [ ] `src/App.tsx` (grid layout, view routing)
- [ ] `src/App.css` (grid template, title styling)
- [ ] `src/App.test.tsx` (updated layout tests)
- [ ] `src/components/FileUpload.tsx` (removed button)
- [ ] `src/components/FileUpload.css` (updated styles)

### Files Untouched (verify no changes)
- [ ] `src/components/EnhancedPuzzleInterface.tsx`
- [ ] `src/components/GameSummary.tsx`
- [ ] `backend/**/*` (entire backend directory)

## Performance Verification

```bash
# Run production build
npm run build

# Serve production build
npx serve -s build

# Open Chrome DevTools
# Performance tab → Record → Reload
# Verify:
#   - Initial render < 2s
#   - Layout transitions < 300ms
#   - No layout shift/reflow warnings
```

## Common Pitfalls

1. **Grid not working**: Ensure parent has `display: grid` and child elements have `grid-area` set
2. **Sidebar too narrow**: Check `minmax(180px, 20%)` is applied to grid-template-columns
3. **State not updating**: Verify callbacks are passed correctly and setState is called
4. **Tests failing**: Check that async operations use `waitFor()` and `await`
5. **TypeScript errors**: Ensure all props match interface definitions in `contracts/components.ts`

## Next Steps

After completing this implementation:

1. Run full test suite: `npm test`
2. Check coverage: `npm test -- --coverage`
3. Manual visual testing (see checklist above)
4. Create PR with reference to spec and plan docs
5. Request code review

## Questions / Issues

If you encounter problems:

1. Review [spec.md](./spec.md) for requirements
2. Review [data-model.md](./data-model.md) for component contracts
3. Check [research.md](./research.md) for technology decisions
4. Consult existing similar components (e.g., FileUpload pattern)

## Resources

- [React Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro/)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [TypeScript React Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Constitution](/.specify/memory/constitution.md) - Project principles
