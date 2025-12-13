# Image Setup Screenshots

This directory contains screenshots of the image-based puzzle setup interface.

## Required Screenshots

The following screenshots should be captured during manual testing:

### Core Interface States
- `initial-image-setup.png` - Empty paste area with placeholder
- `image-pasted-preview.png` - Image preview after pasting 4x4 grid
- `processing-extraction.png` - Loading state during LLM processing
- `error-handling.png` - Error message display with retry capability
- `extraction-success.png` - Success state before puzzle transition

### Navigation Integration  
- `sidebar-from-image.png` - Sidebar showing "From Image" menu item
- `complete-interface.png` - Full application layout with image setup

## Screenshot Guidelines

### Image Requirements
- **Format**: PNG (preferred) or JPG
- **Resolution**: 1920x1080 or higher
- **Browser**: Chrome (latest) for consistency
- **Window Size**: Full browser window or consistent crop

### Content Requirements
- Use realistic puzzle data (avoid copyrighted NYT content)
- Show clear 4x4 word grids in paste area
- Include provider/model dropdown states
- Demonstrate both success and error scenarios

### Naming Convention
- Use descriptive kebab-case filenames
- Include viewport size if multiple versions: `initial-setup-desktop.png`
- Add date suffix for updates: `error-handling-2025-12-13.png`

## How to Capture Screenshots

1. Start the application in development mode
2. Navigate to "From Image" interface
3. Use sample 4x4 word grid images for testing
4. Capture each state systematically
5. Verify screenshots show interface clearly
6. Add to this directory with descriptive names

## Sample Test Images

For capturing screenshots, use these sample word grids:

```
ANIMAL  BIRD    FISH    WHALE
PYTHON  JAVA    SWIFT   RUBY  
APPLE   GOOGLE  META    TESLA
HOUSE   CABIN   VILLA   LODGE
```

## Browser Testing

Capture screenshots in multiple browsers for compatibility documentation:
- Chrome (primary)
- Firefox 
- Safari (macOS)
- Edge

---

**Note**: Screenshots will be added during manual testing phase.
**Status**: Directory prepared, awaiting screenshot capture