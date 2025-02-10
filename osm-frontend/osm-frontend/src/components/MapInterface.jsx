// src/components/MapInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { FeatureGroup } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import axios from 'axios';

const MapInterface = () => {
  const [routeData, setRouteData] = useState(null);
  const [perimeters, setPerimeters] = useState([]);
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);
  const mapRef = useRef();
  const featureGroupRef = useRef();

  // Fetch existing perimeters
  useEffect(() => {
    axios.get('http://localhost:8000/api/perimeters/')
      .then(response => setPerimeters(response.data.features))
      .catch(error => console.error('Error fetching perimeters:', error));
  }, []);

  // Handle perimeter creation
  const handleCreated = (e) => {
    const layer = e.layer;
    const coordinates = layer.getLatLngs()[0].map(point => [point.lng, point.lat]);

    axios.post('http://localhost:8000/api/perimeters/', {
      name: `Perimeter ${Date.now()}`,
      geometry: {
        type: "Polygon",
        coordinates: [coordinates]
      }
    }).then(response => {
      setPerimeters([...perimeters, response.data]);
    });
  };

  // Handle route calculation
  const calculateRoute = async () => {
    if (!startPoint || !endPoint) return;

    try {
      const response = await axios.post('http://localhost:8000/api/routes/', {
        start_point: { type: "Point", coordinates: startPoint },
        end_point: { type: "Point", coordinates: endPoint }
      });

      setRouteData(response.data.data.routes[0]);
    } catch (error) {
      console.error('Routing error:', error);
    }
  };

  return (
    <div className="map-interface">
      <div className="controls">
        <button onClick={() => setStartPoint(prompt('Enter start (lng,lat):').split(',').map(Number))}>
          Set Start
        </button>
        <button onClick={() => setEndPoint(prompt('Enter end (lng,lat):').split(',').map(Number))}>
          Set End
        </button>
        <button onClick={calculateRoute}>Calculate Route</button>
      </div>

      <MapContainer
        center={[51.505, -0.09]}
        zoom={13}
        style={{ height: '600px', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FeatureGroup ref={featureGroupRef}>
          <EditControl
            position="topright"
            onCreated={handleCreated}
            draw={{
              polygon: {
                allowIntersection: false,
                showArea: true,
                metric: true,
                shapeOptions: {
                  color: '#ff0000'
                }
              },
              polyline: false,
              circle: false,
              rectangle: false,
              marker: false
            }}
          />
        </FeatureGroup>

        {routeData && (
          <GeoJSON
            data={routeData.geometry}
            style={{ color: '#3388ff', weight: 5 }}
          />
        )}

        {perimeters.map((perimeter, index) => (
          <GeoJSON
            key={index}
            data={perimeter.geometry}
            style={{ color: '#ff7800', weight: 2 }}
          />
        ))}
      </MapContainer>

      {routeData && (
        <div className="route-info">
          <h3>Route Details</h3>
          <p>Distance: {(routeData.distance / 1000).toFixed(2)} km</p>
          <p>Duration: {Math.round(routeData.duration / 60)} minutes</p>
        </div>
      )}
    </div>
  );
};

export default MapInterface;
