# Quickstart: NYT Connections Puzzle Assistant

## User Journey Validation

### End-to-End Scenario: Complete Puzzle Success
**Objective**: Validate complete puzzle solving workflow from setup to success

**Prerequisites**: 
- Application running locally
- Sample CSV file with 16 words: `apple,orange,banana,grape,dog,cat,mouse,bird,red,blue,green,yellow,chair,table,sofa,desk`

**Steps**:
1. **Load Application**
   - Navigate to http://localhost:3000
   - Verify page title: "NYT Connection Solver Virtual Assistant"
   - Verify all UI elements are centered and visible

2. **Setup Puzzle**
   - Click file picker, select sample CSV file
   - Click gray "Setup Puzzle" button
   - **Verify**: 16 words appear in "Remaining Puzzle Words" area
   - **Verify**: All counters reset to zero
   - **Verify**: All buttons are enabled

3. **First Recommendation**
   - Click green "Next Recommendation" button
   - **Verify**: "Recommended Group" shows 4 words
   - **Verify**: "Group Connection" shows rationale
   - **Verify**: Response buttons are active

4. **Correct Response**
   - Click "Yellow" button (assuming first group is correct)
   - **Verify**: Yellow button becomes gray and disabled
   - **Verify**: "Remaining Puzzle Words" reduces to 12 words
   - **Verify**: "Count Correct Groups" increments to 1
   - **Verify**: Previous guess shows in green text

5. **Incorrect Response**
   - Click "Next Recommendation" for second group
   - Click "Incorrect" button (red)
   - **Verify**: "Count Mistakes" increments to 1
   - **Verify**: Previous guess shows in red text
   - **Verify**: Remaining words unchanged

6. **One-Away Response**
   - Click "Next Recommendation" for third group
   - Click "One-away" button (orange)
   - **Verify**: "Count Mistakes" increments to 2
   - **Verify**: Previous guess shows in orange text
   - **Verify**: Remaining words unchanged

7. **Continue to Success**
   - Get recommendations and mark correct until "Count Correct Groups" reaches 4
   - **Verify**: Success popup appears: "Successfully solved the Puzzle"
   - **Verify**: Game state properly maintained

### Error Handling Validation

**Test Invalid File Upload**:
1. Upload empty file or non-CSV format
2. Click "Setup Puzzle"
3. **Verify**: Error message displayed, setup prevented

**Test Insufficient Words**:
1. Complete puzzle until <4 words remain
2. Click "Next Recommendation"
3. **Verify**: Error message "Not enough words remaining"

**Test No Active Recommendation**:
1. Before getting any recommendation, click "Yellow" button
2. **Verify**: Error message "No recommendation to respond to"

**Test Maximum Mistakes**:
1. Make 4 incorrect/one-away responses
2. **Verify**: Failure popup "Unable to Solve puzzle"
3. **Verify**: All buttons disabled except "Setup Puzzle"

### UI Component Validation

**Layout Verification**:
- All elements centered on page
- File picker with placeholder "Puzzle File"
- Gray "Setup Puzzle" button
- 3-line "Remaining Puzzle Words" text area
- Green "Next Recommendation" button
- "Recommended Group" and "Group Connection" displays
- Color buttons match their text colors
- Red "Incorrect" and orange "One-away" buttons
- Multi-line "Previous Guess" display

**State Management Verification**:
- Puzzle state persists between recommendations
- Button states (enabled/disabled/color changes) work correctly
- Counter updates reflect actual game state
- Previous guesses accumulate with proper color coding

### Performance Validation

**Response Time** (No specific requirements per clarifications):
- Setup puzzle response should be reasonable
- Recommendation generation should be reasonable
- UI updates should be immediate

### Browser Compatibility

**Target Environment**: macOS desktop browsers
- Test in Safari (primary)
- Test in Chrome (secondary)
- Verify file upload works in both browsers
- Verify UI renders correctly

### Recovery Scenarios

**Page Refresh**:
1. Start puzzle, make some progress
2. Refresh browser page
3. **Verify**: Clean state (puzzle resets)
4. **Verify**: Can start new puzzle

**File Re-upload**:
1. Complete a puzzle
2. Upload new CSV file and click "Setup Puzzle"
3. **Verify**: Previous state cleared
4. **Verify**: New puzzle initialized correctly

### Success Criteria
- [ ] Complete puzzle workflow functions end-to-end
- [ ] All error conditions handled gracefully
- [ ] UI state management works correctly
- [ ] Game rules enforced (4 groups max, 4 mistakes max)
- [ ] File upload and parsing works reliably
- [ ] No JavaScript errors in browser console
- [ ] Application works offline (local-only)

### Manual Testing Checklist
- [ ] Upload various CSV formats (test edge cases)
- [ ] Try different word combinations
- [ ] Test rapid clicking of buttons
- [ ] Verify color coding accuracy
- [ ] Test browser back/forward buttons
- [ ] Verify .env configuration loading