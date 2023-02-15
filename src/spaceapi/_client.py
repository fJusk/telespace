import attrs

from PIL import Image

from io import BytesIO
from datetime import datetime
from typing import List, Literal

from ._base import BaseClient
from .schemas import APODRequest, APODResponse, Request


@attrs.define
class APIClient(BaseClient):

    _api_key: str = attrs.field(default='DEMO_KEY', kw_only=True, alias='api_key')

    async def apod(self, **kwargs) -> APODResponse | List[APODResponse]:
        """
        Request to NASA API endpoint.
        endpoint: /planetary/apod
        
        kwargs: request params (see more in .spaceapi/schemas.py)
        """
        endpoint = '/planetary/apod'
        kwargs['api_key'] = self._api_key
        request = APODRequest(**kwargs)
        print(request.date)
        response = await self.get(endpoint, json_resp=True, params=request.dict())
        if isinstance(response, list):
            return [APODResponse(**resp) for resp in response]
        return APODResponse(**response)

    async def get_image(self, url: str, **kwargs) -> BytesIO:
        """ Get image by absolute url. """
        method = 'GET'
        kwargs['params'] = {'api_key': self._api_key}
        req = Request(method=method, url=url, kwargs=kwargs)
        response = await self.request(req)
        return BytesIO(await response.read())


@attrs.define
class SpaceAPI(APIClient):

    def _filter(
        self,
        mode: Literal['include', 'exclude'], 
        query: List[APODResponse], 
        **filters
    ) -> List[APODResponse]:
        """ Exclude or include models by filters. """
        keys = ['date'] # Not full implementation
        mode = mode.upper() 
        for key in keys:
            params = filters.get(key)
            if params is None:
                continue
            if mode == 'INCLUDE':
                query = [model for model in query if getattr(model, key) in params]
            elif mode == 'EXCLUDE':
                query = [model for model in query if getattr(model, key) not in params]
            else:
                raise ValueError(f'Unknown mode: {mode}')
        return query

    async def image_by_date(self, date: datetime) -> APODResponse:
        """ Get picture of the day by date. """
        resp_data = await self.apod(date=date)
        img_url = resp_data.url
        resp_data.img = await self.get_image(img_url)
        return resp_data

    async def image_now(self) -> APODResponse:
        """ Get current picture of the day. """
        date = datetime.now()
        return await self.image_by_date(date)

    async def random(self, length: int, exclude: List[datetime] = None) -> List[APODResponse]:
        """ Get random pictures of the day. """
        resp_data = await self.apod(count=length)
        if exclude:
            resp_data = self._filter('exclude', resp_data, exclude)
        for resp in resp_data:
            resp.img = await self.get_image(resp.url)
        return resp_data
