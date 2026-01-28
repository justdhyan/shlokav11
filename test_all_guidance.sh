#!/bin/bash

# Test all guidance entries for all moods across all emotions

emotions=("fear" "anger" "grief" "confusion" "detachment" "joy" "doubt" "pride" "desire" "envy" "despair")

echo "======================================"
echo "Testing ALL Guidance Entries"
echo "======================================"
echo ""

missing_count=0
success_count=0
total_moods=0

for emotion in "${emotions[@]}"; do
    echo "Emotion: $emotion"
    echo "-------------------"
    
    # Get all moods for this emotion
    moods=$(curl -s http://localhost:8001/api/moods/$emotion | python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([m['_id'] for m in data]))")
    
    for mood_id in $moods; do
        total_moods=$((total_moods + 1))
        
        # Test if guidance exists
        result=$(curl -s http://localhost:8001/api/guidance/$mood_id)
        
        if echo "$result" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'title' in data else 1)" 2>/dev/null; then
            echo "  ✓ $mood_id"
            success_count=$((success_count + 1))
        else
            echo "  ✗ $mood_id - GUIDANCE NOT FOUND"
            missing_count=$((missing_count + 1))
        fi
    done
    
    echo ""
done

echo "======================================"
echo "Summary:"
echo "Total moods tested: $total_moods"
echo "✓ Working: $success_count"
echo "✗ Missing: $missing_count"
echo "======================================"

exit $missing_count
