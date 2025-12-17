# File: algorithms/segmentation.py
from copy import deepcopy
import sys

def segmentation_allocator(requests, total_memory_size, strategy="First Fit"):
    """
    Simulates Segmentation using First, Best, or Worst Fit.
    
    Args:
        requests: List of strings (e.g., "1:100", "-1").
        total_memory_size: Total RAM size.
        strategy: "First Fit", "Best Fit", or "Worst Fit".
    """
    # Memory initialized as one large free block
    memory = [{'id': 'Free', 'start': 0, 'size': total_memory_size}]
    steps = []
    
    for req in requests:
        current_op = ""
        success = False
        
        # --- DEALLOCATION ---
        if req.startswith("-"):
            pid = req[1:]
            current_op = f"Dealloc {pid}"
            
            found = False
            for seg in memory:
                if seg['id'] == pid:
                    seg['id'] = 'Free'
                    found = True
            
            if found:
                success = True
                # Coalesce (Merge adjacent free blocks)
                new_memory = []
                if memory:
                    curr = memory[0]
                    for next_seg in memory[1:]:
                        if curr['id'] == 'Free' and next_seg['id'] == 'Free':
                            curr['size'] += next_seg['size']
                        else:
                            new_memory.append(curr)
                            curr = next_seg
                    new_memory.append(curr)
                memory = new_memory
        
        # --- ALLOCATION ---
        else:
            try:
                pid, size_str = req.split(":")
                size = int(size_str)
                current_op = f"Alloc {pid} ({size}KB)"
                
                # Find candidate segment based on strategy
                candidate_idx = -1
                
                if strategy == "First Fit":
                    for i, seg in enumerate(memory):
                        if seg['id'] == 'Free' and seg['size'] >= size:
                            candidate_idx = i
                            break
                            
                elif strategy == "Best Fit":
                    min_waste = sys.maxsize
                    for i, seg in enumerate(memory):
                        if seg['id'] == 'Free' and seg['size'] >= size:
                            waste = seg['size'] - size
                            if waste < min_waste:
                                min_waste = waste
                                candidate_idx = i
                                
                elif strategy == "Worst Fit":
                    max_waste = -1
                    for i, seg in enumerate(memory):
                        if seg['id'] == 'Free' and seg['size'] >= size:
                            waste = seg['size'] - size
                            if waste > max_waste:
                                max_waste = waste
                                candidate_idx = i

                # Apply Allocation if candidate found
                if candidate_idx != -1:
                    seg = memory[candidate_idx]
                    new_start = seg['start']
                    remaining_size = seg['size'] - size
                    
                    alloc_seg = {'id': pid, 'start': new_start, 'size': size}
                    
                    if remaining_size == 0:
                        memory[candidate_idx] = alloc_seg
                    else:
                        memory[candidate_idx] = alloc_seg
                        free_seg = {'id': 'Free', 'start': new_start + size, 'size': remaining_size}
                        memory.insert(candidate_idx + 1, free_seg)
                    success = True
                    
            except ValueError:
                current_op = f"Invalid Req: {req}"

        # Calculate External Fragmentation
        ext_frag = sum(s['size'] for s in memory if s['id'] == 'Free')
        
        steps.append({
            "step": len(steps) + 1,
            "operation": current_op,
            "success": success,
            "memory_state": deepcopy(memory),
            "external_fragmentation": ext_frag
        })

    return {"steps": steps}
