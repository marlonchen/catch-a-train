def test_find_nearest_station(api_client, api_base_url, headers):
    # Philadelphia
    params = {
        'lat': 39.9526,
        'lon': -75.1652
    }
    
    response = api_client.get(
        f'{api_base_url}/nearest_station',
        params=params,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['type'] == 'FeatureCollection'
    assert len(data['features']) > 0


def test_invalid_location(api_client, api_base_url, headers):
    # Coordinates in middle of ocean
    params = {
        'lat': 0.0,
        'lon': 0.0
    }
    
    response = api_client.get(
        f'{api_base_url}/nearest_station',
        params=params,
        headers=headers
    )
    
    assert response.status_code == 400
    assert 'outside service area' in response.json()['detail']


def test_unauthorized_access(api_client, api_base_url):
    params = {
        'lat': 35.681236,
        'lon': 139.767125
    }
    
    response = api_client.get(
        f'{api_base_url}/nearest_station',
        params=params
    )
    
    assert response.status_code == 403
