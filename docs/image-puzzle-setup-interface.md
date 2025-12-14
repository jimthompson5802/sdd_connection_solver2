# Image-Based Puzzle Setup Interface Documentation

**Feature**: 004-image-puzzle-setup | **Date**: December 13, 2025

## Interface Overview

The image-based puzzle setup feature provides a streamlined interface for users to extract words from puzzle screenshots using AI vision models. This document describes the interface layout and user interactions.

## Interface Layout

### Navigation Access
- **Location**: Left sidebar
- **Menu Item**: "From Image" (located below "From File")
- **Action**: Clicking navigates to the image setup interface

### Main Interface Components

The image setup interface follows a vertical layout with these key sections:

```
┌─────────────────────────────────────────────┐
│                Header                        │
├─────────────────┬───────────────────────────┤
│    Sidebar      │      Main Content         │
│                 │                          │
│  ○ Start New    │  ┌─ Image Paste Area ─┐  │
│    Game         │  │                     │  │
│  ├─ From File   │  │   [Paste Area]      │  │
│  └─ From Image  │  │                     │  │
│                 │  └─────────────────────┘  │
│                 │                          │
│                 │  ┌─ Provider Setup ────┐  │
│                 │  │ Provider: [dropdown]│  │
│                 │  │ Model: [dropdown]   │  │
│                 │  └─────────────────────┘  │
│                 │                          │
│                 │  [Setup Puzzle Button]   │
└─────────────────┴───────────────────────────┘
```

### 1. Image Paste Area

**Initial State (No Image)**:
- Displays placeholder with upload icon
- Text: "Paste image here"  
- Keyboard hint: "Press Ctrl+V (or Cmd+V on Mac)"
- Visual affordance: Dashed border, hover state

**After Image Paste**:
- Shows image preview with proper aspect ratio
- Maintains image quality and sizing
- Allows paste of new image to replace current one

**Error States**:
- Invalid format: "Please paste a valid image (PNG, JPEG, JPG, GIF)"
- Oversized file: "Image too large (max 5MB)"

### 2. Provider Configuration

**Provider Dropdown**:
- Lists available LLM providers (OpenAI, Ollama, Simple)
- Shows default provider as pre-selected
- Consistent styling with existing puzzle interface

**Model Dropdown**:
- Dynamically populated based on selected provider
- Vision-capable models only:
  - OpenAI: GPT-4 Vision Preview, GPT-4 Turbo, GPT-4o
  - Ollama: llava variants (llava:latest, llava:13b, etc.)
  - Simple: Simple Model (for testing)
- Shows default model as pre-selected

### 3. Action Button

**Setup Puzzle Button**:
- Disabled when no image is pasted
- Enabled when valid image is present
- Shows loading state during LLM processing
- Text changes: "Setup Puzzle" → "Processing..." → "Setup Puzzle"

### 4. Error Handling

**Error Display**:
- Shows below action button when errors occur
- Preserves image and selection state for retry
- Clear, actionable error messages:
  - "LLM unable to extract puzzle words"
  - Network/provider specific errors
  - Validation errors

## User Interaction Flow

### Happy Path
1. User clicks "From Image" in sidebar
2. Interface loads with placeholder paste area
3. User pastes image (Ctrl+V / Cmd+V)
4. Image preview displays immediately (<2s)
5. Provider/model dropdowns show defaults
6. User clicks "Setup Puzzle"
7. Loading state shown during processing
8. Success: Transitions to active puzzle interface
9. Words extracted and puzzle begins

### Error Recovery
1. User encounters error (e.g., extraction failure)
2. Error message displays clearly
3. Image and selections preserved
4. User can modify provider/model and retry
5. Or user can paste different image and retry

## Accessibility Features

- Keyboard navigation support (Tab, Enter, Space)
- Screen reader compatible (aria-labels, semantic HTML)
- Focus indicators on all interactive elements
- Reduced motion support in CSS animations
- High contrast mode compatibility

## Performance Characteristics

- **Image paste response**: <2 seconds
- **Image preview generation**: Immediate (browser-native)
- **LLM extraction**: <10 seconds typical
- **Error display**: <3 seconds
- **Interface transitions**: <300ms

## Browser Compatibility

- **Chrome 66+**: Full support (recommended)
- **Firefox 63+**: Full support
- **Safari 13.1+**: Full support
- **Edge 79+**: Full support

*Note*: Clipboard API required for paste functionality. Older browsers may require user to manually upload files.

## Screenshot Placeholders

*Note: This section would contain actual screenshots in a production deployment*

### Interface Screenshots Needed:

1. **Initial State**: `initial-image-setup.png`
   - Shows empty paste area with placeholder text
   - Provider dropdowns with defaults
   - Disabled "Setup Puzzle" button

2. **Image Pasted**: `image-pasted-preview.png`
   - Shows clear image preview of 4x4 word grid
   - Enabled "Setup Puzzle" button
   - Provider/model selections visible

3. **Processing State**: `processing-extraction.png`
   - Loading indicator active
   - Button shows "Processing..." text
   - Image and dropdowns remain visible

4. **Error State**: `error-handling.png`
   - Clear error message displayed
   - Image and selections preserved
   - Retry capability evident

5. **Success Transition**: `extraction-success.png`
   - Moment before transition to puzzle interface
   - Shows successful completion state

### Integration Screenshots:

6. **Sidebar Navigation**: `sidebar-from-image.png`
   - Shows "From Image" menu item location
   - Highlights navigation pattern

7. **Full Interface**: `complete-interface.png`
   - Shows entire application layout
   - Image setup in main area context
   - Sidebar and header integration

## Visual Design Notes

- **Color scheme**: Matches existing puzzle interface
- **Typography**: Consistent with application fonts
- **Spacing**: 16px grid system maintained
- **Borders**: Subtle borders for visual hierarchy
- **Hover states**: Clear interactive feedback
- **Loading states**: Subtle animation without distraction

## Future Enhancements

- Drag-and-drop image support
- Multiple image format support (.webp, .bmp)
- Image editing tools (crop, rotate, enhance)
- Batch processing for multiple puzzles
- Offline capability for supported models

---

**Screenshots Location**: Screenshots should be placed in `/docs/screenshots/image-setup/` when available.

**Last Updated**: December 13, 2025
**Status**: Interface implemented, screenshots pending