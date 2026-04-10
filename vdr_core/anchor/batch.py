import asyncio
import time
from typing import List, Dict, Any, Optional

async def anchor_batch(client: Any, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anchors multiple documents in a single batch request efficiently.
    
    Args:
        client: The SipHeron client instance.
        options: Batch configuration:
            - documents: List of document dicts.
            - concurrency: Max parallel requests (default 5).
            - continueOnError: Whether to continue if one anchor fails (default True).
            - delayBetweenBatchesMs: Wait time between chunks (default 100).
            
    Returns:
        Summary of batch performance and individual results.
    """
    documents = options.get('documents', [])
    concurrency = options.get('concurrency', 5)
    continue_on_error = options.get('continueOnError', True)
    delay_ms = options.get('delayBetweenBatchesMs', 100)
    
    results = []
    succeeded = 0
    failed = 0
    start_time = int(time.time() * 1000)
    
    async def process_doc(index: int, doc: Dict[str, Any]) -> Dict[str, Any]:
        try:
            res = await client.anchor({
                **doc,
                'hashAlgorithm': doc.get('hashAlgorithm') or options.get('hashAlgorithm')
            })
            return {'index': index, 'success': True, 'anchor': res}
        except Exception as e:
            if not continue_on_error:
                raise e
            return {'index': index, 'success': False, 'error': str(e)}

    for i in range(0, len(documents), concurrency):
        chunk = documents[i:i+concurrency]
        tasks = [process_doc(i + j, doc) for j, doc in enumerate(chunk)]
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for c_idx, res in enumerate(chunk_results):
            if isinstance(res, Exception):
                if not continue_on_error: raise res
                item = {'index': i + c_idx, 'success': False, 'error': str(res)}
            else:
                item = res
            results.append(item)
            if item.get('success'): succeeded += 1
            else: failed += 1
            
            if options.get('onProgress'): 
                options['onProgress'](len(results), len(documents), item)
        
        # Respect rate limits between chunks
        if i + concurrency < len(documents) and delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)
                
    return {
        'total': len(documents),
        'succeeded': succeeded,
        'failed': failed,
        'results': sorted(results, key=lambda x: x['index']),
        'durationMs': int(time.time() * 1000) - start_time
    }
