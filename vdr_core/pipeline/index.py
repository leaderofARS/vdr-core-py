from typing import List, Dict, Any, Optional

class PipelineModule:
    """
    AI Compliance Pipeline Module.
    
    Provides methods for anchoring AI pipeline events (retrieval, generation, etc.)
    and managing pipeline configurations.
    """
    def __init__(self, client):
        self.client = client

    async def anchor_event(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anchor a single AI pipeline event.
        """
        response = await self.client._request('POST', '/api/pipeline/events', options)
        return response.get('event', {})

    async def anchor_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Anchor multiple AI pipeline events at once (batch).
        """
        return await self.client._request('POST', '/api/pipeline/events/batch', {'events': events})

    async def list_events(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List pipeline events for the current organization.
        """
        return await self.client._request('GET', '/api/pipeline/events', params or {})

    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get detail for a specific pipeline event.
        """
        response = await self.client._request('GET', f'/api/pipeline/events/{event_id}')
        return response.get('event', {})

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get all events in a specific AI session.
        """
        return await self.client._request('GET', f'/api/pipeline/sessions/{session_id}')

    async def list_configs(self) -> List[Dict[str, Any]]:
        """
        List available pipeline configurations.
        """
        response = await self.client._request('GET', '/api/pipeline/configs')
        return response.get('configs', [])

    async def create_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new pipeline configuration.
        """
        response = await self.client._request('POST', '/api/pipeline/configs', data)
        return response.get('config', {})

    async def delete_config(self, config_id: str) -> None:
        """
        Delete a pipeline configuration.
        """
        await self.client._request('DELETE', f'/api/pipeline/configs/{config_id}')
